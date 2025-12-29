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
    "StockOpnameQuerySet",
    "StockOpnameManager",
    "StockOpname",
)


class StockOpnameQuerySet(models.QuerySet):
    pass


_StockOpnameManagerBase = models.Manager.from_queryset(StockOpnameQuerySet)  # type: type[StockOpnameQuerySet]


class StockOpnameManager(_StockOpnameManagerBase):
    pass


class StockOpname(get_subid_model()):
    """
    (2) Periodical check by Finance.
    Calculates difference and allows adjustment.
    """

    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    date_so = models.DateField(default=timezone.now)

    qty_system = models.IntegerField(help_text="Stock in system at moment of SO")
    qty_actual = models.IntegerField(help_text="Physical count")

    notes = models.TextField(blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)

    objects = StockOpnameManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_stock_opname", "Can add stock opname"),
            ("view_stock_opname", "Can view stock opname"),
            ("change_stock_opname", "Can change stock opname"),
            ("delete_stock_opname", "Can delete stock opname"),
        ]
        verbose_name = "Stock Opname"
        verbose_name_plural = "Stock Opnames"

    @property
    def difference(self):
        return self.qty_actual - self.qty_system

    def save(self, *args, **kwargs):
        # If this is a new SO, capture the current system stock automatically
        if not self.pk:
            self.qty_system = self.material.current_stock

        super().save(*args, **kwargs)

        # LOGIC: If there is a difference, update the Master Stock automatically
        if self.difference != 0:
            self.material.current_stock = self.qty_actual
            self.material.save()
