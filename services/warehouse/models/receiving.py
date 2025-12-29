from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.account.models.user import User
from services.warehouse.models.purchase_order import PurchaseOrder

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ReceivingQuerySet",
    "ReceivingManager",
    "Receiving",
)


class ReceivingQuerySet(models.QuerySet):
    pass


_ReceivingManagerBase = models.Manager.from_queryset(ReceivingQuerySet)  # type: type[ReceivingQuerySet]


class ReceivingManager(_ReceivingManagerBase):
    pass


class Receiving(get_subid_model()):
    """
    (3) Input by Leader.
    Receives goods based on Finance's PO.
    """

    purchase_order = models.ForeignKey(
        PurchaseOrder, on_delete=models.CASCADE, related_name="receivings"
    )
    invoice_number = models.CharField(
        max_length=100, help_text="Nomor Faktur / Surat Jalan"
    )

    qty_received = models.IntegerField(help_text="Actual Quantity Received")
    date_received = models.DateField(default=timezone.now)

    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    objects = ReceivingManager()

    class Meta:
        default_permissions = ()
        verbose_name = "Receiving"
        verbose_name_plural = "Receivings"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # LOGIC: Update Master Stock (Add)
        material = self.purchase_order.material
        material.current_stock += self.qty_received
        material.save()

    def __str__(self):
        return f"IN - {self.purchase_order.po_number}"
