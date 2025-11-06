from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING

# from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.deposit.models.deposit import Deposit
from services.order.models import Order, OrderItem
from services.order.models.invoice import Invoice
from services.order.models.order_extra_cost import OrderExtraCost
from services.order.rest.order.serializers import (
    InvoiceSummarySerializer,
    OrderExtraCostSerializer,
    OrderItemInputSerializer,
    OrderItemListSerializer,
    OrderKonveksiListSerializer,
)
from services.order.rest.order.utils import get_dynamic_item_price, get_qty_value


if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("OrderItemInputSerializer", "OrderCreateSerializer")


# --- 1. New Helper Function ---
def _format_decimal_as_int_or_float(value):
    """Converts a float/Decimal to int if it has no decimal part."""
    if value is None:
        return None
    try:
        float_val = float(value)
        if float_val == int(float_val):
            return int(float_val)
        return float_val
    except (ValueError, TypeError):
        return value  # Return original value if conversion fails


# --- 2. New Mixin for to_representation logic ---
class FloatToIntRepresentationMixin:
    """
    Mixin to convert specified float/decimal fields to int in representation
    if they are whole numbers.

    Serializers using this mixin should define:
    float_to_int_fields = ["field1", "field2"]
    """

    float_to_int_fields = []

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for field_name in self.float_to_int_fields:
            if field_name in data:
                value = data.get(field_name)
                data[field_name] = _format_decimal_as_int_or_float(value)
        return data


# --- 3. New Mixin for nulling invoice ---
class NullInvoiceIfEmptyItemsMixin:
    """
    Mixin to set 'invoice' to None in representation if 'items' is empty.
    """

    def to_representation(self, instance):
        data = super().to_representation(instance)
        items = data.get("items") or []
        if not items:
            data["invoice"] = None
        return data


# --- Refactored Serializers ---


class DepositCreateSerializer(BaseModelSerializer):
    order = serializers.SlugRelatedField(
        slug_field="subid", queryset=Order.objects.all()
    )
    priority_status = serializers.ChoiceField(
        choices=[("reguler", "Reguler"), ("urgent", "Urgent")], default="reguler"
    )
    items = OrderItemInputSerializer(many=True)
    note = serializers.CharField(required=False, allow_blank=True)
    extra_costs = OrderExtraCostSerializer(many=True, required=False)

    class Meta:
        model = Deposit
        fields = (
            "order",
            "priority_status",
            "items",
            "lead_time",
            "note",
            "extra_costs",
            "deposit_amount",
        )

    # --- 4. New Helper methods for create/update ---

    def _create_order_items(self, order, deposit, items_data):
        """Helper to create order items."""
        for item_data in items_data:
            product = item_data["product"]
            fabric_type = item_data["fabric_type"]
            variant_type = item_data.get("variant_type")
            qty = item_data["quantity"]

            final_price, _ = get_dynamic_item_price(
                product, fabric_type, variant_type, qty
            )

            OrderItem.objects.create(
                order=order,
                deposit=deposit,
                product=product,
                fabric_type=fabric_type,
                variant_type=variant_type,
                quantity=qty,
                price=final_price,
            )

    def _create_extra_costs(self, order, deposit, extra_costs_data):
        """Helper to create extra costs."""
        for extra_data in extra_costs_data:
            OrderExtraCost.objects.create(order=order, deposit=deposit, **extra_data)

    def _update_order_items(self, instance, items_data):
        """Helper to update order items (delete and recreate)."""
        if items_data is not None:
            instance.items.all().delete()
            self._create_order_items(instance, items_data)

    def _update_extra_costs(self, instance, extra_costs_data):
        """Helper to update extra costs (delete and recreate)."""
        if extra_costs_data is not None:
            instance.extra_costs.all().delete()
            self._create_extra_costs(instance, extra_costs_data)

    # --- End Helper methods ---

    def create(self, validated_data):
        from django.utils import timezone
        from django.db import transaction

        note = validated_data.pop("note", "")
        delivery_date = validated_data.pop("delivery_date", timezone.now().date())
        extra_costs_data = validated_data.pop("extra_costs", [])

        with transaction.atomic():
            # Normal konveksi order
            order = validated_data.pop("order")
            items_data = validated_data.pop("items", [])

            deposit = Deposit.objects.create(
                order=order,
                created_by=self.context["request"].user,
                **validated_data,
            )

            # --- Refactored: Use helper methods ---
            self._create_order_items(order, deposit, items_data)
            self._create_extra_costs(order, deposit, extra_costs_data)
            # --- End Refactored ---

            # Generate invoice
            today = timezone.now().date()
            invoice_no = f"SI.{today.year}.{today.month:02d}.{deposit.pk:05d}"
            Invoice.objects.create(
                status="partial",
                invoice_no=invoice_no,
                order=order,
                deposit=deposit,
                issued_date=today,
                delivery_date=delivery_date,
                note=note,
            )

        return deposit

    def update(self, instance, validated_data):
        """
        Handle updating existing order (including optional items/extra_costs).
        """
        from django.db import transaction

        is_deposit = validated_data.pop(
            "is_deposit", getattr(instance, "is_deposit", False)
        )
        note = validated_data.pop("note", "")
        delivery_date = validated_data.pop("delivery_date", None)
        items_data = validated_data.pop("items", None)
        extra_costs_data = validated_data.pop("extra_costs", None)

        with transaction.atomic():
            # Update main order fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            # --- Refactored: Use helper methods ---
            # Update order items if provided
            self._update_order_items(instance, items_data)
            # Update extra costs if provided
            self._update_extra_costs(instance, extra_costs_data)
            # --- End Refactored ---

            # Update invoice if exists
            invoice = getattr(instance, "invoice", None)
            if invoice:
                if delivery_date:
                    invoice.delivery_date = delivery_date
                if note:
                    invoice.note = note
                invoice.save()

        return instance


class DepositItemListSerializer(
    FloatToIntRepresentationMixin, serializers.ModelSerializer
):
    product_name = serializers.SerializerMethodField()
    fabric_type = serializers.CharField(source="fabric_type.name")
    unit = serializers.SerializerMethodField()
    # subtotal = serializers.SerializerMethodField()

    # Define fields for the mixin
    float_to_int_fields = ["price"]

    class Meta:
        model = OrderItem
        fields = [
            "product_name",
            "fabric_type",
            "unit",
            "price",
            "quantity",
            "subtotal",
        ]

    # to_representation is now handled by FloatToIntRepresentationMixin

    def get_product_name(self, instance):
        product = getattr(instance, "product", None)
        product_display_name = (
            getattr(product, "name", str(product)) if product else None
        )

        variant_type = getattr(instance, "variant_type", None)
        variant_code = getattr(variant_type, "code", None) if variant_type else None

        if variant_type and variant_code and product_display_name:
            return f"{variant_code}. {product_display_name}"
        return product_display_name

    def get_unit(self, instance):
        variant_type = getattr(instance, "variant_type", None)
        return variant_type.unit.upper() if variant_type and variant_type.unit else None


class DepositListSerializer(FloatToIntRepresentationMixin, BaseModelSerializer):
    order = OrderKonveksiListSerializer(read_only=True)
    invoice = InvoiceSummarySerializer(read_only=True)
    items = OrderItemListSerializer(many=True, read_only=True)
    extra_costs = OrderExtraCostSerializer(many=True, read_only=True)
    detail_order = serializers.SerializerMethodField()
    qty = serializers.SerializerMethodField()

    # Define fields for the mixin
    float_to_int_fields = ["deposit_amount"]

    class Meta:
        model = Deposit
        fields = [
            "pk",
            "order",
            "priority_status",
            "created",
            "items",
            "invoice",
            "extra_costs",
            "detail_order",
            "qty",
            # CS2
            "lead_time",
            "reminder_one",
            "reminder_two",
            "is_expired",
            "is_paid_off",
            "note",
            "shipping_courier",
            "deposit_amount",
        ]

    # to_representation is now handled by FloatToIntRepresentationMixin
    def get_detail_order(self, obj):
        """
        Returns combined quantity string for an order.
        Example outputs:
            "3 ATASAN + 2 STEL"
            "3 + 2 ATASAN"  (if some variant_type are null)
        """
        items = OrderItem.objects.filter(order=obj.order)
        if not items.exists():
            return None  # return None instead of ""

        parts = []
        last_unit = None
        has_null_unit = False

        for item in items:
            qty = item.quantity or 0
            unit = None

            # Safely get variant_type.unit if exists
            variant_type = getattr(item, "variant_type", None)
            if variant_type and getattr(variant_type, "unit", None):
                unit = str(variant_type.unit).upper().strip()
                last_unit = unit
            else:
                has_null_unit = True

            # Build string part
            if unit:
                parts.append(f"{qty} {unit}")
            else:
                parts.append(str(qty))

        result = " + ".join(parts)
        return result or None

    def get_qty(self, obj):
        """
        Returns the total sum of all computed quantities in the order.

        Example:
            If items are:
                - 3 ATASAN (1x multiplier)
                - 2 STEL (2x multiplier)
            Result = (3×1) + (2×2) = 7
        """
        items = OrderItem.objects.filter(order=obj.order)
        if not items.exists():
            return 0

        total_qty = 0

        for item in items:
            qty = item.quantity or 0

            total_qty += get_qty_value(item.variant_type.weight, qty)

        return total_qty


class DepositDetailSerializer(
    FloatToIntRepresentationMixin, NullInvoiceIfEmptyItemsMixin, BaseModelSerializer
):
    # customer = CustomerSerializer(read_only=True)
    invoice = InvoiceSummarySerializer(read_only=True)
    items = OrderItemListSerializer(many=True, read_only=True)
    extra_costs = OrderExtraCostSerializer(many=True, read_only=True)

    # Define fields for the FloatToInt mixin
    float_to_int_fields = ["deposit_amount"]

    class Meta:
        model = Deposit
        fields = [
            "pk",
            # "order",
            # "order_type",
            # "convection_name",
            # "customer",
            "priority_status",
            # "status",
            "created",
            "items",
            "invoice",
            "extra_costs",
            # CS 2
            "reminder_one",
            "reminder_two",
            "is_expired",
            "is_paid_off",
            "note",
            "shipping_courier",
            "deposit_amount",
        ]

    # to_representation is now handled by both mixins
    # 1. FloatToIntRepresentationMixin handles deposit_amount
    # 2. NullInvoiceIfEmptyItemsMixin handles setting invoice=None
