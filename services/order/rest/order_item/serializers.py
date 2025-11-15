from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.deposit.models.deposit import Deposit
from services.deposit.rest.deposit.serializers import (
    DepositListSerializer,
    FloatToIntRepresentationMixin,
)
from services.order.models.order_form import OrderForm
from services.order.models.order_item import OrderItem
from services.order.rest.order.serializers import (
    OrderItemListSerializer,
    OrderKonveksiListSerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("OrderItemSerializer",)


class _DepositListSerializer(FloatToIntRepresentationMixin, BaseModelSerializer):
    # order = OrderKonveksiListSerializer(read_only=True)
    # qty = serializers.SerializerMethodField()
    # estimate_sent = serializers.SerializerMethodField()

    # Define fields for the mixin
    float_to_int_fields = ["deposit_amount"]

    class Meta:
        model = Deposit
        fields = [
            "pk",
            # "order",
            "priority_status",
            "created",
            # "items",
            "invoice",
            # "extra_costs",
            # "detail_order",
            # "qty",
            # CS2
            "lead_time",
            "reminder_one",
            "reminder_two",
            "is_expired",
            "is_paid_off",
            "note",
            "shipping_courier",
            "deposit_amount",
            "accepted_at",
            # "estimate_sent",
        ]

    # def get_estimate_sent(self, obj):
    #     accepted_at = getattr(obj, "accepted_at", None)
    #     lead_time = getattr(obj, "lead_time", 0)

    #     if not accepted_at or not lead_time:
    #         return None

    #     # Use Indonesian public holidays
    #     id_holidays = holidays.country_holidays("ID", years=accepted_at.year)

    #     current_date = accepted_at
    #     days_added = 0

    #     while days_added < lead_time:
    #         current_date += datetime.timedelta(days=1)

    #         # Skip weekends (Saturday=5, Sunday=6)
    #         if current_date.weekday() >= 5:
    #             continue

    #         # Skip Indonesian holidays
    #         if current_date in id_holidays:
    #             continue

    #         days_added += 1

    #     return current_date.strftime("%Y-%m-%d")

    # # to_representation is now handled by FloatToIntRepresentationMixin
    # def get_detail_order(self, obj):
    #     """
    #     Returns combined quantity string for an order.
    #     Example outputs:
    #         "3 ATASAN + 2 STEL"
    #         "3 + 2 ATASAN"  (if some variant_type are null)
    #     """
    #     items = OrderItem.objects.filter(order=obj.order)
    #     if not items.exists():
    #         return None  # return None instead of ""

    #     parts = []
    #     last_unit = None
    #     has_null_unit = False

    #     for item in items:
    #         qty = item.quantity or 0
    #         unit = None

    #         # Safely get variant_type.unit if exists
    #         variant_type = getattr(item, "variant_type", None)
    #         if variant_type and getattr(variant_type, "unit", None):
    #             unit = str(variant_type.unit).upper().strip()
    #             last_unit = unit
    #         else:
    #             has_null_unit = True

    #         # Build string part
    #         if unit:
    #             parts.append(f"{qty} {unit}")
    #         else:
    #             parts.append(str(qty))

    #     result = " + ".join(parts)
    #     return result or None

    # def get_qty(self, obj):
    #     """
    #     Returns the total sum of all computed quantities in the order.

    #     Example:
    #         If items are:
    #             - 3 ATASAN (1x multiplier)
    #             - 2 STEL (2x multiplier)
    #         Result = (3×1) + (2×2) = 7
    #     """
    #     items = OrderItem.objects.filter(order=obj.order)
    #     if not items.exists():
    #         return 0

    #     total_qty = 0

    #     for item in items:
    #         qty = item.quantity or 0

    #         total_qty += get_qty_value(item.variant_type.weight, qty)

    #     return total_qty


class OrderItemSerializer(OrderItemListSerializer):
    """
    Serializer for order form
    """

    has_order_form = serializers.SerializerMethodField()
    order = OrderKonveksiListSerializer(read_only=True)
    deposit = _DepositListSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = (
            [
                "pk",
                "order",
                "deposit",
            ]
            + OrderItemListSerializer.Meta.fields
            + [
                "has_order_form",
            ]
        )

    def get_has_order_form(self, obj: OrderItem) -> bool:
        return obj.order_forms.exists()
