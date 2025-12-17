from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.serializers import ForecastSerializer
from services.warehouse.models import WarehouseReceipt

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "BaseWarehouseReceiptSerializer",
    "WarehouseReceiptSerializer",
)


class BaseWarehouseReceiptSerializer(BaseModelSerializer):
    forecast = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Forecast.objects.all(),
        write_only=True,
        required=True,
    )

    count_receive = serializers.SerializerMethodField()
    count_defect = serializers.SerializerMethodField()
    count_difference = serializers.SerializerMethodField()

    class Meta:
        model = WarehouseReceipt
        fields = (
            "subid",
            "forecast",
            "received_by",
            "received_date",
            "receive_detail",
            "count_receive",
            "defect_detail",
            "defect_note",
            "count_defect",
            "count_difference",
            "note",
            "created",
            "updated",
        )
        read_only_fields = (
            "received_date",
            "created",
            "updated",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # expand received_by user
        data["received_by"] = (
            UserSerializerSimple(instance.received_by).data
            if instance.received_by
            else None
        )
        return data

    def create(self, validated_data):
        forecast = validated_data.pop("forecast")
        return WarehouseReceipt.objects.create(
            forecast=forecast,
            **validated_data,
        )

    def get_count_receive(self, obj):
        """
        Sum all `count` values from receive_detail array
        Only count items having BOTH `size` and `count`
        """
        receipt = obj
        if not receipt or not receipt.receive_detail:
            return 0

        total = 0
        for item in receipt.receive_detail:
            if (
                isinstance(item, dict)
                and "size" in item
                and "count" in item
                and isinstance(item["count"], int)
                and item["count"] > 0
            ):
                total += item["count"]

        return total

    def get_count_defect(self, obj):
        """
        Sum all `count` values from defect_detail array
        Only count items having BOTH `size` and `count`
        """
        receipt = obj
        if not receipt or not receipt.defect_detail:
            return 0

        total = 0
        for item in receipt.defect_detail:
            if (
                isinstance(item, dict)
                and "size" in item
                and "count" in item
                and isinstance(item["count"], int)
                and item["count"] > 0
            ):
                total += item["count"]

        return total

    def get_count_difference(self, instance):
        """
        count_difference = count_po (forecast) - count_receive
        """
        forecast = instance.forecast
        if not forecast:
            return 0

        # ForecastSerializer already defines get_count_po
        count_po = 0
        try:
            # call ForecastSerializer logic safely
            count_po = forecast.count_po if hasattr(forecast, "count_po") else 0

        except Exception:
            count_po = 0

        count_receive = self.get_count_receive(instance)

        return count_po - count_receive


class WarehouseReceiptSerializer(ForecastSerializer):
    warehouse_receipt = serializers.SerializerMethodField()

    class Meta:
        model = Forecast
        fields = ForecastSerializer.Meta.fields + [
            "warehouse_receipt",
        ]

    def get_warehouse_receipt(self, obj):
        try:
            receipt = obj.warehouse_receipts  # related_name from model
            return BaseWarehouseReceiptSerializer(receipt).data
        except WarehouseReceipt.DoesNotExist:
            return None
