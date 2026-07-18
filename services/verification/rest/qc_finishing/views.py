from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from django.db import transaction
from core.common.filter_date import apply_forecast_date_filter, apply_estimate_sent_date_filter

from services.verification.models.qc_finishing_defect import QCFinishingDefect

from core.common.viewsets import BaseViewSet
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.filtersets import ForecastFilterSet
from services.verification.models.qc_finishing import QCFinishing
from services.verification.rest.qc_finishing.filtersets import QCFinishingFilterSet
from services.verification.rest.qc_finishing.serializers import (
    BaseQCFinishingSerializer,
    QCFinishingSerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("QCFinishingViewSet",)


class QCFinishingViewSet(BaseViewSet):
    """
    A viewset for viewing and editing QC Finishing verification entries.
    Accessible only by authorized users.
    """

    required_module_code = "verifikasi-qc-finishing"

    my_tags = ["QC Finishing"]
    queryset = Forecast.objects.prefetch_related("qc_finishings")
    serializer_class = QCFinishingSerializer
    lookup_field = "subid"

    search_fields = [
        "forecast_number",
        "qc_finishings__verification_code",
        "sewer_distributions__tracking_code",
    ]

    permission_map = {
        "list": ["verification.view_finishing"],
        "retrieve": ["verification.view_finishing"],
        "create": ["verification.verify_finishing"],
    }

    def get_required_perms(self):
        return self.permission_map.get(self.action, [])

    filterset_class = ForecastFilterSet
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = apply_forecast_date_filter(queryset, "date_forecast", self.request)
        queryset = apply_estimate_sent_date_filter(queryset, "estimate_sent", self.request)

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

    def create(self, request, *args, **kwargs):
        serializer = BaseQCFinishingSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        forecast = serializer.validated_data["forecast"]

        with transaction.atomic():
            # Remove defect record if it exists
            QCFinishingDefect.objects.filter(forecast=forecast).delete()

            # Update existing QC Finishing if present
            instance = QCFinishing.objects.filter(forecast=forecast).first()

            if instance:
                update_serializer = BaseQCFinishingSerializer(
                    instance,
                    data=request.data,
                    partial=True,
                    context={"request": request},
                )
                update_serializer.is_valid(raise_exception=True)

                qc_finishing = update_serializer.save(
                    verified_by=request.user,
                )

                return Response(
                    BaseQCFinishingSerializer(
                        qc_finishing,
                        context={"request": request},
                    ).data,
                    status=status.HTTP_200_OK,
                )

            # Create new QC Finishing
            qc_finishing = serializer.save(
                verified_by=request.user,
            )

        return Response(
            BaseQCFinishingSerializer(
                qc_finishing,
                context={"request": request},
            ).data,
            status=status.HTTP_201_CREATED,
        )
