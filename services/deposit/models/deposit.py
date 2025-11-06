from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
# from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.order.models import Order

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "DepositQuerySet",
    "DepositManager",
    "Deposit",
)


class DepositQuerySet(models.QuerySet):
    pass


_DepositManagerBase = models.Manager.from_queryset(DepositQuerySet)  # type: type[DepositQuerySet]


class DepositManager(_DepositManagerBase):
    pass


class Deposit(get_subid_model()):
    order = models.ForeignKey(
        Order,
        on_delete=models.SET_NULL,
        related_name="deposits",
        null=True,
        blank=True,
    )
    deposit_amount = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    # priority_status = models.CharField(
    #     max_length=20,
    #     choices=[("reguler", "Reguler"), ("urgent", "Urgent")],
    #     default="reguler",
    # )

    # For CS2
    reminder_one = models.DateField(blank=True, null=True)
    reminder_two = models.DateField(blank=True, null=True)
    is_expired = models.BooleanField(default=False)
    is_paid_off = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)
    shipping_courier = models.CharField(max_length=100, blank=True, null=True)

    created_by = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = DepositManager()

    class Meta:
        default_permissions = ()
        permissions = [
            # --- Deposit Permissions ---
            ("can_add_deposit", "Can add deposit"),
            ("can_view_deposit", "Can view deposit"),
            ("can_change_deposit", "Can change deposit"),
            ("can_delete_deposit", "Can delete deposit"),
        ]

    def __str__(self):
        return f"Deposit {self.pk} - {self.customer} ({self.status})"

    @property
    def is_reminder_one(self):
        return self.reminder_one is not None

    @property
    def is_reminder_two(self):
        return self.reminder_two is not None
