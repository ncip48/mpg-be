from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.serializers import ForecastSerializer
from services.verification.models.print_verification import PrintVerification

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("PrintVerificationSerializer", "BasePrintVerificationSerializer")


class BasePrintVerificationSerializer(BaseModelSerializer):
    forecast = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Forecast.objects.all(),
        required=True,
        allow_null=False,
        write_only=True,
    )
    verified_by = UserSerializerSimple(read_only=True)

    class Meta:
        model = PrintVerification
        fields = (
            "subid",
            "forecast",
            "verified_by",
            "verified_at",
            "is_approved",
            "rejected_quantity",
            "rejection_note",
            "finished_at",
            "created",
            "updated",
        )

    def create(self, validated_data):
        forecast = validated_data.pop("forecast")
        return PrintVerification.objects.create(forecast=forecast, **validated_data)


class PrintVerificationSerializer(ForecastSerializer):
    print_verification = serializers.SerializerMethodField()

    class Meta:
        model = Forecast
        fields = ForecastSerializer.Meta.fields + [
            "print_verification",
        ]

    def get_print_verification(self, obj):
        try:
            print_verification = PrintVerification.objects.get(forecast=obj)
            return BasePrintVerificationSerializer(print_verification).data
        except PrintVerification.DoesNotExist:
            return None
