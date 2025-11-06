from __future__ import annotations
from decimal import Decimal
from io import BytesIO
import os
from typing import TYPE_CHECKING
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import logging
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from core.common.viewsets import BaseViewSet
from services.order.models.invoice import Invoice
from services.order.rest.order.serializers import (
    OrderCreateSerializer,
    OrderKonveksiListSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    OrderMarketplaceListSerializer,
)
from services.order.models import Order

# Report lab
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
)
from django.http import HttpResponse

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("OrderViewSet",)


class OrderViewSet(BaseViewSet):
    required_perms = [
        "order.can_add_deposit",
        "order.can_change_deposit",
        "order.can_delete_deposit",
        "order.can_view_deposit",
        "order.can_add_order_marketplace",
        "order.can_change_order_marketplace",
        "order.can_delete_order_marketplace",
        "order.can_view_order_marketplace",
    ]
    my_tags = ["Orders"]
    queryset = (
        Order.objects.select_related("customer", "invoice")
        .prefetch_related("items")
        .order_by("-created")
    )
    lookup_field = "subid"
    serializer_class = OrderListSerializer
    filterset_fields = [
        "order_type",
        "priority_status",
        "status",
        "marketplace",
        "order_choice",
    ]
    search_fields = [
        "order_number",
        "customer__name",
        "invoice__invoice_no",
        "user_name",
    ]
    serializer_map = {
        "create": OrderCreateSerializer,
        "konveksi": OrderKonveksiListSerializer,
        "marketplace": OrderMarketplaceListSerializer,
        "partial_update": OrderCreateSerializer,
        "update": OrderCreateSerializer,
    }

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the current action.
        Defaults to `serializer_class` if no match in `serializer_map`.
        """
        # Handle "list" with query param same as before
        if (
            self.action == "list"
            and self.request.query_params.get("order_type") == "konveksi"
        ):
            serializer = self.serializer_map.get("konveksi", None)
            if serializer is not None:
                return serializer

        if (
            self.action == "list"
            and self.request.query_params.get("order_type") == "marketplace"
        ):
            serializer = self.serializer_map.get("marketplace", None)
            if serializer is not None:
                return serializer

        if self.action == "retrieve":
            obj = self.get_object()
            if hasattr(obj, "order_type"):
                if obj.order_type == "konveksi":
                    serializer = self.serializer_map.get("konveksi", None)
                    if serializer is not None:
                        return serializer
                elif obj.order_type == "marketplace":
                    serializer = self.serializer_map.get("marketplace", None)
                    if serializer is not None:
                        return serializer

        return self.serializer_map.get(self.action, self.serializer_class)

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Use the same detail serializer for response
        response_serializer = OrderDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Handle full update (PUT)
        """
        instance = self.get_object()
        serializer = OrderCreateSerializer(
            instance, data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        response_serializer = OrderDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """
        Handle partial update (PATCH)
        """
        instance = self.get_object()
        serializer = OrderCreateSerializer(
            instance, data=request.data, partial=True, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        response_serializer = OrderDetailSerializer(order)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
