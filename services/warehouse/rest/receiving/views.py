from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from core.common.viewsets import BaseViewSet
from services.warehouse.models import Receiving
from services.warehouse.rest.receiving.serializers import ReceivingSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("ReceivingViewSet",)


class ReceivingViewSet(BaseViewSet):
    """
    A viewset for Warehouse Leaders to manage Incoming Goods.
    """

    queryset = Receiving.objects.all().order_by("-date_received")
    serializer_class = ReceivingSerializer
    lookup_field = "subid"
    search_fields = ["purchase_order__po_number", "invoice_number"]
    required_perms = [
        "warehouse.add_receiving",
        "warehouse.change_receiving",
        "warehouse.delete_receiving",
        "warehouse.view_receiving",
    ]
    my_tags = ["Warehouse Receiving"]

    def perform_create(self, serializer):
        serializer.save(received_by=self.request.user)
