from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from rest_framework import status
from rest_framework.response import Response

from core.common.viewsets import BaseViewSet
from services.order.models.order_item import OrderItem
from services.order.rest.order_form.serializers import OrderFormSerializer
from services.order.rest.order_item.serializers import OrderItemSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("OrderItemViewSet",)


class OrderItemViewSet(BaseViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    lookup_field = "subid"
    ordering_fields = ["pk"]
    ordering = ["-pk"]

    search_fields = ["product__name", "deposit__order__customer__name"]

    required_perms = [
        "order.add_orderform",
        "order.change_orderform",
        "order.delete_orderform",
        "order.view_orderform",
    ]

    my_tags = ["Order Forms"]

    serializer_map = {
        # Allow using same serializer for create/update
        "create": OrderFormSerializer,
        "partial_update": OrderFormSerializer,
        "update": OrderFormSerializer,
    }

    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def order_form(self, request, *args, **kwargs):
        order_item = self.get_object()  # get OrderItem by subid from URL
        print("omke")

        order_form = order_item.order_forms.first()

        if not order_form:
            return Response(
                {"detail": "Order form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderFormSerializer(order_form)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_order_form(self, request, *args, **kwargs):
        order_item = self.get_object()  # lookup OrderItem by subid

        # Check if an OrderForm already exists for this OrderItem
        if order_item.order_forms.exists():
            return Response(
                {"detail": "Order form already exists for this order item."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Prepare incoming data
        data = request.data.copy()
        data["order_item"] = order_item.subid  # SlugRelatedField expects subid

        serializer = OrderFormSerializer(data=data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update_order_form(self, request, *args, **kwargs):
        """Full update (PUT) for the order form attached to this OrderItem."""
        order_item = self.get_object()
        order_form = order_item.order_forms.first()

        if not order_form:
            return Response(
                {"detail": "Order form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()
        data["order_item"] = order_item.subid  # prevent changing FK

        serializer = OrderFormSerializer(
            order_form,
            data=data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update_order_form(self, request, *args, **kwargs):
        """Partial update (PATCH) for the order form."""
        order_item = self.get_object()
        order_form = order_item.order_forms.first()

        if not order_form:
            return Response(
                {"detail": "Order form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()
        data["order_item"] = order_item.subid  # ensure FK cannot be modified

        serializer = OrderFormSerializer(
            order_form,
            data=data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete_order_form(self, request, *args, **kwargs):
        """Delete the order form for this OrderItem."""
        order_item = self.get_object()
        order_form = order_item.order_forms.first()

        if not order_form:
            return Response(
                {"detail": "Order form not found"}, status=status.HTTP_404_NOT_FOUND
            )

        order_form.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
