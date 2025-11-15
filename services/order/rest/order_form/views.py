from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.common.viewsets import BaseViewSet
from services.order.models.order_form import OrderForm
from services.order.rest.order_form.serializers import OrderFormSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("OrderFormViewSet",)


class OrderFormViewSet(BaseViewSet):
    """
    ViewSet for handling Order Forms.
    """

    queryset = OrderForm.objects.select_related("order_item")
    serializer_class = OrderFormSerializer
    lookup_field = "subid"

    search_fields = ["team_name", "form_type"]

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
