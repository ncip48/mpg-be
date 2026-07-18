from __future__ import annotations
from services.verification.rest.qc_line_verification.filtersets import (
    QCLineVerificationFilterSet,
)

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from core.common.filter_date import apply_date_filter

from core.common.viewsets import BaseViewSet
from services.forecast.models.forecast import Forecast
from services.verification.models.qc_line_verification import QCLineVerification
from services.verification.rest.qc_line_verification.serializers import (
    BaseQCLineVerificationSerializer,
    QCLineVerificationSerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("QCLineVerificationViewSet",)


class QCLineVerificationViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Print Verification entries.
    Accessible only by superusers.
    """

    required_module_code = "verifikasi-qc-line"

    my_tags = ["QC Line Verification"]
    queryset = Forecast.objects.prefetch_related("qc_line_verifications")
    serializer_class = QCLineVerificationSerializer
    lookup_field = "subid"

    search_fields = ["forecast_number"]

    permission_map = {
        "list": ["verification.view_line"],
        "retrieve": ["verification.view_line"],
        "create": ["verification.verify_line"],
        "update": ["verification.verify_line"],
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

    filterset_class = QCLineVerificationFilterSet

    def create(self, request, *args, **kwargs):
        serializer = BaseQCLineVerificationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        forecast = serializer.validated_data["forecast"]

        # Check if record exists
        instance = QCLineVerification.objects.filter(forecast=forecast).first()

        if instance:
            # Update existing record
            update_serializer = BaseQCLineVerificationSerializer(
                instance, data=request.data, partial=True, context={"request": request}
            )
            update_serializer.is_valid(raise_exception=True)
            updated = update_serializer.save(checked_by=request.user)
            return Response(
                BaseQCLineVerificationSerializer(
                    updated, context={"request": request}
                ).data,
                status=status.HTTP_200_OK,
            )

        # Create new
        qc = serializer.save(checked_by=request.user)

        return Response(
            BaseQCLineVerificationSerializer(qc, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Get Forecast
        forecast = self.get_object()

        # Find QC Line Verification linked to this Forecast
        instance = QCLineVerification.objects.filter(forecast=forecast).first()
        if not instance:
            return Response(
                {"detail": "QC Line Verification not found for this forecast."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Use BaseQCLineVerificationSerializer for updating
        serializer = BaseQCLineVerificationSerializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        return Response(
            BaseQCLineVerificationSerializer(updated, context={"request": request}).data
        )
