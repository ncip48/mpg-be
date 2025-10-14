from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.printer.models.printer import Printer
from services.printer.rest.printer.serializers import PrinterSerializer
from services.product.models.fabric_price import FabricPrice
from services.product.models.fabric_type import FabricType
from services.product.models.price_adjustment import ProductPriceAdjustment
from services.product.models.price_tier import ProductPriceTier
from services.product.models.product import Product
from services.product.models.variant_type import ProductVariantType
from services.store.models.store import Store
from services.store.rest.store.serializers import StoreSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_serializer_method

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ProductSerializer",
    "ProductPriceAdjustmentNestedSerializer",
    "ProductPriceTierNestedSerializer",
    "ProductSerializerSimple",
)

# --- Nested serializers ----------------------------------------------------

class FabricPriceSerializer(serializers.ModelSerializer):
    fabric_type = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=FabricType.objects.all()
    )
    fabric_name = serializers.CharField(source="fabric_type.name", read_only=True)

    class Meta:
        model = FabricPrice
        fields = ["fabric_type", "fabric_name", "price"]


class ProductPriceTierNestedSerializer(serializers.ModelSerializer):
    variant_type = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=ProductVariantType.objects.all(),
        required=False,
        allow_null=True,
    )
    variant_name = serializers.CharField(
        source="variant_type.name", read_only=True, default=None
    )

    # ✅ instead of nested fabric_adjustments, now show master fabric prices
    fabric_prices = serializers.SerializerMethodField()

    class Meta:
        model = ProductPriceTier
        fields = [
            "variant_type",
            "variant_name",
            "min_qty",
            "max_qty",
            "base_price",
            "fabric_prices",
        ]
        ref_name = "NestedProductPriceTier"

    def get_fabric_prices(self, obj):
        """Return all fabric prices for this variant type (from master FabricPrice table)."""
        variant = obj.variant_type
        if not variant:
            return [{
                "fabric_type": None,
                "fabric_name": "Standard",
                "price": "0.00"
            }]
        prices = FabricPrice.objects.filter(variant_type=variant).order_by("price")
        return FabricPriceSerializer(prices, many=True).data

    def create(self, validated_data):
        return ProductPriceTier.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
    
# --- Product Serializer ----------------------------------------------------

class ProductSerializer(BaseModelSerializer):
    store = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Store.objects.all(),
        write_only=True
    )
    printer = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Printer.objects.all(),
        write_only=True
    )

    printer_display = PrinterSerializer(source="printer", read_only=True)
    store_display = StoreSerializer(source="store", read_only=True)

    price_tiers = ProductPriceTierNestedSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "pk",
            "name",
            "image",
            "printer",
            "printer_display",
            "store",
            "store_display",
            "sku",
            "price_tiers",
        ]

    def create(self, validated_data):
        tiers_data = validated_data.pop("price_tiers", [])
        product = Product.objects.create(**validated_data)
        for tier_data in tiers_data:
            ProductPriceTier.objects.create(product=product, **tier_data)
        return product

    def update(self, instance, validated_data):
        tiers_data = validated_data.pop("price_tiers", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if tiers_data is not None:
            instance.price_tiers.all().delete()
            for tier_data in tiers_data:
                ProductPriceTier.objects.create(product=instance, **tier_data)
        return instance

    def to_representation(self, instance):
        """Group price tiers by variant_type and include fabric prices."""
        data = super().to_representation(instance)
        tiers = data.pop("price_tiers", [])

        grouped = {}
        for t in tiers:
            variant_type = t.get("variant_type")
            variant_name = t.get("variant_name")

            key = variant_type or "base"
            if key not in grouped:
                grouped[key] = {
                    "variant_type": {
                        "pk": variant_type,
                        "name": variant_name or None,
                    },
                    "tiers": [],
                }

            grouped[key]["tiers"].append({
                "min_qty": t["min_qty"],
                "max_qty": t["max_qty"],
                "base_price": t["base_price"],
                "fabric_prices": t["fabric_prices"],
            })

        data["price_tiers"] = list(grouped.values())
        return data
        
class ProductSerializerSimple(BaseModelSerializer):
    """
    Simple serializer for Product, exposing only primary key and name.
    """
    class Meta:
        model = Product
        fields = ['pk', 'name']