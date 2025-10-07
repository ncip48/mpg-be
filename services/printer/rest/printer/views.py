from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.viewsets import BaseViewSet
from services.printer.models.printer import Printer
from services.printer.rest.printer.serializers import PrinterSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "PrinterViewSet",
)

class PrinterViewSet(BaseViewSet):
    """
    A viewset for viewing and editing printers.
    Accessible only by superusers.
    """
    queryset = Printer.objects.all()
    serializer_class = PrinterSerializer
    lookup_field = "subid"
    search_fields = ["name",]
    required_perms = [
        "printer.add_printer",
        "printer.change_printer",
        "printer.delete_printer",
        "printer.view_printer",
    ]
    my_tags = ["Printers"]
    serializer_map = {
        "autocomplete": PrinterSerializer,
    }
