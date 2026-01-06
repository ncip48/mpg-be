from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _
from rest_framework.parsers import FormParser, MultiPartParser

from core.common.viewsets import BaseViewSet
from services.printer.models.printer import Printer
from services.printer.rest.printer.serializers import PrinterSerializer
from services.product.models.product import Product
from services.product.rest.product.filtersets import ProductFilterSet
from services.product.rest.product.serializers import (
    ProductSerializer,
    ProductSerializerSimple,
)
from services.store.models.store import Store
from services.store.rest.store.serializers import StoreSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("ProductViewSet",)


class ProductViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Products.
    Accessible only by superusers.
    """

    my_tags = ["Products"]
    queryset = Product.objects.all().select_related("store", "printer")
    serializer_class = ProductSerializer
    lookup_field = "subid"
    search_fields = ["name", "sku", "store__name", "printer__name"]
    required_perms = [
        "product.add_product",
        "product.change_product",
        "product.delete_product",
        "product.view_product",
    ]
    # parser_classes = [MultiPartParser, FormParser]
    serializer_map = {
        "autocomplete": ProductSerializerSimple,
    }
    filterset_class = ProductFilterSet
