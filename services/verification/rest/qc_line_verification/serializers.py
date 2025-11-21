from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import serializers

from core.common.serializers import BaseModelSerializer
from services.account.rest.user.serializers import UserSerializerSimple
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.serializers import ForecastSerializer
from services.verification.models.qc_line_verification import QCLineVerification

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("QCLineVerificationSerializer", "BaseQCLineVerificationSerializer")


class BaseQCLineVerificationSerializer(BaseModelSerializer):
    forecast = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Forecast.objects.all(),
        required=True,
        allow_null=False,
        write_only=True,
    )
    checked_by = UserSerializerSimple(read_only=True)

    class Meta:
        model = QCLineVerification
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

        return data

    def create(self, validated_data):
        forecast = validated_data.pop("forecast")
        return QCLineVerification.objects.create(forecast=forecast, **validated_data)


class QCLineVerificationSerializer(ForecastSerializer):
    qc_line_verification = serializers.SerializerMethodField()

    class Meta:
        model = Forecast
        fields = ForecastSerializer.Meta.fields + [
            "qc_line_verification",
        ]

    def get_qc_line_verification(self, obj):
        request = self.context.get("request")
        try:
            qc_line_verification = QCLineVerification.objects.get(forecast=obj)
            return BaseQCLineVerificationSerializer(
                qc_line_verification, context={"request": request}
            ).data
        except QCLineVerification.DoesNotExist:
            return None
