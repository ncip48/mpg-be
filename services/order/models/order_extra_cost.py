from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.order.models.order import Order

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "OrderExtraCostQuerySet",
    "OrderExtraCostManager",
    "OrderExtraCost",
)


class OrderExtraCostQuerySet(models.QuerySet):
    pass


_OrderExtraCostManagerBase = models.Manager.from_queryset(OrderExtraCostQuerySet)  # type: type[OrderExtraCostQuerySet]


class OrderExtraCostManager(_OrderExtraCostManagerBase):
    pass


class OrderExtraCost(get_subid_model()):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="extra_costs")
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField(default=1)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    type = models.CharField(max_length=20, choices=[
        ("ongkir", "Biaya Ongkos Kirim"),
        ("charge", "Biaya Tambahan"),
        ("discount", "Diskon"),
        ("promo", "Promo"),
    ], default="charge")
    
    objects = OrderExtraCostManager()
    
    def __str__(self):
        return f"ExtraCost {self.pk} for Order {self.order.pk}: {self.description}"
