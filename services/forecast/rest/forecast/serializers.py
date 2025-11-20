from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.forecast.models.forecast import Forecast
from services.order.models.order import Order
from services.order.models.order_item import OrderItem

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("ForecastSerializer",)


class ForecastSerializer(BaseModelSerializer):
    """
    Serializer for Forecast management.
    Handles CRUD for Forecast entries.
    """

    # Optional: show subid for FK relations
    order = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Order.objects.all(),
        required=False,
        allow_null=True,
    )

    order_item = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=OrderItem.objects.all(),
        required=False,
        allow_null=True,
    )

    created_by = serializers.SlugRelatedField(slug_field="subid", read_only=True)

    class Meta:
        model = Forecast
        fields = [
            "pk",
            "subid",
            "order",
            "order_item",
            "date_forecast",
            "print_status",
            "created_by",
            "created",
            "updated",
        ]
        read_only_fields = ("created", "updated", "created_by")
