from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.common.viewsets import BaseViewSet
from services.defect.models import Reject
from services.defect.rest.reject.filtersets import RejectFilterSet
from services.defect.rest.reject.serializers import RejectSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("RejectViewSet",)


class RejectViewSet(BaseViewSet):
    required_module_code = "reject"

    required_perms = [
        "reject.can_add_reject",
        "reject.can_change_reject",
        "reject.can_delete_reject",
        "reject.can_view_reject",
    ]

    my_tags = ["Reject"]

    queryset = (
        Reject.objects.select_related(
            "content_type",
            "created_by",
        )
        .order_by("-created")
    )

    lookup_field = "subid"

    serializer_class = RejectSerializer
    # filterset_class = RejectFilterSet

    search_fields = [
        "subid",
        "defect",
        "note",
    ]

    serializer_map = {
        "create": RejectSerializer,
        "update": RejectSerializer,
        "partial_update": RejectSerializer,
        "retrieve": RejectSerializer,
    }