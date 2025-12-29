from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ComplaintActionQuerySet",
    "ComplaintActionManager",
    "ComplaintAction",
)


class ComplaintActionQuerySet(models.QuerySet):
    pass


_ComplaintActionManagerBase = models.Manager.from_queryset(ComplaintActionQuerySet)  # type: type[ComplaintActionQuerySet]


class ComplaintActionManager(_ComplaintActionManagerBase):
    pass


class ComplaintAction(get_subid_model()):
    ACTION_TYPE = [
        ("QC_VERIFY", "QC Verification"),
        ("APPROVAL", "Approval"),
    ]

    ACTION_RESULT = [
        ("ACCEPTED", "Diterima"),
        ("REJECTED", "Ditolak"),
        ("REPLACE", "Kirim Ulang"),
        ("REPAIR", "Perbaikan"),
        ("REFUND", "Refund"),
    ]

    ticket = models.ForeignKey(
        "ticket.ComplaintTicket",
        on_delete=models.CASCADE,
        related_name="actions",
    )

    action_type = models.CharField(max_length=20, choices=ACTION_TYPE)
    result = models.CharField(max_length=20, choices=ACTION_RESULT)

    note = models.TextField(blank=True)
    estimated_finish_date = models.DateField(null=True, blank=True)

    acted_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
    )

    created = models.DateTimeField(auto_now_add=True)

    objects = ComplaintActionManager()

    class Meta:
        verbose_name = _("ticket complaint action")
        verbose_name_plural = _("ticket complaint actions")
        default_permissions = ()
        permissions = [
            # --- Marketplace Order Permissions ---
            ("can_action_complaint_ticket", "Can action complaint ticket"),
        ]

    def __str__(self) -> str:
        return self.ticket
