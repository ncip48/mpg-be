from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.serializers import ForecastSerializer
from services.warehouse.models import WarehouseDelivery
from services.warehouse.models.warehouse_receipt import WarehouseReceipt

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "BaseWarehouseDeliverySerializer",
    "WarehouseDeliverySerializer",
)


class BaseWarehouseDeliverySerializer(BaseModelSerializer):
    forecast = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Forecast.objects.all(),
        write_only=True,
        required=True,
    )
    her = serializers.SerializerMethodField()

    class Meta:
        model = WarehouseDelivery
        fields = (
            "subid",
            "forecast",
            "delivered_by",
            "delivery_date",
            "delivery_detail",
            "defect_count",
            "detail",
            "her",
            "created",
            "updated",
        )
        read_only_fields = (
            "created",
            "updated",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # expand delivered_by user
        data["delivered_by"] = (
            UserSerializerSimple(instance.delivered_by).data
            if instance.delivered_by
            else None
        )
        return data

    def get_her(self, obj):
        receipt = WarehouseReceipt.objects.filter(forecast=obj.forecast).first()
        return receipt.note if receipt else None

    def create(self, validated_data):
        forecast = validated_data.pop("forecast")
        return WarehouseDelivery.objects.create(
            forecast=forecast,
            **validated_data,
        )


class WarehouseDeliverySerializer(ForecastSerializer):
    warehouse_delivery = serializers.SerializerMethodField()

    class Meta:
        model = Forecast
        fields = ForecastSerializer.Meta.fields + [
            "warehouse_delivery",
        ]

    def get_warehouse_delivery(self, obj):
        try:
            receipt = obj.warehouse_deliveries  # related_name from model
            return BaseWarehouseDeliverySerializer(receipt).data
        except WarehouseDelivery.DoesNotExist:
            return None
