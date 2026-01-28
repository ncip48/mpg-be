from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import transaction
from django.db.models import Q
from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.customer.models.customer import Customer
from services.customer.rest.customer.serializers import CustomerSerializerSimple
from services.deposit.rest.deposit.serializers import DepositListSerializer
from services.forecast.models.forecast import Forecast
from services.forecast.models.stock_item import StockItem
from services.forecast.models.stock_item_size import StockItemSize
from services.forecast.rest.forecast.utils import format_tanggal_indonesia
from services.order.models.order import Order
from services.order.models.order_form import OrderForm
from services.order.models.order_item import OrderItem
from services.order.rest.order.serializers import FloatToIntRepresentationMixin
from services.printer.models.printer import Printer
from services.printer.rest.printer.serializers import PrinterSerializer
from services.product.models.fabric_type import FabricType
from services.product.models.product import Product
from services.product.models.variant_type import ProductVariantType

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("ForecastSerializer",)


class StockItemSizeSerializer(BaseModelSerializer):
    size = serializers.CharField()
    qty = serializers.IntegerField(default=0)

    class Meta:
        model = StockItemSize
        fields = (
            "pk",
            "size",
            "qty",
        )


class StockItemInputSerializer(BaseModelSerializer):
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
    sizes = StockItemSizeSerializer(many=True, write_only=True)

    class Meta:
        model = StockItem
        fields = (
            "product",
            "fabric_type",
            "variant_type",
            "quantity",
            "sizes",
        )


class StockItemListSerializer(FloatToIntRepresentationMixin, BaseModelSerializer):
    product_name = serializers.SerializerMethodField()
    fabric_type = serializers.CharField(source="fabric_type.name")
    unit = serializers.SerializerMethodField()
    # subtotal = serializers.SerializerMethodField()
    has_forecast = serializers.SerializerMethodField()

    # Define fields for the mixin
    float_to_int_fields = ["price"]

    class Meta:
        model = StockItem
        fields = [
            "product_name",
            "fabric_type",
            "unit",
            "price",
            "quantity",
            "subtotal",
            "has_forecast",
        ]

    # to_representation is now handled by FloatToIntRepresentationMixin
    def get_has_forecast(self, instance):
        return Forecast.objects.filter(order_item=instance).exists()

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
    # sku = serializers.SerializerMethodField()
    # printer = serializers.SerializerMethodField()
    # printer = serializers.SlugRelatedField(
    #     slug_field="subid", queryset=Printer.objects.all(), write_only=True
    # )
    stock_item = StockItemInputSerializer(write_only=True, required=False)
    product_name = serializers.SerializerMethodField()
    fabric_name = serializers.SerializerMethodField()
    # priority_status = serializers.SerializerMethodField()
    # estimate_sent = serializers.SerializerMethodField()

    created_by = serializers.SlugRelatedField(slug_field="subid", read_only=True)

    progress = serializers.SerializerMethodField()

    # details = serializers.SerializerMethodField()

    class Meta:
        model = Forecast
        fields = [
            "pk",
            # "printer",
            "forecast_number",
            "customer",
            "is_stock",
            "convection_name",
            "stock_item",
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
            "progress",
        ]
        read_only_fields = ("created", "updated", "created_by")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if not request:
            return

        # Works for POST & PATCH
        is_stock = request.data.get("is_stock")

        if str(is_stock).lower() in ("true", "1"):
            self.fields["stock_item"].required = True

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["sku"] = self.sku(instance)
        data["printer"] = self.printer_display(instance)
        data["priority_status"] = self.priority_status(instance)
        data["estimate_sent"] = self.estimate_sent(instance)
        return data

    def printer_display(self, obj):
        if obj.is_stock:
            printer = Printer.objects.filter(
                pk=StockItem.objects.filter(forecast=obj).first().product.printer.id
            ).first()
        else:
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
        if obj.is_stock:
            return "STOK JB"
        else:
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

    def get_product_name(self, obj):
        if obj.is_stock:
            # print(obj.stock_items)
            stock_item = StockItem.objects.filter(forecast=obj).first()
            product = stock_item.product.name if stock_item else None
        else:
            if obj.order_item:
                product = Product.objects.filter(pk=obj.order_item.product.id).first()
                product = product.name if product else None
            else:
                product = OrderForm.objects.filter(order=obj.order).first()
                date = (
                    format_tanggal_indonesia(product.email_send_date)
                    if product.email_send_date
                    else "-"
                )
                product = f"{product.marketplace} {date} Sesi {product.session}"

        return product

    def sku(self, obj):
        if obj.is_stock:
            stock_item = StockItem.objects.filter(forecast=obj).first()
            sku = stock_item.product.sku if stock_item else None
        else:
            sku = "Custom"
        return sku

    def get_fabric_name(self, obj):
        if obj.is_stock:
            # print(obj.stock_items)
            stock_item = StockItem.objects.filter(forecast=obj).first()
            fabric = stock_item.fabric_type.name if stock_item else None
        else:
            if obj.order_item:
                fabric = (
                    obj.order_item.fabric_type.name
                    if obj.order_item.fabric_type
                    else None
                )
            else:
                product = OrderForm.objects.filter(order=obj.order).first()
                fabric = product.fabric_type.name if product else None

        return fabric

    def priority_status(self, obj):
        if obj.is_stock:
            ps = obj.priority_status.upper()
        else:
            if obj.order_item:
                ps = obj.order_item.deposit.priority_status.upper()
            else:
                ps = obj.order.priority_status.upper()

        return ps

    def estimate_sent(self, obj):
        if obj.is_stock:
            es = obj.estimate_sent
        else:
            if obj.order_item:
                deposit = DepositListSerializer(obj.order_item.deposit)
                es = deposit.data["estimate_sent"]
            else:
                es = obj.order.estimated_shipping_date

        return es

    def get_progress(self, obj):
        """
        Progress is determined by the first missing verification step
        following the business workflow order.
        """

        steps = [
            ("print_verifications", "Menunggu Verifikasi Print"),
            ("qc_line_verifications", "Menunggu QC Line"),
            ("qc_cutting_verifications", "Menunggu QC Cutting"),
            ("qc_finishings", "Menunggu QC Finishing"),
            ("qc_finishing_defects", "Menunggu QC Finishing Defect"),
            ("warehouse_deliveries", "Menunggu Pengiriman Gudang"),
            ("warehouse_receipts", "Menunggu Penerimaan Gudang"),
        ]

        for relation, label in steps:
            # same logic as filtersets: __isnull
            if not getattr(obj, relation).exists():
                return label

        return "Selesai"

    @transaction.atomic
    def create(self, validated_data):
        request = self.context.get("request")

        # Extract nested data
        stock_item_data = validated_data.pop("stock_item", None)

        if request and request.user and request.user.is_authenticated:
            validated_data["created_by"] = request.user

        # Create Forecast
        forecast = Forecast.objects.create(**validated_data)

        # Create stock item + nested sizes
        if stock_item_data:
            sizes_data = stock_item_data.pop("sizes", [])

            # First create StockItem (sizes removed)
            stock_item = StockItem.objects.create(forecast=forecast, **stock_item_data)

            # Then create StockItemSize rows
            if sizes_data:
                StockItemSize.objects.bulk_create(
                    [
                        StockItemSize(
                            stock_item=stock_item,
                            size=size_obj["size"],
                            qty=size_obj["qty"],
                        )
                        for size_obj in sizes_data
                    ]
                )

        return forecast
