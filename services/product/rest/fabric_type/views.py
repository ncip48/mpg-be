from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.viewsets import BaseViewSet
from services.product.models.fabric_type import FabricType
from services.product.rest.fabric_type.serializers import (
    FabricTypeCreateSerializer,
    FabricTypeSerializer,
    FabricTypeSerializerSimple,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("FabricTypeViewSet",)


class FabricTypeViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Fabric Types.
    Accessible only by superusers.
    """

    queryset = FabricType.objects.prefetch_related(
        "fabric_prices__variant_type",
    )
    serializer_class = FabricTypeSerializer
    lookup_field = "subid"
    search_fields = ["name"]
    required_perms = [
        "product.add_fabrictype",
        "product.change_fabrictype",
        "product.delete_fabrictype",
        "product.view_fabrictype",
    ]
    my_tags = ["Fabric Types"]
    serializer_map = {
        "autocomplete": FabricTypeSerializerSimple,
        "create": FabricTypeCreateSerializer,
        "partial_update": FabricTypeCreateSerializer,
        "update": FabricTypeCreateSerializer,
    }
