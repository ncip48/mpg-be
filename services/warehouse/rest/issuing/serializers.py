from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.warehouse.models import Issuing
from services.warehouse.models.material import Material

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("IssuingSerializer",)


class IssuingSerializer(BaseModelSerializer):
    """
    Serializer for Warehouse Issuing (Pengeluaran).
    Includes validation to prevent negative stock.
    """

    material = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Material.objects.all(),
        required=True,
    )

    class Meta:
        model = Issuing
        fields = [
            "pk",
            "material",
            "forecast_date",
            "qty_out",
            "date_out",
            "issued_by",
        ]
        read_only_fields = ["issued_by"]

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        material = data["material"]
        qty_out = data["qty_out"]

        if material.current_stock < qty_out:
            raise serializers.ValidationError(
                _("Insufficient stock! Current: %(stock)s, Requested: %(qty)s")
                % {"stock": material.current_stock, "qty": qty_out}
            )
        return data
