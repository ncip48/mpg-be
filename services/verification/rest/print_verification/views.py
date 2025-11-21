from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.response import Response

from core.common.viewsets import BaseViewSet
from services.forecast.models.forecast import Forecast
from services.verification.models.print_verification import PrintVerification
from services.verification.rest.print_verification.serializers import (
    BasePrintVerificationSerializer,
    PrintVerificationSerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("PrintVerificationViewSet",)


class PrintVerificationViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Print Verification entries.
    Accessible only by superusers.
    """

    my_tags = ["Print Verification"]
    queryset = Forecast.objects.all()
    serializer_class = PrintVerificationSerializer
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
        serializer = BasePrintVerificationSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        forecast = serializer.validated_data["forecast"]

        # Check if record exists
        instance = PrintVerification.objects.filter(forecast=forecast).first()

        if instance:
            # Update existing record
            update_serializer = BasePrintVerificationSerializer(
                instance, data=request.data, partial=True, context={"request": request}
            )
            update_serializer.is_valid(raise_exception=True)
            updated = update_serializer.save(verified_by=request.user)
            return Response(
                BasePrintVerificationSerializer(
                    updated, context={"request": request}
                ).data,
                status=status.HTTP_200_OK,
            )

        # Create new
        print_verification = serializer.save(verified_by=request.user)

        return Response(
            BasePrintVerificationSerializer(
                print_verification, context={"request": request}
            ).data,
            status=status.HTTP_201_CREATED,
        )
