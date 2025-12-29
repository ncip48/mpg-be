from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.account.models.user import User
from services.warehouse.models.material import Material
from services.warehouse.models.supplier import Supplier

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "PurchaseOrderQuerySet",
    "PurchaseOrderManager",
    "PurchaseOrder",
)


class PurchaseOrderQuerySet(models.QuerySet):
    pass


_PurchaseOrderManagerBase = models.Manager.from_queryset(PurchaseOrderQuerySet)  # type: type[PurchaseOrderQuerySet]


class PurchaseOrderManager(_PurchaseOrderManagerBase):
    pass


class PurchaseOrder(get_subid_model()):
    """
    (1) Input by Finance.
    Generates the PO Number.
    """

    po_number = models.CharField(max_length=50, unique=True, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    material = models.ForeignKey(Material, on_delete=models.PROTECT)

    qty_ordered = models.IntegerField()
    order_date = models.DateField(default=timezone.now)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = PurchaseOrderManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_purchase_order", "Can add purchase order"),
            ("view_purchase_order", "Can view purchase order"),
            ("change_purchase_order", "Can change purchase order"),
            ("delete_purchase_order", "Can delete purchase order"),
        ]
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"

    def save(self, *args, **kwargs):
        # Auto-generate PO Number if not exists (e.g., PO-202310-001)
        if not self.po_number:
            count = PurchaseOrder.objects.count() + 1
            self.po_number = f"PO-{timezone.now().strftime('%Y%m')}-{count:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.po_number} - {self.supplier.name}"
