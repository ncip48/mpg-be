from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from rest_framework import status
from rest_framework.response import Response
from core.common.viewsets import BaseViewSet
from services.order.rest.order.serializers import (
    OrderCreateSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
)
from services.order.models import Order

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "OrderViewSet",
)

class OrderViewSet(BaseViewSet):
    required_perms = [
        "order.add_order",
        "order.change_order",
        "order.delete_order",
        "order.view_order",
    ]
    my_tags = ["Orders"]
    queryset = (
        Order.objects.select_related("customer", "invoice")
        .prefetch_related("items")
        .order_by("-created")
    )
    lookup_field = "subid"
    serializer_class = OrderListSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        invoice = serializer.save()

        # Use the same detail serializer for response
        response_serializer = OrderDetailSerializer(invoice.order)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
