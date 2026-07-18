from __future__ import annotations
from services.forecast.models.stock_item import StockItem
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
from django.db.models import (
    Case,
    When,
    F,
    Value,
    CharField,
    OuterRef,
    Subquery,
)
from django.db.models.functions import Concat

from services.order.models.order_form import OrderForm

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
    
    stock_product = StockItem.objects.filter(
        forecast=OuterRef("pk")
    ).values("product__name")[:1]

    order_form = OrderForm.objects.filter(
        order=OuterRef("order")
    )
    
    stock_sku = StockItem.objects.filter(
        forecast=OuterRef("pk")
    ).values("product__sku")[:1]

    queryset = Forecast.objects.all().annotate(
        convection_name=Case(
            When(is_stock=True, then=Value("STOK JB")),
            default=F("order_item__order__convection_name"),
            output_field=CharField(),
        ),
        product_name=Case(
            When(
                is_stock=True,
                then=Subquery(stock_product),
            ),
            When(
                order_item__isnull=False,
                then=F("order_item__product__name"),
            ),
            default=Concat(
                Subquery(order_form.values("marketplace")[:1]),
                Value(" "),
                # email_send_date formatting here is the problem
                Value("Sesi "),
                Subquery(order_form.values("session")[:1]),
                output_field=CharField(),
            ),
            output_field=CharField(),
        ),
        sku_search=Case(
            When(
                is_stock=True,
                then=Subquery(stock_sku),
            ),
            default=Value("Custom"),
            output_field=CharField(),
        )
    )
    serializer_class = ForecastSerializer
    lookup_field = "subid"

    search_fields = [
        "forecast_number",
        # SKU
        "sku_search",
        "convection_name",
        "product_name",
    ]

    filterset_class = ForecastFilterSet

    required_perms = [
        "forecast.add_forecast",
        "forecast.change_forecast",
        "forecast.delete_forecast",
        "forecast.view_forecast",
    ]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = apply_date_filter(queryset, "date", self.request)

        # 🚀 PREVENT N+1: Fetch all related foreign keys in one go
        queryset = queryset.select_related(
            "order",
            "order__customer",
            "order_item",
            "order_item__order",
            "order_item__order__customer",
            "order_item__product",
            "order_item__product__printer",
            "order_item__fabric_type",
            "order_item__deposit",
        )

        # 🚀 PREVENT N+1: Fetch reverse relations (like StockItem and OrderForm)
        # Note: Change "stock_items" and "order_forms" if you defined custom related_names on those models.
        queryset = queryset.prefetch_related(
            "stock_items__product__printer",
            "stock_items__fabric_type",
            "order__order_forms", 
            "order__order_forms__printer", # <-- ADD THIS LINE
        )

        return queryset

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
