from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

from django.db import models

# from django.utils.translation import gettext_lazy as _
from core.common.models import get_subid_model
from services.customer.models.customer import Customer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "OrderQuerySet",
    "OrderManager",
    "Order",
)


class OrderQuerySet(models.QuerySet):
    pass


_OrderManagerBase = models.Manager.from_queryset(OrderQuerySet)  # type: type[OrderQuerySet]


class OrderManager(_OrderManagerBase):
    pass


def generate_order_id():
    return f"EZK-{random.randint(1000, 9999)}"


class Order(get_subid_model()):
    identifier = models.CharField(
        max_length=20, null=True, blank=True, default=generate_order_id
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        related_name="orders",
        null=True,
        blank=True,
    )
    convection_name = models.CharField(max_length=150, blank=True, null=True)
    order_type = models.CharField(
        max_length=20,
        choices=[
            ("konveksi", "Konveksi"),
            ("marketplace", "Marketplace"),
        ],
    )
    priority_status = models.CharField(
        max_length=20,
        choices=[
            ("reguler", "Reguler"),
            ("urgent", "Urgent"),
            ("express", "Express"),
        ],
        default="reguler",
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("deposit", "Deposit"),
            ("in_production", "In Production"),
            ("completed", "Completed"),
        ],
        default="draft",
    )
    # deposit_amount = models.DecimalField(
    #     max_digits=12, decimal_places=2, null=True, blank=True
    # )

    # Marketplace Form
    user_name = models.CharField(max_length=150, blank=True, null=True)
    order_number = models.CharField(max_length=100, blank=True, null=True)
    marketplace = models.CharField(
        max_length=20,
        choices=[
            ("shopee", "Shopee"),
            ("tiktok", "TikTok"),
            ("tokopedia", "Tokopedia"),
        ],
        blank=True,
        null=True,
    )
    order_choice = models.CharField(
        max_length=20,
        choices=[
            ("custom_design", "Custom Design"),
            ("top", "Top"),
            ("pants", "Pants"),
            ("set", "Set"),
        ],
        blank=True,
        null=True,
    )
    quantity = models.PositiveIntegerField(default=0)
    estimated_shipping_date = models.DateField(blank=True, null=True)

    # For CS2
    # reminder_one = models.DateField(blank=True, null=True)
    # reminder_two = models.DateField(blank=True, null=True)
    # is_expired = models.BooleanField(default=False)
    # is_paid_off = models.BooleanField(default=False)
    # note = models.TextField(blank=True, null=True)
    # shipping_courier = models.CharField(max_length=100, blank=True, null=True)

    created_by = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = OrderManager()

    class Meta:
        default_permissions = ()
        permissions = [
            # --- Marketplace Order Permissions ---
            ("can_add_order_marketplace", "Can add marketplace order"),
            ("can_view_order_marketplace", "Can view marketplace order"),
            ("can_change_order_marketplace", "Can change marketplace order"),
            ("can_delete_order_marketplace", "Can delete marketplace order"),
        ]

    def __str__(self):
        return f"Order {self.pk} - {self.customer} ({self.status})"

    @property
    def is_reminder_one(self):
        return self.reminder_one is not None

    @property
    def is_reminder_two(self):
        return self.reminder_two is not None
