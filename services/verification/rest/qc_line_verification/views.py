from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

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

    my_tags = ["QC Line Verification"]
    queryset = Forecast.objects.all()
    serializer_class = QCLineVerificationSerializer
    lookup_field = "subid"

    search_fields = [
        "forecast__order__subid",
        "forecast__order_item__subid",
        "verified_by__first_name",
    ]

    required_perms = [
        "print_verification.add_print_verification",
        "print_verification.change_print_verification",
        "print_verification.delete_print_verification",
        "print_verification.view_print_verification",
    ]

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
