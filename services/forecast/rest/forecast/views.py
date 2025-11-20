from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from core.common.viewsets import BaseViewSet
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.serializers import ForecastSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("ForecastViewSet",)


class ForecastViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Forecast entries.
    Accessible only by superusers.
    """

    my_tags = ["Forecasts"]
    queryset = Forecast.objects.all()
    serializer_class = ForecastSerializer
    lookup_field = "subid"

    search_fields = [
        "order__subid",
        "order_item__subid",
        "created_by__email",
    ]

    required_perms = [
        "forecast.add_forecast",
        "forecast.change_forecast",
        "forecast.delete_forecast",
        "forecast.view_forecast",
    ]
