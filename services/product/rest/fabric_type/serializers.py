from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.product.models.fabric_type import FabricType

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "FabricTypeSerializer",
)


class FabricTypeSerializer(BaseModelSerializer):
    """
    Serializer for Fabric Type management by superusers.
    Handles CRUD for fabric types and related configurations.
    """

    class Meta:
        model = FabricType
        fields = [
            "pk",
            "name",
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
