from __future__ import annotations
import json
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.printer.models.printer import Printer
from services.printer.rest.printer.serializers import PrinterSerializer
from services.product.models.fabric_price import FabricPrice
from services.product.models.fabric_type import FabricType
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
        slug_field="subid", queryset=FabricType.objects.all()
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
    variant_code = serializers.CharField(
        source="variant_type.code", read_only=True, default=None
    )

    # ✅ instead of nested fabric_adjustments, now show master fabric prices
    fabric_prices = serializers.SerializerMethodField()

    class Meta:
        model = ProductPriceTier
        fields = [
            "variant_type",
            "variant_name",
            "variant_code",
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
            return [{"fabric_type": None, "fabric_name": "Standard", "price": "0.00"}]
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

import json
from rest_framework import serializers


class ProductSerializer(BaseModelSerializer):
    store = serializers.SlugRelatedField(
        slug_field="subid", queryset=Store.objects.all(), write_only=True
    )
    printer = serializers.SlugRelatedField(
        slug_field="subid", queryset=Printer.objects.all(), write_only=True
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

    def _parse_json_field(self, data, field_name):
        """
        Safely get and parse a JSON-like field that may come from:
         - JSON body (list/dict already)
         - multipart form-data (value is a list of strings, or string)
        Returns Python object or None.
        """
        # prefer explicit lookup in initial_data if available (for form-data)
        value = None
        # `data` might be a QueryDict or dict; handle both
        if isinstance(data, dict) and field_name in data:
            value = data.get(field_name)
        else:
            # fallback: try to read from self.initial_data if present
            value = getattr(self, "initial_data", {}).get(field_name)

        # if value is a list (common with multipart/form-data), unwrap first element
        if isinstance(value, (list, tuple)):
            value = value[0] if value else None

        # if it's already a Python list/dict (when Content-Type: application/json), return as-is
        if isinstance(value, (list, dict)):
            return value

        # if it's a string, attempt JSON parse
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError({field_name: "Invalid JSON format"})

        # otherwise None or unknown -> return None
        return None

    def to_internal_value(self, data):
        """
        Only decode price_tiers when it's passed as a JSON string (form-data).
        Do NOT pre-validate nested serializer here — let DRF handle validation.
        """
        data = data.copy()
        parsed = self._parse_json_field(data, "price_tiers")
        if parsed is not None:
            # assign the parsed structure so DRF will validate it using the declared field
            data["price_tiers"] = parsed
        return super().to_internal_value(data)

    def _get_price_tiers_validated(self, raw_container):
        """
        Given a raw list of price tier dicts, validate them via nested serializer and
        return validated_data (list of dicts) or raise ValidationError.
        """
        if raw_container is None:
            return []
        serializer = ProductPriceTierNestedSerializer(data=raw_container, many=True)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def create(self, validated_data):
        # standard path: nested field present in validated_data
        tiers_data = validated_data.pop("price_tiers", None)

        # fallback: parse from initial_data (works for multipart/form-data)
        if tiers_data is None:
            raw = self._parse_json_field(self.initial_data or {}, "price_tiers")
            if raw is not None:
                tiers_data = self._get_price_tiers_validated(raw)

        if tiers_data is None:
            tiers_data = []

        product = Product.objects.create(**validated_data)

        for tier_data in tiers_data:
            ProductPriceTier.objects.create(product=product, **tier_data)

        return product

    def update(self, instance, validated_data):
        tiers_data = validated_data.pop("price_tiers", None)

        # fallback same as create
        if tiers_data is None:
            raw = self._parse_json_field(self.initial_data or {}, "price_tiers")
            if raw is not None:
                tiers_data = self._get_price_tiers_validated(raw)

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
            variant_code = t.get("variant_code")

            key = variant_type or "base"
            if key not in grouped:
                grouped[key] = {
                    "pk": variant_type,
                    "variant_type": {
                        "pk": variant_type,
                        "name": variant_name,
                        "code": variant_code,
                    },
                    "name": f"{variant_code}. {instance.name}"
                    if variant_type
                    else f"{instance.name}" or None,
                    "tiers": [],
                }

            grouped[key]["tiers"].append(
                {
                    "min_qty": t["min_qty"],
                    "max_qty": t["max_qty"],
                    "base_price": t["base_price"],
                    "fabric_prices": t.get("fabric_prices", []),
                }
            )

        data["price_tiers"] = list(grouped.values())
        return data


class ProductSerializerSimple(BaseModelSerializer):
    """
    Simple serializer for Product, exposing only primary key and name.
    """

    class Meta:
        model = Product
        fields = ["pk", "name"]
