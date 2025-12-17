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
from services.warehouse.models import WarehouseReceipt
from services.warehouse.rest.warehouse_receipt.serializers import (
    BaseWarehouseReceiptSerializer,
    WarehouseReceiptSerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("WarehouseReceiptViewSet",)


class WarehouseReceiptViewSet(BaseViewSet):
    """
    ViewSet for Warehouse Receipt (QC Finishing Gudang).
    One Forecast can have only ONE WarehouseReceipt.
    """

    my_tags = ["Warehouse Receipt"]

    queryset = Forecast.objects.select_related(
        "warehouse_receipts",
        "warehouse_receipts__received_by",
        "order",
        "printer",
    ).prefetch_related(
        "order_item",
    )

    serializer_class = WarehouseReceiptSerializer
    lookup_field = "subid"

    search_fields = [
        "order__subid",
        "order_item__subid",
        "warehouse_receipts__received_by__first_name",
    ]

    required_perms = [
        "warehouse.add_warehouse_receipt",
        "warehouse.change_warehouse_receipt",
        "warehouse.delete_warehouse_receipt",
        "warehouse.view_warehouse_receipt",
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
        - If WarehouseReceipt for forecast exists → UPDATE
        - Otherwise → CREATE
        """
        serializer = BaseWarehouseReceiptSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        forecast = serializer.validated_data["forecast"]

        instance = (
            WarehouseReceipt.objects.filter(forecast=forecast)
            .select_related(
                "received_by",
                "forecast",
            )
            .first()
        )

        if instance:
            # UPDATE
            update_serializer = BaseWarehouseReceiptSerializer(
                instance,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            update_serializer.is_valid(raise_exception=True)

            updated = update_serializer.save(
                received_by=request.user,
            )

            return Response(
                BaseWarehouseReceiptSerializer(
                    updated, context={"request": request}
                ).data,
                status=status.HTTP_200_OK,
            )

        # CREATE
        receipt = serializer.save(
            received_by=request.user,
        )

        return Response(
            BaseWarehouseReceiptSerializer(receipt, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
