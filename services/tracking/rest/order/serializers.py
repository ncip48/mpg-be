from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db.models import Q
from rest_framework import serializers

from services.forecast.models import Forecast
from services.order.models import Order, OrderItem

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("TrackingSerializer",)


class TrackingSerializer(serializers.Serializer):
    identifier = serializers.CharField(write_only=True)

    TRACKING_STEPS = [
        ("print_verifications", "Verifikasi Print"),
        ("qc_press_verifications", "QC Press"),
        ("qc_line_verifications", "QC Line"),
        ("qc_cutting_verifications", "QC Cutting"),
        ("qc_finishings", "QC Finishing"),
        ("warehouse_deliveries", "Pengiriman Gudang"),
        ("warehouse_receipts", "Penerimaan Gudang"),
    ]

    def validate(self, attrs):
        identifier = attrs["identifier"]

        order = (
            Order.objects.filter(
                Q(subid=identifier) |
                Q(identifier=identifier) |
                Q(order_number=identifier)
            )
            .first()
        )

        if order is None:
            order_item = (
                OrderItem.objects.select_related("order")
                .filter(
                    Q(subid=identifier) |
                    Q(order__identifier=identifier)
                )
                .first()
            )

            if order_item:
                order = order_item.order

        if order is None:
            raise serializers.ValidationError(
                {"identifier": "Order not found."}
            )

        attrs["order"] = order
        return attrs

    @property
    def data(self):
        if not hasattr(self, "_data"):
            self._data = self.build_response(self.validated_data["order"])
        return self._data

    def build_response(self, order):
        print(order)
        forecasts = (
            Forecast.objects.filter(
                Q(order=order) |
                Q(order_item__order=order)
            )
            .distinct()
        )

        return {
            "order": {
                "subid": order.subid,
                "identifier": order.identifier,
            },
            "forecasts": [
                self._serialize_forecast(forecast)
                for forecast in forecasts
            ],
        }

    def _serialize_forecast(self, forecast):
        return {
            "forecast": forecast.subid,
            "forecast_number": forecast.forecast_number,
            "steps": [
                self._serialize_step(forecast, relation, label)
                for relation, label in self.TRACKING_STEPS
            ],
        }

    def _serialize_step(self, forecast, relation, label):
        obj = getattr(forecast, relation, None)

        if obj is None:
            return {
                "key": relation,
                "label": label,
                "subid": None,
                "status": "PENDING",
            }

        return {
            "key": relation,
            "label": label,
            "subid": obj.subid,
            "status": "ACC"
            if getattr(obj, "is_approved", True)
            else "REJECT",
        }