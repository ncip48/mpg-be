from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.forecast.models.forecast import Forecast

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "WarehouseReceiptQuerySet",
    "WarehouseReceiptManager",
    "WarehouseReceipt",
)


class WarehouseReceiptQuerySet(models.QuerySet):
    pass


_WarehouseReceiptManagerBase = models.Manager.from_queryset(WarehouseReceiptQuerySet)  # type: type[WarehouseReceiptQuerySet]


class WarehouseReceiptManager(_WarehouseReceiptManagerBase):
    pass


class WarehouseReceipt(get_subid_model()):
    # OneToOne: Each Forecast has exactly one verification result
    forecast = models.OneToOneField(
        Forecast, on_delete=models.CASCADE, related_name="warehouse_receipts"
    )

    # 1. User & Tanggal (Requirement Spreadsheet)
    received_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Admin Gudang",
    )
    received_date = models.DateField(
        verbose_name="Tanggal Penerimaan", null=True, blank=True
    )

    # 4 & 6. Detail Jumlah (Kita buat model terpisah agar rapi, atau field per size)
    # Di sini kita gunakan total summary untuk tampilan cepat
    receive_detail = models.JSONField()

    # 7. Defect di Gudang
    defect_detail = models.JSONField()
    defect_note = models.TextField(
        blank=True,
        null=True,
        help_text="Catatan jika ada defect di gudang",
    )

    # 8. Keterangan Tambahan Admin Gudang (Jika ada selisih dengan Forecast)
    note = models.TextField(
        blank=True,
        null=True,
        help_text="Keterangan jika jumlah berbeda dengan forecast",
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = WarehouseReceiptManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_warehouse_receipt", "Can add warehouse receipt"),
            ("view_warehouse_receipt", "Can view warehouse receipt"),
            ("change_warehouse_receipt", "Can change warehouse receipt"),
            ("delete_warehouse_receipt", "Can delete warehouse receipt"),
        ]
        verbose_name = "Warehouse Receipt"
        verbose_name_plural = "Warehouse Receipts"

    def __str__(self):
        return f"Receipt goods for {self.forecast.id} - {self.received_date}"
