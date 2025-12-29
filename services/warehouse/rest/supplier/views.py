from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from core.common.viewsets import BaseViewSet
from services.warehouse.models import Supplier
from services.warehouse.rest.supplier.serializers import SupplierSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("SupplierViewSet",)


class SupplierViewSet(BaseViewSet):
    """
    A viewset for managing suppliers.
    """

    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    lookup_field = "subid"
    search_fields = ["name", "contact_info"]
    required_perms = [
        "warehouse.add_supplier",
        "warehouse.change_supplier",
        "warehouse.delete_supplier",
        "warehouse.view_supplier",
    ]
    my_tags = ["Suppliers"]
    serializer_map = {
        "autocomplete": SupplierSerializer,
    }
