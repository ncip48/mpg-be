from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.customer.rest.customer.serializers import CustomerSerializerSimple
from services.order.models.order_form import OrderForm
from services.order.models.order_item import OrderItem
from services.order.rest.order.serializers import OrderItemListSerializer
from services.order.rest.order.utils import get_qty_value
from services.printer.rest.printer.serializers import PrinterSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("OrderFormSerializer",)


class OrderFormSerializer(BaseModelSerializer):
    """
    Serializer for order form
    """

    # Write-only FK, using subid as input
    order_item = serializers.SlugRelatedField(
        slug_field="subid", queryset=OrderItem.objects.all(), write_only=True
    )

    # Read-only nested output of order_item
    order_item_display = OrderItemListSerializer(source="order_item", read_only=True)
    total_qty = serializers.SerializerMethodField()
    printer = PrinterSerializer(source="order_item.product.printer", read_only=True)
    customer = CustomerSerializerSimple(
        source="order_item.order.customer", read_only=True
    )

    class Meta:
        model = OrderForm
        fields = [
            "pk",
            "form_type",
            "printer",
            "customer",
            "order_item",
            "order_item_display",
            "team_name",
            "design_front",
            "design_back",
            "jersey_pattern",
            "jersey_type",
            "jersey_cutting",
            "collar_type",
            "pants_cutting",
            "promo_logo_ez",
            "tag_size_bottom",
            "tag_size_shoulder",
            "logo_chest_right",
            "logo_center",
            "logo_chest_left",
            "logo_back",
            "logo_pants",
            "total_qty",
        ]
        read_only_fields = ["pk"]

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)

    def get_total_qty(self, obj):
        """
        Returns the total sum of all computed quantities in the order.

        Example:
            If items are:
                - 3 ATASAN (1x multiplier)
                - 2 STEL (2x multiplier)
            Result = (3×1) + (2×2) = 7
        """
        items = OrderItem.objects.filter(order_forms=obj)
        if not items.exists():
            return 0

        total_qty = 0

        for item in items:
            qty = item.quantity or 0

            total_qty += get_qty_value(item.variant_type.weight, qty)

        return total_qty
