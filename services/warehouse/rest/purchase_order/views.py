from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from core.common.viewsets import BaseViewSet
from services.warehouse.models import PurchaseOrder
from services.warehouse.rest.purchase_order.serializers import PurchaseOrderSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("PurchaseOrderViewSet",)


class PurchaseOrderViewSet(BaseViewSet):
    """
    A viewset for Finance to manage POs.
    """

    queryset = PurchaseOrder.objects.all().order_by("-created")
    serializer_class = PurchaseOrderSerializer
    lookup_field = "subid"
    search_fields = ["po_number", "supplier__name", "material__name"]
    required_perms = [
        "warehouse.add_purchaseorder",
        "warehouse.change_purchaseorder",
        "warehouse.delete_purchaseorder",
        "warehouse.view_purchaseorder",
    ]
    my_tags = ["Purchase Orders"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
