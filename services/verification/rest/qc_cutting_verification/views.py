from __future__ import annotations
from services.verification.rest.qc_cutting_verification.filtersets import (
    QCCuttingVerificationFilterSet,
)

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from core.common.viewsets import BaseViewSet
from services.forecast.models.forecast import Forecast
from services.verification.models import QCCuttingVerification
from services.verification.rest.qc_cutting_verification.serializers import (
    BaseQCCuttingVerificationSerializer,
    QCCuttingVerificationSerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("QCCuttingVerificationViewSet",)


class QCCuttingVerificationViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Print Verification entries.
    Accessible only by superusers.
    """

    my_tags = ["QC Cutting Verification"]
    queryset = Forecast.objects.prefetch_related("qc_cutting_verifications")
    serializer_class = QCCuttingVerificationSerializer
    lookup_field = "subid"

    search_fields = ["forecast_number"]

    required_perms = [
        "print_verification.add_print_verification",
        "print_verification.change_print_verification",
        "print_verification.delete_print_verification",
        "print_verification.view_print_verification",
    ]

    filterset_class = QCCuttingVerificationFilterSet

    def create(self, request, *args, **kwargs):
        serializer = BaseQCCuttingVerificationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        forecast = serializer.validated_data["forecast"]

        # Check if record exists
        instance = QCCuttingVerification.objects.filter(forecast=forecast).first()

        if instance:
            # Update existing record
            update_serializer = BaseQCCuttingVerificationSerializer(
                instance, data=request.data, partial=True, context={"request": request}
            )
            update_serializer.is_valid(raise_exception=True)
            updated = update_serializer.save(checked_by=request.user)
            return Response(
                BaseQCCuttingVerificationSerializer(
                    updated, context={"request": request}
                ).data,
                status=status.HTTP_200_OK,
            )

        # Create new
        qc = serializer.save(checked_by=request.user)

        return Response(
            BaseQCCuttingVerificationSerializer(qc, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # Get Forecast
        forecast = self.get_object()

        # Find QC Line Verification linked to this Forecast
        instance = QCCuttingVerification.objects.filter(forecast=forecast).first()
        if not instance:
            return Response(
                {"detail": "QC Cutting Verification not found for this forecast."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Use BaseQCLineVerificationSerializer for updating
        serializer = BaseQCCuttingVerificationSerializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        updated = serializer.save()

        return Response(
            BaseQCCuttingVerificationSerializer(
                updated, context={"request": request}
            ).data
        )
