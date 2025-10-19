from __future__ import annotations
from django.db import transaction
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.product.models.fabric_price import FabricPrice
from services.product.models.fabric_type import FabricType
from services.product.models.variant_type import ProductVariantType
from services.product.rest.variant_type.serializers import ProductVariantTypeSerializerSimple

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "FabricTypeSerializer",
)


class FabricVariantPriceSerializer(BaseModelSerializer):
    """
    Handles relation between FabricType and ProductVariantType with price.
    Used for nested input/output in FabricTypeCreateSerializer.
    """
    pk = serializers.SlugRelatedField(
        slug_field="subid",
        source="variant_type",
        queryset=ProductVariantType.objects.all(),
        write_only=True,
    )
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    variant_type = ProductVariantTypeSerializerSimple(read_only=True)

    class Meta:
        model = FabricPrice
        fields = ["pk", "variant_type", "price"]
        
    def to_representation(self, instance):
        data = super().to_representation(instance)
        # price must return int if int (e.g. '100.00' => 100, '99.99' => 99.99)
        price = data.get("price")
        if price is not None:
            try:
                price_float = float(price)
                if price_float.is_integer():
                    data["price"] = int(price_float)
                else:
                    data["price"] = float(price)
            except (ValueError, TypeError):
                # Keep original if conversion fails
                pass
        return data

class FabricTypeSerializer(BaseModelSerializer):
    """
    Serializer for Fabric Type management by superusers.
    Handles CRUD for fabric types and related configurations.
    """
    fabric_prices = FabricVariantPriceSerializer(many=True, read_only=True)

    class Meta:
        model = FabricType
        fields = [
            "pk",
            "name",
            "fabric_prices",
            "created",
            "updated",
        ]
        
class FabricTypeSerializerSimple(BaseModelSerializer):
    """
    Serializer for Fabric Type management by superusers.
    Handles CRUD for fabric types and related configurations.
    """

    class Meta:
        model = FabricType
        fields = [
            "pk",
            "name",
        ]

class FabricTypeCreateSerializer(BaseModelSerializer):
    """
    Serializer for Fabric Type management by superusers.
    Handles CRUD for fabric types and related variant-type pricing.
    """
    variant_types = FabricVariantPriceSerializer(many=True, write_only=True)
    fabric_prices = FabricVariantPriceSerializer(many=True, read_only=True)

    class Meta:
        model = FabricType
        fields = [
            "pk",
            "name",
            "variant_types",     # input field
            "fabric_prices",     # output field
            "created",
            "updated",
        ]

    def create(self, validated_data):
        variant_data = validated_data.pop("variant_types", [])
        fabric = FabricType.objects.create(**validated_data)

        # create FabricPrice relations
        for v in variant_data:
            FabricPrice.objects.create(
                fabric_type=fabric,
                variant_type=v["variant_type"],
                price=v["price"]
            )

        return fabric

    @transaction.atomic
    def update(self, instance, validated_data):
        variant_data = validated_data.pop("variant_types", None)
        instance.name = validated_data.get("name", instance.name)
        instance.save()

        if variant_data is not None:
            # 1️⃣ Collect current and new variant_type IDs
            new_variant_ids = [v["variant_type"].id for v in variant_data]
            existing_variant_ids = list(
                instance.fabric_prices.values_list("variant_type_id", flat=True)
            )

            # 2️⃣ Delete removed variant_type relations
            to_delete = set(existing_variant_ids) - set(new_variant_ids)
            if to_delete:
                FabricPrice.objects.filter(
                    fabric_type=instance, variant_type_id__in=to_delete
                ).delete()

            # 3️⃣ Create or update existing ones
            for v in variant_data:
                FabricPrice.objects.update_or_create(
                    fabric_type=instance,
                    variant_type=v["variant_type"],
                    defaults={"price": v["price"]},
                )

        return instance