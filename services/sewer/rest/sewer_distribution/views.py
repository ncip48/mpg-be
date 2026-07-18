from __future__ import annotations

from django.db import transaction
import logging
from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response
from core.common.filter_date import apply_forecast_date_filter, apply_sewer_distribution_date_filter

from core.common.viewsets import BaseViewSet
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.filtersets import ForecastFilterSet
from services.sewer.models.sewer_distribution import SewerDistribution
from services.sewer.rest.sewer_distribution.filtersets import SewerDistributionFilterSet
from services.sewer.rest.sewer_distribution.serializers import (
    BaseSewerDistributionSerializer,
    SewerDistributionSerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("SewerDistributionViewSet",)


class SewerDistributionViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Sewer Distribution entries.
    Accessible only by superusers.
    """

    required_module_code = "pembagian-penjahit"

    my_tags = ["Sewer Distribution"]
    queryset = (
        Forecast.objects.prefetch_related(
            "sewer_distributions", "qc_finishings", "qc_finishing_defects"
        )
        .filter(sewer_distributions__isnull=False)
        .distinct()
    )
    serializer_class = SewerDistributionSerializer
    lookup_field = "subid"

    search_fields = [
        "forecast_number",
        "order__subid",
        "order_item__subid",
        "sewer_distributions__distributed_by__first_name",
        "sewer_distributions__sewer__name",
        "sewer_distributions__tracking_code",
    ]

    permission_map = {
        "list": ["sewer.view_sewer_distribution"],
        "retrieve": ["sewer.view_sewer_distribution"],
        "create": ["verification.sewer_distribution"],
        "update": ["sewer.change_sewer_distribution"],
        "delete": ["sewer.delete_sewer_distribution"],
    }

    def get_required_perms(self):
        return self.permission_map.get(self.action, [])

    filterset_class = SewerDistributionFilterSet
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = apply_forecast_date_filter(queryset, "date_forecast", self.request)
        queryset = apply_sewer_distribution_date_filter(queryset, "sewer_distributions__created", self.request)

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
        forecast = get_object_or_404(Forecast, subid=request.data["forecast"])
        sewers_data = request.data.get("sewers", [])

        with transaction.atomic():
            # 1️⃣ REMOVE ALL existing distributions for this forecast
            SewerDistribution.objects.filter(forecast=forecast).delete()

            created = []

            # 2️⃣ INSERT new ones
            for item in sewers_data:
                serializer = BaseSewerDistributionSerializer(
                    data={**item, "forecast": forecast.subid},
                    context={"request": request},
                )
                serializer.is_valid(raise_exception=True)
                created.append(serializer.save(distributed_by=request.user))

        return Response(
            BaseSewerDistributionSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED,
        )
