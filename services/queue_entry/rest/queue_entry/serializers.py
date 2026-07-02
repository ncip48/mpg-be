from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.common.serializers import BaseModelSerializer
from services.queue_entry.models import QueueEntry

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("QueueEntrySerializer",)


class QueueEntrySerializer(BaseModelSerializer):
    """
    Serializer for QueueEntry management.
    """

    class Meta:
        model = QueueEntry
        fields = [
            "pk",
            "subid",
            "deposit",
            "forecast",
            "ticket_number",
            "created_by",
            "created",
            "updated",
        ]
        read_only_fields = [
            "pk",
            "subid",
            "ticket_number",
            "created_by",
            "created",
            "updated",
        ]