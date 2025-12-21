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
from services.sewer.models.sewer_distribution import SewerDistribution
from services.sewer.rest.sewer_distribution.serializers import (
    BaseSewerDistributionSerializer,
    SewerDistributionSerializer,
)
from services.verification.models.print_verification import PrintVerification
from services.verification.rest.print_verification.serializers import (
    BasePrintVerificationSerializer,
    PrintVerificationSerializer,
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
        Forecast.objects.prefetch_related("sewer_distributions")
        .filter(sewer_distributions__isnull=False)
        .distinct()
    )
    serializer_class = SewerDistributionSerializer
    lookup_field = "subid"

    search_fields = [
        "order__subid",
        "order_item__subid",
        "sewer_distributions__distributed_by__first_name",
    ]

    required_perms = [
        "sewer.add_sewer_distribution",
        "sewer.change_sewer_distribution",
        "sewer.delete_sewer_distribution",
        "sewer.view_sewer_distribution",
    ]

    filterset_class = ForecastFilterSet

    def create(self, request, *args, **kwargs):
        serializer = BaseSewerDistributionSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        forecast = serializer.validated_data["forecast"]

        # Check if record exists
        instance = SewerDistribution.objects.filter(forecast=forecast).first()

        if instance:
            # Update existing record
            update_serializer = BaseSewerDistributionSerializer(
                instance, data=request.data, partial=True, context={"request": request}
            )
            update_serializer.is_valid(raise_exception=True)
            updated = update_serializer.save(distributed_by=request.user)
            return Response(
                BaseSewerDistributionSerializer(
                    updated, context={"request": request}
                ).data,
                status=status.HTTP_200_OK,
            )

        # Create new
        print_verification = serializer.save(distributed_by=request.user)

        return Response(
            BaseSewerDistributionSerializer(
                print_verification, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )
