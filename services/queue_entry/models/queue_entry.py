from __future__ import annotations

import logging
import secrets
import string
from typing import TYPE_CHECKING

from django.db import models

from core.common.models import get_subid_model
from services.deposit.models import Deposit
from services.forecast.models import Forecast

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "QueueEntryQuerySet",
    "QueueEntryManager",
    "QueueEntry",
)


class QueueEntryQuerySet(models.QuerySet):
    pass


_QueueEntryManagerBase = models.Manager.from_queryset(
    QueueEntryQuerySet
)


class QueueEntryManager(_QueueEntryManagerBase):
    pass


class QueueEntry(get_subid_model()):
    deposit = models.ForeignKey(
        Deposit,
        on_delete=models.CASCADE,
        related_name="queue_entries",
        null=True,
        blank=True,
    )
    
    order_item = models.ForeignKey(
        "order.OrderItem",
        on_delete=models.CASCADE,
        related_name="queue_entries",
        null=True,
        blank=True,
    )
    
    order = models.ForeignKey(
        "order.Order",
        on_delete=models.CASCADE,
        related_name="queue_entries",
        null=True,
        blank=True,
    )

    forecast = models.ForeignKey(
        Forecast,
        on_delete=models.SET_NULL,
        related_name="queue_entries",
        null=True,
        blank=True,
    )

    ticket_number = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
    )

    created_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = QueueEntryManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("can_add_queue_entry", "Can add queue entry"),
            ("can_view_queue_entry", "Can view queue entry"),
            ("can_change_queue_entry", "Can change queue entry"),
            ("can_delete_queue_entry", "Can delete queue entry"),
        ]

    def __str__(self):
        return self.ticket_number

    @staticmethod
    def generate_ticket_number():
        while True:
            ticket = (
                "Q-"
                + "".join(secrets.choice(string.ascii_uppercase) for _ in range(3))
                + "".join(secrets.choice(string.digits) for _ in range(5))
            )

            if not QueueEntry.objects.filter(ticket_number=ticket).exists():
                return ticket

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = self.generate_ticket_number()

        super().save(*args, **kwargs)