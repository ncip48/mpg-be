from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.serializers import ForecastSerializer
from services.verification.models.qc_finishing import QCFinishing

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("QCFinishingSerializer", "BaseQCFinishingSerializer")


class BaseQCFinishingSerializer(BaseModelSerializer):
    forecast = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Forecast.objects.all(),
        required=True,
        allow_null=False,
        write_only=True,
    )

    class Meta:
        model = QCFinishing
        fields = (
            "subid",
            "forecast",
            "verified_by",
            "received_quantity",
            "realization_status",
            "verification_code",
            "notes",
            "created",
            "updated",
        )
        read_only_fields = (
            "verification_code",
            "created",
            "updated",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # nested user info
        data["verified_by"] = (
            UserSerializerSimple(instance.verified_by).data
            if instance.verified_by
            else None
        )

        return data

    def create(self, validated_data):
        forecast = validated_data.pop("forecast")
        return QCFinishing.objects.create(forecast=forecast, **validated_data)


class QCFinishingSerializer(ForecastSerializer):
    qc_finishing = serializers.SerializerMethodField()

    class Meta:
        model = Forecast
        fields = ForecastSerializer.Meta.fields + [
            "qc_finishing",
        ]

    def get_qc_finishing(self, obj):
        try:
            qc = obj.qc_finishing  # OneToOne → direct access
            return BaseQCFinishingSerializer(qc).data
        except QCFinishing.DoesNotExist:
            return None
