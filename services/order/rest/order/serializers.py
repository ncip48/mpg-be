from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING

# from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.customer.models.customer import Customer
from services.customer.rest.customer.serializers import CustomerSerializer
from services.order.models import Order, OrderItem
from services.order.models.invoice import Invoice
from services.order.models.order_extra_cost import OrderExtraCost
from services.order.rest.order.utils import get_dynamic_item_price, get_qty_value
from services.product.models import ProductVariantType, Product, FabricType

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("OrderItemInputSerializer", "OrderCreateSerializer")


class OrderExtraCostSerializer(BaseModelSerializer):
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = OrderExtraCost
        fields = [
            "pk",
            "description",
            "quantity",
            "amount",
            "total_amount",
            "type",
        ]

    def to_representation(self, instance):
        result = super().to_representation(instance)
        amount = result.get("amount")
        # If amount is float but integer (e.g. 20.0), return as int
        if amount is not None:
            try:
                if float(amount) == int(float(amount)):
                    result["amount"] = int(float(amount))
                else:
                    result["amount"] = float(amount)
            except (ValueError, TypeError):
                pass
        return result

    def get_total_amount(self, obj):
        if (
            hasattr(obj, "quantity")
            and hasattr(obj, "amount")
            and obj.quantity is not None
            and obj.amount is not None
        ):
            total = obj.quantity * obj.amount
            # Format: no .0 if integer
            if total == int(total):
                return int(total)
            return float(total)
        return None


class OrderItemInputSerializer(BaseModelSerializer):
    product = serializers.SlugRelatedField(
        slug_field="subid", queryset=Product.objects.all()
    )
    fabric_type = serializers.SlugRelatedField(
        slug_field="subid", queryset=FabricType.objects.all()
    )
    variant_type = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=ProductVariantType.objects.all(),
        required=False,
        allow_null=True,
    )
    quantity = serializers.IntegerField(min_value=1)
    # price = serializers.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        model = OrderItem
        fields = (
            "product",
            "fabric_type",
            "variant_type",
            "quantity",
            # "price",
        )


class OrderCreateSerializer(BaseModelSerializer):
    is_deposit = serializers.BooleanField(default=False)
    customer = serializers.SlugRelatedField(
        slug_field="subid", queryset=Customer.objects.all()
    )
    order_type = serializers.ChoiceField(
        choices=[("konveksi", "Konveksi"), ("marketplace", "Marketplace")]
    )
    priority_status = serializers.ChoiceField(
        choices=[("reguler", "Reguler"), ("urgent", "Urgent")], default="reguler"
    )
    items = OrderItemInputSerializer(many=True)
    delivery_date = serializers.DateField(required=False)
    note = serializers.CharField(required=False, allow_blank=True)
    extra_costs = OrderExtraCostSerializer(many=True, required=False)

    class Meta:
        model = Order
        fields = (
            "is_deposit",
            "convection_name",
            "customer",
            "order_type",
            "priority_status",
            "items",
            "delivery_date",
            "note",
            "extra_costs",
            # Marketplace fields
            "user_name",
            "order_number",
            "marketplace",
            "order_choice",
            "estimated_shipping_date",
            "deposit_amount",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data = self.initial_data if hasattr(self, "initial_data") else {}

        is_deposit = data.get("is_deposit", False)
        order_type = data.get("order_type", None)

        # Normalize boolean if sent as string
        if isinstance(is_deposit, str):
            is_deposit = is_deposit.lower() == "true"

        if order_type == "marketplace":
            # 'customer' and 'items' are NOT required
            self.fields["customer"].required = False
            self.fields["items"].required = False
            # The following become required
            extra_required = [
                "user_name",
                "order_number",
                "marketplace",
                "order_choice",
                "estimated_shipping_date",
            ]
            for field_name in extra_required:
                if field_name in self.fields:
                    self.fields[field_name].required = True
        else:
            # 'customer' and 'items' are required, others are not
            self.fields["customer"].required = True
            self.fields["convection_name"].required = True
            if not is_deposit:
                self.fields["items"].required = False
                self.fields["deposit_amount"].required = False
            else:
                self.fields["items"].required = True
                self.fields["deposit_amount"].required = True
            extra_mkt_fields = [
                "user_name",
                "order_number",
                "marketplace",
                "order_choice",
                "estimated_shipping_date",
            ]
            for field_name in extra_mkt_fields:
                if field_name in self.fields:
                    self.fields[field_name].required = False

    def create(self, validated_data):
        from django.utils import timezone
        from django.db import transaction

        is_deposit = validated_data.pop("is_deposit", False)
        order_type = validated_data.get("order_type")
        note = validated_data.pop("note", "")
        delivery_date = validated_data.pop("delivery_date", timezone.now().date())
        extra_costs_data = validated_data.pop("extra_costs", [])

        with transaction.atomic():
            # Handle order creation
            if not is_deposit and order_type == "marketplace":
                # Marketplace order - customer/items not required
                order = Order.objects.create(
                    status="draft",
                    created_by=self.context["request"].user,
                    **validated_data,
                )
            else:
                # Normal konveksi order
                customer = validated_data.pop("customer")
                items_data = validated_data.pop("items", [])

                order = Order.objects.create(
                    status="deposit" if is_deposit else "draft",
                    customer=customer,
                    created_by=self.context["request"].user,
                    **validated_data,
                )

                # Create order items
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
                        product=product,
                        fabric_type=fabric_type,
                        variant_type=variant_type,
                        quantity=qty,
                        price=final_price,
                    )

                # Create extra costs (shared)
                for extra_data in extra_costs_data:
                    OrderExtraCost.objects.create(order=order, **extra_data)

                # Generate invoice
                today = timezone.now().date()
                invoice_no = f"SI.{today.year}.{today.month:02d}.{order.pk:05d}"
                Invoice.objects.create(
                    status="partial" if is_deposit else "draft",
                    invoice_no=invoice_no,
                    order=order,
                    issued_date=today,
                    delivery_date=delivery_date,
                    note=note,
                )

        return order

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

            # Update order items if provided and non-empty
            if items_data is not None:
                # Clear and recreate items
                instance.items.all().delete()
                for item_data in items_data:
                    product = item_data["product"]
                    fabric_type = item_data["fabric_type"]
                    variant_type = item_data.get("variant_type")
                    qty = item_data["quantity"]

                    final_price, _ = get_dynamic_item_price(
                        product, fabric_type, variant_type, qty
                    )

                    OrderItem.objects.create(
                        order=instance,
                        product=product,
                        fabric_type=fabric_type,
                        variant_type=variant_type,
                        quantity=qty,
                        price=final_price,
                    )

            # Update extra costs if provided
            if extra_costs_data is not None:
                instance.extra_costs.all().delete()
                for extra_data in extra_costs_data:
                    OrderExtraCost.objects.create(order=instance, **extra_data)

            # Update invoice if exists
            invoice = getattr(instance, "invoice", None)
            if invoice:
                if delivery_date:
                    invoice.delivery_date = delivery_date
                if note:
                    invoice.note = note
                invoice.save()

        return instance


class OrderItemListSerializer(serializers.ModelSerializer):
    product_name = serializers.SerializerMethodField()
    fabric_type = serializers.CharField(source="fabric_type.name")
    unit = serializers.SerializerMethodField()
    # subtotal = serializers.SerializerMethodField()

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

    def to_representation(self, instance):
        data = super().to_representation(instance)
        price = data.get("price")
        if price is not None:
            try:
                price_float = float(price)
                if price_float == int(price_float):
                    data["price"] = int(price_float)
                else:
                    data["price"] = price_float
            except (TypeError, ValueError):
                pass
        return data

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
        return variant_type.unit.upper() if variant_type else None


class InvoiceSummarySerializer(BaseModelSerializer):
    total_invoice = serializers.SerializerMethodField()
    total_extra_cost = serializers.SerializerMethodField()
    grand_total = serializers.SerializerMethodField()

    class Meta:
        model = Invoice
        fields = [
            "pk",
            "invoice_no",
            "issued_date",
            "delivery_date",
            "total_invoice",
            "total_extra_cost",
            "grand_total",
            "status",
        ]

    def get_total_extra_cost(self, obj):
        # Get total of extra costs related to this invoice's order
        order = obj.order if hasattr(obj, "order") else None
        if order and hasattr(order, "extra_costs"):
            total = 0
            for extra_cost in order.extra_costs.all():
                if extra_cost.quantity is not None and extra_cost.amount is not None:
                    total += extra_cost.quantity * float(extra_cost.amount)
            # Return as int if there's no decimal part
            if total == int(total):
                return int(total)
            return float(total)
        return 0

    def get_total_invoice(self, obj):
        # Calculate total invoice from related order items
        order = getattr(obj, "order", None)
        if order and hasattr(order, "items"):
            total = 0
            for item in order.items.all():
                if item.price is not None and item.quantity is not None:
                    total += float(item.price) * item.quantity
            if total == int(total):
                return int(total)
            return float(total)
        return 0

    def get_grand_total(self, obj):
        # grand_total = total_invoice + total_extra_cost
        total_invoice = self.get_total_invoice(obj)
        total_extra_cost = self.get_total_extra_cost(obj)
        grand_total = total_invoice + total_extra_cost
        if grand_total == int(grand_total):
            return int(grand_total)
        return float(grand_total)


class OrderListSerializer(BaseModelSerializer):
    customer = CustomerSerializer(read_only=True)
    invoice = InvoiceSummarySerializer(read_only=True)
    items = OrderItemListSerializer(many=True, read_only=True)
    # extra_costs = OrderExtraCostSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "pk",
            "convection_name",
            "order_type",
            "customer",
            "priority_status",
            "status",
            "created",
            "items",
            "invoice",
            # "extra_costs",
            # Marketplace fields
            "user_name",
            "order_number",
            "marketplace",
            "order_choice",
            "estimated_shipping_date",
            # CS2
            "reminder_one",
            "reminder_two",
            "is_expired",
            "is_paid_off",
            "note",
            "shipping_courier",
            "deposit_amount",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        deposit_amount = data.get("deposit_amount")
        if deposit_amount is not None:
            try:
                dep_float = float(deposit_amount)
                if dep_float == int(dep_float):
                    data["deposit_amount"] = int(dep_float)
                else:
                    data["deposit_amount"] = dep_float
            except (TypeError, ValueError):
                pass
        return data


class OrderDetailSerializer(BaseModelSerializer):
    customer = CustomerSerializer(read_only=True)
    invoice = InvoiceSummarySerializer(read_only=True)
    items = OrderItemListSerializer(many=True, read_only=True)
    extra_costs = OrderExtraCostSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "pk",
            "order_type",
            "convection_name",
            "customer",
            "priority_status",
            "status",
            "created",
            "items",
            "invoice",
            "extra_costs",
            # Marketplace fields
            "user_name",
            "order_number",
            "marketplace",
            "order_choice",
            "estimated_shipping_date",
            # CS 2
            "reminder_one",
            "reminder_two",
            "is_expired",
            "is_paid_off",
            "note",
            "shipping_courier",
            "deposit_amount",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        deposit_amount = data.get("deposit_amount")
        if deposit_amount is not None:
            try:
                dep_float = float(deposit_amount)
                if dep_float == int(dep_float):
                    data["deposit_amount"] = int(dep_float)
                else:
                    data["deposit_amount"] = dep_float
            except (TypeError, ValueError):
                pass

        # --- 2️⃣ Remove invoice if items is empty ---
        items = data.get("items") or []
        if not items:
            data["invoice"] = None

        return data


class OrderKonveksiListSerializer(BaseModelSerializer):
    customer = CustomerSerializer(read_only=True)
    invoice = InvoiceSummarySerializer(read_only=True)
    items = OrderItemListSerializer(many=True, read_only=True)
    detail_order = serializers.SerializerMethodField()
    qty = serializers.SerializerMethodField()
    # extra_costs = OrderExtraCostSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "pk",
            "order_type",
            "convection_name",
            "customer",
            "priority_status",
            "status",
            "created",
            "items",
            "invoice",
            # CS2
            "reminder_one",
            # "is_reminder_one",
            "reminder_two",
            # "is_reminder_two",
            "is_expired",
            "is_paid_off",
            "note",
            "shipping_courier",
            "deposit_amount",
            "detail_order",
            "qty",
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        deposit_amount = data.get("deposit_amount")
        if deposit_amount is not None:
            try:
                dep_float = float(deposit_amount)
                if dep_float == int(dep_float):
                    data["deposit_amount"] = int(dep_float)
                else:
                    data["deposit_amount"] = dep_float
            except (TypeError, ValueError):
                pass

        # --- Set invoice to null if items is empty ---
        items = data.get("items") or []
        if not items:
            data["invoice"] = None

        return data

    def get_detail_order(self, obj):
        """
        Returns combined quantity string for an order.
        Example outputs:
            "3 ATASAN + 2 STEL"
            "3 + 2 ATASAN"  (if some variant_type are null)
        """
        items = OrderItem.objects.filter(order=obj)
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
        items = OrderItem.objects.filter(order=obj)
        if not items.exists():
            return 0

        total_qty = 0

        for item in items:
            qty = item.quantity or 0
            unit = None

            # Try to get unit name from variant_type
            if getattr(item.variant_type, "unit", None):
                unit = str(item.variant_type.unit).upper().strip()

            total_qty += get_qty_value(unit, qty)

        return total_qty


class OrderMarketplaceListSerializer(BaseModelSerializer):
    class Meta:
        model = Order
        fields = [
            "pk",
            "order_type",
            "priority_status",
            # "status",
            "created",
            # Marketplace fields
            "user_name",
            "order_number",
            "marketplace",
            "order_choice",
            "estimated_shipping_date",
            # CS2
            # "reminder_one",
            # "reminder_two",
            # "is_expired",
            # "is_paid_off",
            "note",
            "shipping_courier",
        ]
