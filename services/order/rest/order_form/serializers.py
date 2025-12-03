from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core import settings
from core.common.serializers import BaseModelSerializer
from services.customer.rest.customer.serializers import CustomerSerializerSimple
from services.deposit.models.deposit import Deposit
from services.order.models.order import Order
from services.order.models.order_form import OrderForm
from services.order.models.order_form_detail import OrderFormDetail
from services.order.models.order_item import OrderItem
from services.order.rest.order.serializers import (
    FloatToIntRepresentationMixin,
    OrderItemListSerializer,
    OrderMarketplaceListSerializer,
)
from services.order.rest.order.utils import get_qty_value
from services.printer.models.printer import Printer
from services.printer.rest.printer.serializers import PrinterSerializer
from services.product.models.fabric_type import FabricType
from services.product.rest.fabric_type.serializers import FabricTypeSerializerSimple

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("OrderFormSerializer", "OrderFormDetailSerializer")


class _OrderSerializer(BaseModelSerializer):
    class Meta:
        model = Order
        fields = ["pk", "identifier"]


class _DepositListSerializer(FloatToIntRepresentationMixin, BaseModelSerializer):
    float_to_int_fields = ["deposit_amount"]
    order = _OrderSerializer(read_only=True)

    class Meta:
        model = Deposit
        fields = [
            "pk",
            "order",
            "priority_status",
            "created",
            "lead_time",
            "reminder_one",
            "reminder_two",
            "is_expired",
            "is_paid_off",
            "note",
            "shipping_courier",
            "deposit_amount",
            "accepted_at",
        ]


class OrderFormDetailSerializer(BaseModelSerializer):
    back_name = serializers.CharField(required=True, allow_blank=False)
    jersey_number = serializers.CharField(required=True)
    shirt_size = serializers.CharField(required=True)
    pants_size = serializers.CharField(required=True)

    class Meta:
        model = OrderFormDetail
        fields = ["pk", "back_name", "jersey_number", "shirt_size", "pants_size"]


class OrderFormSerializer(BaseModelSerializer):
    """
    Serializer for order form
    """

    # Write-only FK, using subid as input
    order_item = serializers.SlugRelatedField(
        slug_field="subid", queryset=OrderItem.objects.all(), write_only=True
    )

    # New write-only field
    details = OrderFormDetailSerializer(many=True, required=False, allow_null=True)

    # Read-only nested output of order_item
    order_item_display = OrderItemListSerializer(source="order_item", read_only=True)
    total_qty = serializers.SerializerMethodField()
    printer = PrinterSerializer(source="order_item.product.printer", read_only=True)
    customer = CustomerSerializerSimple(
        source="order_item.order.customer", read_only=True
    )
    deposit = _DepositListSerializer(source="order_item.deposit", read_only=True)

    class Meta:
        model = OrderForm
        fields = [
            "pk",
            "form_type",
            "printer",
            "customer",
            "deposit",
            "order_item",
            "order_item_display",
            "team_name",
            "design_front",
            "design_back",
            "preview_print_front",
            "preview_print_back",
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
            "details",
        ]
        read_only_fields = ["pk"]

    def validate(self, attrs):
        errors = {}

        file_fields = [
            "design_front",
            "design_back",
            "preview_print_front",
            "preview_print_back",
            "logo_chest_right",
            "logo_center",
            "logo_chest_left",
            "logo_back",
            "logo_pants",
        ]

        for field in file_fields:
            value = attrs.get(field)
            if value:
                # Example: Limit file types
                allowed_types = ["image/jpeg", "image/png", "image/jpg"]
                if value.content_type not in allowed_types:
                    errors[field] = (
                        f"Invalid file type '{value.content_type}'. "
                        "Only JPEG and PNG images are allowed."
                    )

                # Example: File size validation (max 10MB)
                if value.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
                    errors[field] = (
                        f"File size too large ({value.size / 1024 / 1024:.1f} MB). "
                        f"Maximum allowed is {settings.FILE_UPLOAD_MAX_MEMORY_SIZE / 1024 / 1024:.1f} MB."
                    )

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def run_validation(self, data=serializers.empty):
        """
        Fix for nested writable serializers:
        Force nested lists to accept partial updates during PATCH.
        """
        if self.partial and "details" in self.fields:
            field = self.fields["details"]
            field.partial = True
        return super().run_validation(data)

    def _parse_json_field(self, data, field_name):
        """
        Safely get and parse a JSON-like field that may come from:
         - JSON body (list/dict already)
         - multipart form-data (value is a list of strings, or string)
        Returns Python object or None.
        """
        # prefer explicit lookup in initial_data if available (for form-data)
        # print("RAW DETAILS:", repr(getattr(self, "initial_data", {}).get("details")))
        value = None
        # `data` might be a QueryDict or dict; handle both
        if isinstance(data, dict) and field_name in data:
            value = data.get(field_name)
        else:
            # fallback: try to read from self.initial_data if present
            value = getattr(self, "initial_data", {}).get(field_name)

        # if value is a list (common with multipart/form-data), unwrap first element
        if isinstance(value, (list, tuple)):
            value = value[0] if value else None

        # if it's already a Python list/dict (when Content-Type: application/json), return as-is
        if isinstance(value, (list, dict)):
            return value

        # if it's a string, attempt JSON parse
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError({field_name: "Invalid JSON format"})

        # otherwise None or unknown -> return None
        return None

    def _get_details_validated(self, raw_list):
        if raw_list is None:
            return []
        serializer = OrderFormDetailSerializer(data=raw_list, many=True)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def to_internal_value(self, data):
        """
        Only decode details when it's passed as a JSON string (form-data).
        Do NOT pre-validate nested serializer here — let DRF handle validation.
        """
        data = data.copy()
        parsed = self._parse_json_field(data, "details")
        print(parsed)
        if parsed is not None:
            # assign the parsed structure so DRF will validate it using the declared field
            data["details"] = parsed
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["details"] = OrderFormDetailSerializer(
            instance.order_form_details.all(), many=True
        ).data
        return data

    def create(self, validated_data):
        details_data = validated_data.pop("details", None)

        # fallback when DRF wipes nested data
        if details_data is None:
            raw = self._parse_json_field(self.initial_data or {}, "details")
            if raw is not None:
                details_data = self._get_details_validated(raw)

        if details_data is None:
            details_data = []

        validated_data["created_by"] = self.context["request"].user

        order_form = super().create(validated_data)

        # Create OrderFormDetail rows
        for detail in details_data:
            OrderFormDetail.objects.create(order_form=order_form, **detail)

        return order_form

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)

        # This logic is to check if 'details' was *present* in the
        # raw request. If it wasn't, we shouldn't modify the details.
        details_key_present = "details" in (self.initial_data or {})

        if details_data is None and details_key_present:
            # 'details' was in the request, so parse and validate it.
            # This will result in [] for "details: null" or "details: []"
            # or a populated list for "details: [...]"
            raw = self._parse_json_field(self.initial_data or {}, "details")
            details_data = self._get_details_validated(raw)

        # Update the main OrderForm fields (team_name, etc.)
        instance = super().update(instance, validated_data)

        # --- ADD THIS LOGIC ---
        # If 'details' was part of the request, update the nested items.
        if details_key_present:
            # 'details_data' will be a list (possibly empty)

            # 1. Delete all existing details for this form
            instance.order_form_details.all().delete()

            # 2. Create the new details from the request data
            for detail in details_data:
                OrderFormDetail.objects.create(order_form=instance, **detail)

        # If 'details' was not in the request, we do nothing,
        # preserving the existing details.

        return instance

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


class OrderFormMarketplaceSerializer(BaseModelSerializer):
    """
    Serializer for order form marketplace
    """

    order = serializers.SlugRelatedField(
        slug_field="subid", queryset=Order.objects.all(), write_only=True
    )

    printer = serializers.SlugRelatedField(
        slug_field="subid", queryset=Printer.objects.all(), write_only=True
    )

    fabric_type = serializers.SlugRelatedField(
        slug_field="subid", queryset=FabricType.objects.all(), write_only=True
    )

    details = OrderFormDetailSerializer(many=True, required=False, allow_null=True)

    class Meta:
        model = OrderForm
        fields = [
            "pk",
            "form_type",
            "order",
            "printer",
            "fabric_type",
            "marketplace",
            "email_send_date",
            "session",
            "preview_print_front",
            "preview_print_back",
            "details",
        ]
        read_only_fields = ["pk"]

    def run_validation(self, data=serializers.empty):
        """
        Fix for nested writable serializers:
        Force nested lists to accept partial updates during PATCH.
        """
        if self.partial and "details" in self.fields:
            field = self.fields["details"]
            field.partial = True
        return super().run_validation(data)

    def _parse_json_field(self, data, field_name):
        """
        Safely get and parse a JSON-like field that may come from:
         - JSON body (list/dict already)
         - multipart form-data (value is a list of strings, or string)
        Returns Python object or None.
        """
        # prefer explicit lookup in initial_data if available (for form-data)
        # print("RAW DETAILS:", repr(getattr(self, "initial_data", {}).get("details")))
        value = None
        # `data` might be a QueryDict or dict; handle both
        if isinstance(data, dict) and field_name in data:
            value = data.get(field_name)
        else:
            # fallback: try to read from self.initial_data if present
            value = getattr(self, "initial_data", {}).get(field_name)

        # if value is a list (common with multipart/form-data), unwrap first element
        if isinstance(value, (list, tuple)):
            value = value[0] if value else None

        # if it's already a Python list/dict (when Content-Type: application/json), return as-is
        if isinstance(value, (list, dict)):
            return value

        # if it's a string, attempt JSON parse
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError({field_name: "Invalid JSON format"})

        # otherwise None or unknown -> return None
        return None

    def _get_details_validated(self, raw_list):
        if raw_list is None:
            return []
        serializer = OrderFormDetailSerializer(data=raw_list, many=True)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data

    def to_internal_value(self, data):
        """
        Only decode details when it's passed as a JSON string (form-data).
        Do NOT pre-validate nested serializer here — let DRF handle validation.
        """
        data = data.copy()
        parsed = self._parse_json_field(data, "details")
        print(parsed)
        if parsed is not None:
            # assign the parsed structure so DRF will validate it using the declared field
            data["details"] = parsed
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["details"] = OrderFormDetailSerializer(
            instance.order_form_details.all(), many=True
        ).data
        data["printer"] = PrinterSerializer(instance.printer).data
        data["order"] = OrderMarketplaceListSerializer(instance.order).data
        data["fabric_type"] = FabricTypeSerializerSimple(instance.fabric_type).data
        return data
        return data

    def create(self, validated_data):
        details_data = validated_data.pop("details", None)

        # fallback when DRF wipes nested data
        if details_data is None:
            raw = self._parse_json_field(self.initial_data or {}, "details")
            if raw is not None:
                details_data = self._get_details_validated(raw)

        if details_data is None:
            details_data = []

        validated_data["created_by"] = self.context["request"].user

        order_form = super().create(validated_data)

        # Create OrderFormDetail rows
        for detail in details_data:
            OrderFormDetail.objects.create(order_form=order_form, **detail)

        return order_form

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)

        # This logic is to check if 'details' was *present* in the
        # raw request. If it wasn't, we shouldn't modify the details.
        details_key_present = "details" in (self.initial_data or {})

        if details_data is None and details_key_present:
            # 'details' was in the request, so parse and validate it.
            # This will result in [] for "details: null" or "details: []"
            # or a populated list for "details: [...]"
            raw = self._parse_json_field(self.initial_data or {}, "details")
            details_data = self._get_details_validated(raw)

        # Update the main OrderForm fields (team_name, etc.)
        instance = super().update(instance, validated_data)

        # --- ADD THIS LOGIC ---
        # If 'details' was part of the request, update the nested items.
        if details_key_present:
            # 'details_data' will be a list (possibly empty)

            # 1. Delete all existing details for this form
            instance.order_form_details.all().delete()

            # 2. Create the new details from the request data
            for detail in details_data:
                OrderFormDetail.objects.create(order_form=instance, **detail)

        # If 'details' was not in the request, we do nothing,
        # preserving the existing details.

        return instance
