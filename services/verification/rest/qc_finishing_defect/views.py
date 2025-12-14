from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import status
from rest_framework.response import Response

from core.common.viewsets import BaseViewSet
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.filtersets import ForecastFilterSet
from services.verification.models.qc_finishing_defect import QCFinishingDefect
from services.verification.rest.qc_finishing_defect.serializers import (
    BaseQCFinishingDefectSerializer,
    QCFinishingDefectSerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("QCFinishingDefectViewSet",)


class QCFinishingDefectViewSet(BaseViewSet):
    """
    A viewset for viewing and editing QC Finishing Defect entries.
    Accessible only by authorized users.
    """

    my_tags = ["QC Finishing Defect"]
    queryset = Forecast.objects.all()
    serializer_class = QCFinishingDefectSerializer
    lookup_field = "subid"

    search_fields = [
        "order__subid",
        "order_item__subid",
        "qc_finishing_defect__checked_by__first_name",
    ]

    required_perms = [
        "verification.add_qc_finishing_defect",
        "verification.change_qc_finishing_defect",
        "verification.delete_qc_finishing_defect",
        "verification.view_qc_finishing_defect",
    ]

    filterset_class = ForecastFilterSet

    def create(self, request, *args, **kwargs):
        serializer = BaseQCFinishingDefectSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        forecast = serializer.validated_data["forecast"]

        # OneToOne → check existing defect record
        instance = QCFinishingDefect.objects.filter(forecast=forecast).first()

        if instance:
            # Update existing defect
            update_serializer = BaseQCFinishingDefectSerializer(
                instance,
                data=request.data,
                partial=True,
                context={"request": request},
            )
            update_serializer.is_valid(raise_exception=True)

            updated = update_serializer.save(checked_by=request.user)

            return Response(
                BaseQCFinishingDefectSerializer(
                    updated, context={"request": request}
                ).data,
                status=status.HTTP_200_OK,
            )

        # Create new defect record
        defect = serializer.save(checked_by=request.user)

        return Response(
            BaseQCFinishingDefectSerializer(defect, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        # Forecast subid comes from URL
        forecast = self.get_object()  # this returns Forecast, NOT defect

        defect = QCFinishingDefect.objects.filter(forecast=forecast).first()

        print(defect)

        if not defect:
            return Response(
                {"detail": "QC Finishing Defect not found for this forecast."},
                status=status.HTTP_404_NOT_FOUND,
            )

        defect.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
