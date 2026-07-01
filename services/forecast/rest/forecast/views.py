from __future__ import annotations
from services.forecast.rest.forecast.filtersets import ForecastFilterSet

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from django.utils.dateparse import parse_date

from core.common.viewsets import BaseViewSet
from services.forecast.models.forecast import Forecast
from services.forecast.rest.forecast.serializers import ForecastSerializer

from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("ForecastViewSet",)

def apply_date_filter(queryset, field_name, request):
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")

    filters = {}

    if start_date:
        filters[f"{field_name}__gte"] = parse_date(start_date)

    if end_date:
        filters[f"{field_name}__lte"] = parse_date(end_date)

    return queryset.filter(**filters)

class ForecastViewSet(BaseViewSet):
    required_module_code = "forecasting"
    """
    A viewset for viewing and editing Forecast entries.
    Accessible only by superusers.
    """

    my_tags = ["Forecasts"]
    queryset = Forecast.objects.all()
    serializer_class = ForecastSerializer
    lookup_field = "subid"

    search_fields = [
        "forecast_number",
        # SKU
        "order_item__product__sku",
        "order__order_forms__order_item__product__sku",
        "stock_items__product__sku",
        # Nama Konveksi
        "order__convection_name",
    ]

    filterset_class = ForecastFilterSet

    required_perms = [
        "forecast.add_forecast",
        "forecast.change_forecast",
        "forecast.delete_forecast",
        "forecast.view_forecast",
    ]

    @action(
        detail=False,
        methods=["get"],
        url_path="tracker",
        permission_classes=[IsAuthenticated],
    )
    def tracker(self, request, *args, **kwargs):
        """
        Tracker endpoint:
        Same behavior as list(), but only requires authentication.
        """

        queryset = self.filter_queryset(self.get_queryset())
        
        queryset = apply_date_filter(queryset, "date_forecast", request)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
