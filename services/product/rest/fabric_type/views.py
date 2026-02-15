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

    required_module_code = "kain"

    queryset = FabricType.objects.prefetch_related(
        "fabric_prices__variant_type",
    )
    serializer_class = FabricTypeSerializer
    lookup_field = "subid"
    search_fields = ["name"]
    required_perms = [
        "product.can_add_fabric_type",
        "product.can_change_fabric_type",
        "product.can_delete_fabric_type",
        "product.can_view_fabric_type",
    ]
    my_tags = ["Fabric Types"]
    serializer_map = {
        "autocomplete": FabricTypeSerializerSimple,
        "create": FabricTypeCreateSerializer,
        "partial_update": FabricTypeCreateSerializer,
        "update": FabricTypeCreateSerializer,
    }
