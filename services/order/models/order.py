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
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
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
    # total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    deposit_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    objects = OrderManager()
    
    def __str__(self):
        return f"Order {self.pk} - {self.customer} ({self.status})"
