from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.serializers import ForecastSerializer
from services.sewer.models.sewer import Sewer
from services.sewer.models.sewer_distribution import SewerDistribution
from services.sewer.rest.sewer.serializers import SewerSerializer
from services.verification.models.qc_finishing_defect import QCFinishingDefect

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "BaseQCFinishingDefectSerializer",
    "QCFinishingDefectSerializer",
)


class BaseQCFinishingDefectSerializer(BaseModelSerializer):
    forecast = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Forecast.objects.all(),
        required=True,
        allow_null=False,
        write_only=True,
    )

    class Meta:
        model = QCFinishingDefect
        fields = (
            "subid",
            "forecast",
            "checked_by",
            "quantity_rejected",
            "reason",
            "is_repaired",
            "created",
            "updated",
        )
        read_only_fields = (
            "created",
            "updated",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        data["checked_by"] = (
            UserSerializerSimple(instance.checked_by).data
            if instance.checked_by
            else None
        )

        return data

    def create(self, validated_data):
        forecast = validated_data.pop("forecast")
        return QCFinishingDefect.objects.create(
            forecast=forecast,
            **validated_data,
        )


class QCFinishingDefectSerializer(ForecastSerializer):
    qc_finishing_defect = serializers.SerializerMethodField()
    sewer = serializers.SerializerMethodField()
    tracking_code = serializers.SerializerMethodField()

    class Meta:
        model = Forecast
        fields = ForecastSerializer.Meta.fields + [
            "qc_finishing_defect",
            "sewer",
            "tracking_code",
        ]

    def get_qc_finishing_defect(self, obj):
        try:
            defect = obj.qc_finishing_defects  # OneToOne access
            return BaseQCFinishingDefectSerializer(defect).data
        except QCFinishingDefect.DoesNotExist:
            return None

    def get_sewer(self, obj):
        sewer_distribution = (
            SewerDistribution.objects.select_related("sewer")
            .filter(forecast=obj)
            .first()
        )

        if not sewer_distribution or not sewer_distribution.sewer:
            return None

        return SewerSerializer(sewer_distribution.sewer).data

    def get_tracking_code(self, obj):
        sw = SewerDistribution.objects.filter(forecast=obj).first()
        return sw.tracking_code if sw else None
