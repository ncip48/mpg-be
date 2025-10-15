from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.customer.models.customer import Customer
from services.customer.rest.customer.serializers import CustomerSerializer
from services.order.models import Order, OrderItem
from services.order.models.invoice import Invoice
from services.order.models.order_extra_cost import OrderExtraCost
from services.product.models import ProductVariantType, Product, FabricType

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "OrderItemInputSerializer",
    "OrderCreateSerializer"
)

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
        if hasattr(obj, 'quantity') and hasattr(obj, 'amount') and obj.quantity is not None and obj.amount is not None:
            total = obj.quantity * obj.amount
            # Format: no .0 if integer
            if total == int(total):
                return int(total)
            return float(total)
        return None


class OrderItemInputSerializer(BaseModelSerializer):
    product = serializers.SlugRelatedField(slug_field="subid", queryset=Product.objects.all())
    fabric_type = serializers.SlugRelatedField(slug_field="subid", queryset=FabricType.objects.all())
    variant_type = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=ProductVariantType.objects.all(),
        required=False,
        allow_null=True
    )
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.DecimalField(max_digits=12, decimal_places=2)
    
    class Meta:
        model = OrderItem
        fields = (
            "product",
            "fabric_type",
            "variant_type",
            "quantity",
            "price",
        )


class OrderCreateSerializer(BaseModelSerializer):
    is_deposit = serializers.BooleanField(default=False)
    customer = serializers.SlugRelatedField(slug_field="subid", queryset=Customer.objects.all())
    order_type = serializers.ChoiceField(choices=[("konveksi", "Konveksi"), ("marketplace", "Marketplace")])
    priority_status = serializers.ChoiceField(choices=[("reguler", "Reguler"), ("urgent", "Urgent")], default="reguler")
    items = OrderItemInputSerializer(many=True)
    delivery_date = serializers.DateField(required=False)
    note = serializers.CharField(required=False, allow_blank=True)
    extra_costs = OrderExtraCostSerializer(many=True, required=False)
    
    class Meta:
        model = Order
        fields = (
            "is_deposit",
            "customer",
            "order_type",
            "priority_status",
            "items",
            "delivery_date",
            "note",
            "extra_costs"
        )

    def create(self, validated_data):
        from decimal import Decimal
        from django.utils import timezone
        from django.db import transaction

        is_deposit = validated_data.pop("is_deposit", False)
        customer = validated_data.pop("customer")
        items_data = validated_data.pop("items")
        note = validated_data.pop("note", "")
        delivery_date = validated_data.pop("delivery_date", timezone.now().date())
        extra_costs_data = validated_data.pop("extra_costs", [])

        with transaction.atomic():
            # Create Order
            order = Order.objects.create(
                status="deposit" if is_deposit else "draft",
                customer=customer,
                created_by=self.context["request"].user,
                **validated_data
            )

            # Create Items
            for item_data in items_data:
                product = item_data["product"]
                fabric_type = item_data["fabric_type"]
                variant_type = item_data.get("variant_type")
                qty = item_data["quantity"]
                price = item_data["price"]

                OrderItem.objects.create(
                    order=order,
                    product_name=product,
                    fabric_type=fabric_type,
                    variant_type=variant_type,
                    quantity=qty,
                    price=price,
                )
                
            # Create extra costs
            for extra_data in extra_costs_data:
                OrderExtraCost.objects.create(order=order, **extra_data)

            # Generate invoice number (e.g., SI.2025.10.0001)
            today = timezone.now().date()
            invoice_no = f"SI.{today.year}.{today.month:02d}.{order.pk:05d}"

            invoice = Invoice.objects.create(
                status="partial" if is_deposit else "draft",
                invoice_no=invoice_no,
                order=order,
                issued_date=today,
                delivery_date=delivery_date,
                note=note,
            )

        return invoice

class OrderItemListSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source="product_name.name")
    fabric_type = serializers.CharField(source="fabric_type.name")
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["product_name", "fabric_type", "price", "quantity", "subtotal"]
    
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
    
    def get_subtotal(self, obj):
        # Get fabric_price if available based on product, fabric_type, variant_type
        variant_type = getattr(obj, "variant_type", None)
        fabric_type = getattr(obj, "fabric_type", None)
        price = getattr(obj, "price", 0)
        qty = getattr(obj, "quantity", 0)

        fabric_price_obj = None
        if variant_type and fabric_type:
            fabric_price_qs = getattr(variant_type, "fabric_prices", None)
            if fabric_price_qs is not None:
                fabric_price_qs_filtered = fabric_price_qs.filter(fabric_type=fabric_type, variant_type=variant_type)
                fabric_price_obj = fabric_price_qs_filtered.first()
        if fabric_price_obj and hasattr(fabric_price_obj, "price"):
            subtotal = qty * price + fabric_price_obj.price
        else:
            subtotal = qty * price
        return subtotal


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
            "customer",
            "priority_status",
            "status",
            "created",
            "items",
            "invoice",
            # "extra_costs",
        ]


class OrderDetailSerializer(BaseModelSerializer):
    customer = CustomerSerializer(read_only=True)
    invoice = InvoiceSummarySerializer(read_only=True)
    items = OrderItemListSerializer(many=True, read_only=True)
    extra_costs = OrderExtraCostSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "pk",
            "customer",
            "priority_status",
            "status",
            "created",
            "items",
            "invoice",
            "extra_costs"
        ]