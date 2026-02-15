from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from core.common.viewsets import BaseViewSet
from services.warehouse.models import StockOpname
from services.warehouse.rest.stock_opname.serializers import StockOpnameSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("StockOpnameViewSet",)


class StockOpnameViewSet(BaseViewSet):
    """
    A viewset for Finance to manage Stock Opname.
    """

    queryset = StockOpname.objects.all().order_by("-date_so")
    serializer_class = StockOpnameSerializer
    lookup_field = "subid"
    search_fields = ["material__name"]
    permission_map = {
        "list": ["warehouse.view_stockopname"],
        "retrieve": ["warehouse.view_stockopname"],
        "create": ["warehouse.stock_opname_material"],
        "update": ["warehouse.stock_opname_material"],
        "destroy": ["warehouse.delete_stockopname"],
    }

    def get_required_perms(self):
        return self.permission_map.get(self.action, [])

    my_tags = ["Stock Opname"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
