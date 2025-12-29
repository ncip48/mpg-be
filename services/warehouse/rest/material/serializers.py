from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.warehouse.models import (
    Material,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("MaterialSerializer", "MaterialSerializerSimple")


class MaterialSerializer(BaseModelSerializer):
    """
    Serializer for Material (Raw Material) master data.
    """

    current_stock = serializers.ReadOnlyField()
    category_display = serializers.CharField(
        source="get_category_display", read_only=True
    )
    unit_display = serializers.CharField(source="get_unit_display", read_only=True)

    class Meta:
        model = Material
        fields = [
            "pk",
            "code",
            "name",
            "category",
            "category_display",
            "description",
            "unit",
            "unit_display",
            "current_stock",
        ]


class MaterialSerializerSimple(BaseModelSerializer):
    """
    Serializer for Material (Raw Material) master data.
    """

    class Meta:
        model = Material
        fields = [
            "pk",
            "name",
        ]
