from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.common.viewsets import BaseViewSet
from services.queue_entry.models import QueueEntry
from services.queue_entry.rest.queue_entry.filtersets import QueueEntryFilterSet
from services.queue_entry.rest.queue_entry.serializers import (
    QueueEntrySerializer,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("QueueEntryViewSet",)


class QueueEntryViewSet(BaseViewSet):
    required_module_code = "pre-produksi"
    required_perms = [
        "queue.can_add_queue_entry",
        "queue.can_change_queue_entry",
        "queue.can_delete_queue_entry",
        "queue.can_view_queue_entry",
    ]

    my_tags = ["Queue"]

    queryset = (
        QueueEntry.objects.select_related(
            "deposit",
            "forecast",
            "created_by",
            "deposit__order",
            "deposit__order__customer",
        )
        .order_by("-created")
    )

    lookup_field = "subid"

    serializer_class = QueueEntrySerializer
    filterset_class = QueueEntryFilterSet

    search_fields = [
        "ticket_number",
        "deposit__order__order_number",
        "deposit__order__customer__name",
        "deposit__pic",
    ]

    serializer_map = {
        "create": QueueEntrySerializer,
        "update": QueueEntrySerializer,
        "partial_update": QueueEntrySerializer,
        "retrieve": QueueEntrySerializer,
    }