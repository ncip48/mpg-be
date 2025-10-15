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
    "InvoiceQuerySet",
    "InvoiceManager",
    "Invoice",
)


class InvoiceQuerySet(models.QuerySet):
    pass


_InvoiceManagerBase = models.Manager.from_queryset(InvoiceQuerySet)  # type: type[InvoiceQuerySet]


class InvoiceManager(_InvoiceManagerBase):
    pass


class Invoice(get_subid_model()):
    invoice_no = models.CharField(max_length=50, unique=True)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="invoice")
    issued_date = models.DateField()
    delivery_date = models.DateField()
    is_deposit_invoice = models.BooleanField(
        default=False,
        help_text=_("Indicates if this invoice is for a down payment"),
    )
    note = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("cancelled", "Cancelled"),
        ("partial", "Partial (Deposit)"),
    ], default="unpaid")
    
    objects = InvoiceManager()
    
    def __str__(self):
        return f"Invoice {self.invoice_no} for Order {self.order.pk}"
