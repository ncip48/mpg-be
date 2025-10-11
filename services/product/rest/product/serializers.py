from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.printer.models.printer import Printer
from services.printer.rest.printer.serializers import PrinterSerializer
from services.product.models.fabric_type import FabricType
from services.product.models.price_adjustment import ProductPriceAdjustment
from services.product.models.price_tier import ProductPriceTier
from services.product.models.product import Product
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

class ProductPriceAdjustmentNestedSerializer(serializers.ModelSerializer):
    fabric_type = serializers.PrimaryKeyRelatedField(queryset=FabricType.objects.all())

    class Meta:
        model = ProductPriceAdjustment
        fields = ["fabric_type", "extra_price"]
        ref_name = "NestedProductPriceAdjustment"   # 👈 add this


class ProductPriceTierNestedSerializer(serializers.ModelSerializer):
    fabric_adjustments = ProductPriceAdjustmentNestedSerializer(many=True, required=False)

    class Meta:
        model = ProductPriceTier
        fields = ["variant_type", "min_qty", "max_qty", "base_price", "fabric_adjustments"]
        ref_name = "NestedProductPriceTier"   # 👈 add this

    def create(self, validated_data):
        fabric_data = validated_data.pop("fabric_adjustments", [])
        tier = ProductPriceTier.objects.create(**validated_data)
        for f in fabric_data:
            ProductPriceAdjustment.objects.create(product_price_tier=tier, **f)
        return tier
        
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
    printer_display = PrinterSerializer(source='printer', read_only=True)
    store_display = StoreSerializer(source='store', read_only=True)

    # price_tiers = ProductPriceTierNestedSerializer(many=True, required=False)

    class Meta:
        model = Product
        fields = [
            "pk", "name", "image", "printer", "printer_display",
            "store", "store_display", "sku",
        ]
        
    def create(self, validated_data):
        tiers_data = validated_data.pop("price_tiers", [])
        product = Product.objects.create(**validated_data)
        for tier_data in tiers_data:
            ProductPriceTierNestedSerializer().create({
                **tier_data,
                "product": product
            })
        return product
        
class ProductSerializerSimple(BaseModelSerializer):
    """
    Simple serializer for Product, exposing only primary key and name.
    """
    class Meta:
        model = Product
        fields = ['pk', 'name']