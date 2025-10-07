from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.viewsets import BaseViewSet
from services.printer.models.printer import Printer
from services.printer.rest.printer.serializers import PrinterSerializer
from services.store.models.store import Store
from services.store.rest.store.serializers import StoreSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "StoreViewSet",
)

class StoreViewSet(BaseViewSet):
    """
    A viewset for viewing and editing stores.
    Accessible only by superusers.
    """
    my_tags = ["Stores"]
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    lookup_field = "subid"
    search_fields = ["name",]
    required_perms = [
        "store.add_store",
        "store.change_store",
        "store.delete_store",
        "store.view_store",
    ]
    serializer_map = {
        "autocomplete": StoreSerializer,
    }
