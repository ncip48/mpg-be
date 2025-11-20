from __future__ import annotations

import logging
from collections import Counter
from typing import TYPE_CHECKING

from django.db.models import Q
from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.customer.models.customer import Customer
from services.customer.rest.customer.serializers import CustomerSerializerSimple
from services.deposit.rest.deposit.serializers import DepositListSerializer
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.utils import format_tanggal_indonesia
from services.order.models.order import Order
from services.order.models.order_form import OrderForm
from services.order.models.order_form_detail import OrderFormDetail
from services.order.models.order_item import OrderItem
from services.printer.models.printer import Printer
from services.printer.rest.printer.serializers import PrinterSerializer
from services.product.models.product import Product

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

    customer = serializers.SerializerMethodField()
    convection_name = serializers.SerializerMethodField()
    sku = serializers.SerializerMethodField()
    printer = serializers.SerializerMethodField()
    product_name = serializers.SerializerMethodField()
    fabric_name = serializers.SerializerMethodField()
    priority_status = serializers.SerializerMethodField()
    estimate_sent = serializers.SerializerMethodField()

    created_by = serializers.SlugRelatedField(slug_field="subid", read_only=True)

    details = serializers.SerializerMethodField()
    count_po = serializers.SerializerMethodField()

    class Meta:
        model = Forecast
        fields = [
            "pk",
            "printer",
            "customer",
            "convection_name",
            "product_name",
            "fabric_name",
            "priority_status",
            "estimate_sent",
            "sku",
            "order",
            "order_item",
            "date_forecast",
            "print_status",
            "created_by",
            "created",
            "updated",
            "details",
            "count_po",
        ]
        read_only_fields = ("created", "updated", "created_by")

    def get_details(self, obj):
        """
        Normalize and group sizes:
        - "L MEN" → "L"
        - "S WOMEN" → "S"
        - "L KIDS" → "KIDS"
        - "XS GIRL" → "GIRL"
        """

        # Detect source (order_item or order)
        if obj.order_item:
            order_form = OrderForm.objects.filter(order_item=obj.order_item).first()
        else:
            order_form = OrderForm.objects.filter(order=obj.order).first()

        if not order_form:
            return []

        details = OrderFormDetail.objects.filter(order_form=order_form)

        def normalize_type(shirt_size: str) -> str:
            parts = shirt_size.upper().split()

            for keyword in ["KIDS"]:
                if keyword in parts:
                    return keyword

            # Otherwise use first part (S, M, L, XL, etc.)
            return parts[0]

        # Normalize + count
        types = [normalize_type(d.shirt_size) for d in details]
        counter = Counter(types)

        return [{"type": t, "count": c} for t, c in counter.items()]

    def get_printer(self, obj):
        if obj.order_item:
            printer = Printer.objects.filter(
                pk=obj.order_item.product.printer.id
            ).first()
        else:
            printer = Printer.objects.filter(
                pk=OrderForm.objects.filter(order=obj.order).first().printer_id
            ).first()

        if not printer:
            return None

        return PrinterSerializer(printer).data

    def get_convection_name(self, obj):
        if obj.order_item:
            order = obj.order_item.order
        else:
            order = None

        return order.convection_name if order else None

    def get_customer(self, obj):
        if obj.order_item:
            customer = Customer.objects.filter(
                pk=obj.order_item.order.customer.id
            ).first()
        else:
            customer = None

        return CustomerSerializerSimple(customer).data if customer else None

    def get_sku(self, obj):
        return "Custom"

    def get_count_po(self, obj):
        """
        Count ALL items in OrderFormDetail.
        """

        # Detect source
        if obj.order_item:
            order_form = OrderForm.objects.filter(order_item=obj.order_item).first()
        else:
            order_form = OrderForm.objects.filter(order=obj.order).first()

        if not order_form:
            return 0  # total count, so return integer

        # Get all detail items
        details = OrderFormDetail.objects.filter(order_form=order_form)

        # Return total number of rows/items
        return details.count()

    def get_product_name(self, obj):
        if obj.order_item:
            product = Product.objects.filter(pk=obj.order_item.product.id).first()
            product = product.name if product else None
        else:
            product = OrderForm.objects.filter(order=obj.order).first()
            product = f"{product.marketplace} {format_tanggal_indonesia(product.email_send_date)} Sesi {product.session}"

        return product

    def get_fabric_name(self, obj):
        if obj.order_item:
            fabric = (
                obj.order_item.fabric_type.name if obj.order_item.fabric_type else None
            )
        else:
            product = OrderForm.objects.filter(order=obj.order).first()
            fabric = product.fabric_type.name if product else None

        return fabric

    def get_priority_status(self, obj):
        if obj.order_item:
            ps = obj.order_item.deposit.priority_status.upper()
        else:
            ps = obj.order.priority_status.upper()

        return ps

    def get_estimate_sent(self, obj):
        if obj.order_item:
            deposit = DepositListSerializer(obj.order_item.deposit)
            es = deposit.data["estimate_sent"]
        else:
            es = obj.order.estimated_shipping_date

        return es
