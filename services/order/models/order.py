from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

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


class Order(get_subid_model()):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, related_name="orders", null=True, blank=True)
    order_type = models.CharField(
        max_length=20,
        choices=[("konveksi", "Konveksi"), ("marketplace", "Marketplace")],
    )
    priority_status = models.CharField(
        max_length=20,
        choices=[("reguler", "Reguler"), ("urgent", "Urgent")],
        default="reguler"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ("draft", "Draft"),
            ("deposit", "Deposit"),
            ("in_production", "In Production"),
            ("completed", "Completed"),
        ],
        default="draft"
    )
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
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
    estimated_shipping_date = models.DateField(blank=True, null=True)
    
    # For CS2
    reminder_one = models.BooleanField(default=False)
    reminder_two = models.BooleanField(default=False)
    is_expired = models.BooleanField(default=False)
    is_paid_off = models.BooleanField(default=False)
    note = models.TextField(blank=True, null=True)
    shipping_courier = models.CharField(max_length=100, blank=True, null=True)
    
    created_by = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    def __str__(self):
        return f"Order {self.pk} - {self.customer} ({self.status})"
