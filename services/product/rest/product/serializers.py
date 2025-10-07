from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.printer.models.printer import Printer
from services.printer.rest.printer.serializers import PrinterSerializer
from services.product.models.product import Product
from services.store.models.store import Store
from services.store.rest.store.serializers import StoreSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ProductSerializer",
)
        
class ProductSerializer(BaseModelSerializer):
    """
    Serializer for Product management by superusers.
    Handles CRUD for Product and assignment of permissions.
    """
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

    class Meta:
        model = Product
        fields = ['pk', 'name', 'image', 'printer', 'printer_display', 'store', 'store_display', 'sku']
        extra_kwargs = {
            'printer': {'write_only': True},
            'store': {'write_only': True},
        }
        
class ProductSerializerSimple(BaseModelSerializer):
    """
    Simple serializer for Product, exposing only primary key and name.
    """
    class Meta:
        model = Product
        fields = ['pk', 'name']