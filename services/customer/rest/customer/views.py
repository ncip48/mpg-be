from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.viewsets import BaseViewSet
from services.customer.models.customer import Customer
from services.customer.rest.customer.serializers import CustomerSerializer, CustomerSerializerSimple
from services.printer.models.printer import Printer
from services.printer.rest.printer.serializers import PrinterSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "CustomerViewSet",
)

class CustomerViewSet(BaseViewSet):
    """
    A viewset for viewing and editing customers.
    Accessible only by superusers.
    """
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    lookup_field = "subid"
    search_fields = ["name", "phone", "address"]
    filterset_fields = ["source"]
    required_perms = [
        "customer.add_customer",
        "customer.change_customer",
        "customer.delete_customer",
        "customer.view_customer",
    ]
    my_tags = ["Customers"]
    serializer_map = {
        "autocomplete": CustomerSerializerSimple,
    }
