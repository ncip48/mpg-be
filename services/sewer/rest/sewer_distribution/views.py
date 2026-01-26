from __future__ import annotations

from django.db import transaction
import logging
from typing import TYPE_CHECKING

from django.shortcuts import get_object_or_404

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

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
        "order__subid",
        "order_item__subid",
        "sewer_distributions__distributed_by__first_name",
        "sewer_distributions__sewer__name",
        "sewer_distributions__tracking_code",
    ]

    required_perms = [
        "sewer.add_sewer_distribution",
        "sewer.change_sewer_distribution",
        "sewer.delete_sewer_distribution",
        "sewer.view_sewer_distribution",
    ]

    filterset_class = SewerDistributionFilterSet

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
