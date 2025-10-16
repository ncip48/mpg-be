from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.viewsets import BaseViewSet
from services.product.models.fabric_type import FabricType
from services.product.rest.fabric_type.serializers import FabricTypeSerializer, FabricTypeSerializerSimple

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "FabricTypeViewSet",
)


class FabricTypeViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Fabric Types.
    Accessible only by superusers.
    """
    queryset = FabricType.objects.all()
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
    }
