from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.warehouse.models import StockOpname
from services.warehouse.models.material import Material
from services.warehouse.rest.material.serializers import MaterialSerializerSimple

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("StockOpnameSerializer",)


class StockOpnameSerializer(BaseModelSerializer):
    """
    Serializer for Stock Opname (Adjustments).
    """

    material = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Material.objects.all(),
        required=True,
    )
    difference = serializers.SerializerMethodField()

    class Meta:
        model = StockOpname
        fields = [
            "pk",
            "material",
            "date_so",
            "qty_system",
            "qty_actual",
            "difference",
            "notes",
            "created_by",
        ]
        read_only_fields = ["qty_system", "created_by"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["material"] = MaterialSerializerSimple(instance.material).data
        data["created_by"] = UserSerializerSimple(instance.created_by).data
        return data

    def get_difference(self, obj: StockOpname) -> int:
        return obj.difference
