from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.product.models.variant_type import ProductVariantType

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ProductVariantTypeSerializer",
)


class ProductVariantTypeSerializer(BaseModelSerializer):
    """
    Serializer for Product Variant Type management by superusers.
    Handles CRUD for product variant types and related configurations.
    """

    class Meta:
        model = ProductVariantType
        fields = [
            "pk",
            "code",
            "name",
            "note",
            "created",
            "updated",
        ]
        
class ProductVariantTypeSerializerSimple(BaseModelSerializer):
    """
    Serializer for Product Variant Type management by superusers.
    Handles CRUD for product variant types and related configurations.
    """

    class Meta:
        model = ProductVariantType
        fields = [
            "pk",
            "code",
            "name",
        ]
