from __future__ import annotations


from services.verification.rest.print_verification.filtersets import (
    PrintVerificationFilterSet,
)

import logging
from typing import TYPE_CHECKING

from django.db import connection
from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from core.common.filter_date import apply_date_filter

from core.common.viewsets import BaseViewSet
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.filtersets import ForecastFilterSet
from services.verification.models.print_verification import PrintVerification
from services.verification.rest.print_verification.serializers import (
    BasePrintVerificationSerializer,
    PrintVerificationSerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("PrintVerificationViewSet",)


class PrintVerificationViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Print Verification entries.
    Accessible only by superusers.
    """

    required_module_code = "verifikasi-print"

    my_tags = ["Print Verification"]
    queryset = Forecast.objects.select_related(
        "print_verifications",
        "print_verifications__verified_by",
        "order",
        "printer",
    ).prefetch_related(
        "order_item",
    )
    serializer_class = PrintVerificationSerializer
    lookup_field = "subid"

    search_fields = ["forecast_number"]

    filterset_class = PrintVerificationFilterSet

    permission_map = {
        "list": ["verification.view_print"],
        "retrieve": ["verification.view_print"],
        "create": ["verification.verify_print"],
    }
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = apply_date_filter(queryset, "date_forecast", self.request)

        # 🚀 PREVENT N+1: Fetch all related foreign keys in one go
        queryset = queryset.select_related(
            "order",
            "order__customer",
            "order_item",
            "order_item__order",
            "order_item__order__customer",
            "order_item__product",
            "order_item__product__printer",
            "order_item__fabric_type",
            "order_item__deposit",
        )

        # 🚀 PREVENT N+1: Fetch reverse relations (like StockItem and OrderForm)
        # Note: Change "stock_items" and "order_forms" if you defined custom related_names on those models.
        queryset = queryset.prefetch_related(
            "stock_items__product__printer",
            "stock_items__fabric_type",
            "order__order_forms", 
            "order__order_forms__printer", # <-- ADD THIS LINE
        )

        return queryset

    def get_required_perms(self):
        return self.permission_map.get(self.action, [])

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        print("TOTAL QUERIES:", len(connection.queries))

        return response

    def create(self, request, *args, **kwargs):
        serializer = BasePrintVerificationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        forecast = serializer.validated_data["forecast"]

        # Check if record exists
        instance = PrintVerification.objects.filter(forecast=forecast).first()

        if instance:
            # Update existing record
            update_serializer = BasePrintVerificationSerializer(
                instance, data=request.data, partial=True, context={"request": request}
            )
            update_serializer.is_valid(raise_exception=True)
            updated = update_serializer.save(verified_by=request.user)
            return Response(
                BasePrintVerificationSerializer(
                    updated, context={"request": request}
                ).data,
                status=status.HTTP_200_OK,
            )

        # Create new
        print_verification = serializer.save(verified_by=request.user)

        return Response(
            BasePrintVerificationSerializer(
                print_verification, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )
