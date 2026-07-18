from __future__ import annotations
from services.verification.models.qc_press_verification import QCPressVerification

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from core.common.filter_date import apply_date_filter

from core.common.viewsets import BaseViewSet
from services.forecast.models.forecast import Forecast
from services.verification.rest.qc_press_verification.filtersets import QCPressVerificationFilterSet
from services.verification.rest.qc_press_verification.serializers import (
    BaseQCPressVerificationSerializer,
    QCPressVerificationSerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("QCPressVerificationViewSet",)


class QCPressVerificationViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Print Verification entries.
    Accessible only by superusers.
    """

    required_module_code = "verifikasi-qc-press"

    my_tags = ["QC Press Verification"]
    queryset = Forecast.objects.prefetch_related("qc_press_verifications")
    serializer_class = QCPressVerificationSerializer
    lookup_field = "subid"

    search_fields = ["forecast_number"]

    permission_map = {
        "list": ["verification.view_press"],
        "retrieve": ["verification.view_press"],
        "create": ["verification.verify_press"],
        "update": ["verification.verify_press"],
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

    filterset_class = QCPressVerificationFilterSet

    def create(self, request, *args, **kwargs):
        serializer = BaseQCPressVerificationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        forecast = serializer.validated_data["forecast"]

        # Check if record exists
        instance = QCPressVerification.objects.filter(forecast=forecast).first()

        if instance:
            # Update existing record
            update_serializer = BaseQCPressVerificationSerializer(
                instance, data=request.data, partial=True, context={"request": request}
            )
            update_serializer.is_valid(raise_exception=True)
            updated = update_serializer.save(checked_by=request.user)
            return Response(
                BaseQCPressVerificationSerializer(
                    updated, context={"request": request}
                ).data,
                status=status.HTTP_200_OK,
            )

        # Create new
        qc = serializer.save(checked_by=request.user)

        return Response(
            BaseQCPressVerificationSerializer(qc, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Get Forecast
        forecast = self.get_object()

        # Find QC Press Verification linked to this Forecast
        instance = QCPressVerification.objects.filter(forecast=forecast).first()
        if not instance:
            return Response(
                {"detail": "QC Press Verification not found for this forecast."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Use BaseQCPressVerificationSerializer for updating
        serializer = BaseQCPressVerificationSerializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        return Response(
            BaseQCPressVerificationSerializer(updated, context={"request": request}).data
        )
