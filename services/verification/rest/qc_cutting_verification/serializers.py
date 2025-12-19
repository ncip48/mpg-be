from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.serializers import ForecastSerializer
from services.sewer.models.sewer_distribution import SewerDistribution
from services.sewer.rest.sewer.serializers import SewerSerializer
from services.verification.models import QCCuttingVerification

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("QCCuttingVerificationSerializer", "BaseQCCuttingVerificationSerializer")


class BaseQCCuttingVerificationSerializer(BaseModelSerializer):
    forecast = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Forecast.objects.all(),
        required=True,
        allow_null=False,
        write_only=True,
    )

    defect_area = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = QCCuttingVerification
        fields = (
            "subid",
            "forecast",
            "checked_by",
            "verified_at",
            "is_approved",
            "rejected_quantity",
            "defect_area",
            "defect_note",
            "defect_image",
            "created",
            "updated",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get("request")  # <── get the request

        if instance.defect_image:
            if request:
                data["defect_image"] = request.build_absolute_uri(
                    instance.defect_image.url
                )
            else:
                # fallback relative path
                data["defect_image"] = instance.defect_image.url
        else:
            data["defect_image"] = None

        data["checked_by"] = UserSerializerSimple(instance.checked_by).data

        return data

    def create(self, validated_data):
        forecast = validated_data.pop("forecast")

        return QCCuttingVerification.objects.create(
            forecast=forecast,
            **validated_data,
        )


class QCCuttingVerificationSerializer(ForecastSerializer):
    qc_cutting_verification = serializers.SerializerMethodField()
    sewer = serializers.SerializerMethodField()

    class Meta:
        model = Forecast
        fields = ForecastSerializer.Meta.fields + [
            "qc_cutting_verification",
            "sewer",
        ]

    def get_qc_cutting_verification(self, obj):
        request = self.context.get("request")
        try:
            qc_cutting_verification = obj.qc_cutting_verifications
            return BaseQCCuttingVerificationSerializer(
                qc_cutting_verification, context={"request": request}
            ).data
        except QCCuttingVerification.DoesNotExist:
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
