from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from django.db import transaction

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
