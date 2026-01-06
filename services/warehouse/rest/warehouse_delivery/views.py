from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import connection
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from core.common.viewsets import BaseViewSet
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.filtersets import ForecastFilterSet
from services.warehouse.models import WarehouseDelivery
from services.warehouse.rest.warehouse_delivery.serializers import (
    BaseWarehouseDeliverySerializer,
    WarehouseDeliverySerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("WarehouseDeliveryViewSet",)


class WarehouseDeliveryViewSet(BaseViewSet):
    """
    ViewSet for Warehouse Receipt (QC Finishing Gudang).
    One Forecast can have only ONE WarehouseDelivery.
    """

    my_tags = ["Warehouse Receipt"]

    queryset = Forecast.objects.select_related(
        "warehouse_deliveries",
        "warehouse_receipts",
        "warehouse_deliveries__delivered_by",
        "order",
        "printer",
    ).prefetch_related(
        "order_item",
    )

    serializer_class = WarehouseDeliverySerializer
    lookup_field = "subid"

    search_fields = [
        "order__subid",
        "order_item__subid",
        "warehouse_deliveries__delivered_by__first_name",
    ]

    required_perms = [
        "warehouse.add_delivery",
        "warehouse.change_delivery",
        "warehouse.delete_delivery",
        "warehouse.view_delivery",
    ]

    filterset_class = ForecastFilterSet

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        # Debug N+1 (remove in production)
        print("TOTAL QUERIES:", len(connection.queries))

        return response

    def create(self, request, *args, **kwargs):
        """
        UPSERT behavior:
        - If WarehouseDelivery for forecast exists → UPDATE
        - Otherwise → CREATE
        """
        serializer = BaseWarehouseDeliverySerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        forecast = serializer.validated_data["forecast"]

        instance = (
            WarehouseDelivery.objects.filter(forecast=forecast)
            .select_related(
                "delivered_by",
                "forecast",
            )
            .first()
        )

        if instance:
            # UPDATE
            update_serializer = BaseWarehouseDeliverySerializer(
                instance,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            update_serializer.is_valid(raise_exception=True)

            updated = update_serializer.save(
                delivered_by=request.user,
            )

            return Response(
                BaseWarehouseDeliverySerializer(
                    updated, context={"request": request}
                ).data,
                status=status.HTTP_200_OK,
            )

        # CREATE
        receipt = serializer.save(
            delivered_by=request.user,
        )

        return Response(
            BaseWarehouseDeliverySerializer(receipt, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
