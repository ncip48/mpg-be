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
from services.verification.models.print_verification import PrintVerification

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("SewerDistributionSerializer", "BaseSewerDistributionSerializer")


class BaseSewerDistributionSerializer(BaseModelSerializer):
    forecast = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Forecast.objects.all(),
        required=True,
        allow_null=False,
        write_only=True,
    )
    sewer = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Sewer.objects.all(),
        required=True,
        allow_null=False,
        write_only=True,
    )

    class Meta:
        model = SewerDistribution
        fields = (
            "subid",
            "forecast",
            "distributed_by",
            "sewer",
            "quantity",
            "accessories",
            "notes",
            "tracking_code",
            "is_full",
            "created",
            "updated",
        )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["distributed_by"] = UserSerializerSimple(instance.distributed_by).data
        data["sewer"] = SewerSerializer(instance.sewer).data
        return data

    def create(self, validated_data):
        forecast = validated_data.pop("forecast")
        sewer = validated_data.pop("sewer")
        return SewerDistribution.objects.create(
            forecast=forecast, sewer=sewer, **validated_data
        )


class SewerDistributionSerializer(ForecastSerializer):
    sewer_distribution = serializers.SerializerMethodField()

    class Meta:
        model = Forecast
        fields = ForecastSerializer.Meta.fields + [
            "sewer_distribution",
        ]

    def get_sewer_distribution(self, obj):
        try:
            sewer_distribution = SewerDistribution.objects.get(forecast=obj)
            return BaseSewerDistributionSerializer(sewer_distribution).data
        except SewerDistribution.DoesNotExist:
            return None
