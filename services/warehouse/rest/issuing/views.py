from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from core.common.viewsets import BaseViewSet
from services.warehouse.models import Issuing
from services.warehouse.rest.issuing.serializers import IssuingSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("IssuingViewSet",)


class IssuingViewSet(BaseViewSet):
    """
    A viewset for Warehouse Leaders to manage Outgoing Goods.
    """

    queryset = Issuing.objects.all().order_by("-date_out")
    serializer_class = IssuingSerializer
    lookup_field = "subid"
    search_fields = ["material__name"]
    required_perms = [
        "warehouse.add_issuing",
        "warehouse.change_issuing",
        "warehouse.delete_issuing",
        "warehouse.view_issuing",
    ]
    my_tags = ["Warehouse Issuing"]

    def perform_create(self, serializer):
        serializer.save(issued_by=self.request.user)
