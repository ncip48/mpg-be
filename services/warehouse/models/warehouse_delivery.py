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
    "WarehouseDeliveryQuerySet",
    "WarehouseDeliveryManager",
    "WarehouseDelivery",
)


class WarehouseDeliveryQuerySet(models.QuerySet):
    pass


_WarehouseDeliveryManagerBase = models.Manager.from_queryset(WarehouseDeliveryQuerySet)  # type: type[WarehouseDeliveryQuerySet]


class WarehouseDeliveryManager(_WarehouseDeliveryManagerBase):
    pass


class WarehouseDelivery(get_subid_model()):
    # OneToOne: Each Forecast has exactly one verification result
    forecast = models.OneToOneField(
        Forecast, on_delete=models.CASCADE, related_name="warehouse_deliveries"
    )

    # 1. User & Tanggal (Requirement Spreadsheet)
    delivered_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Admin Gudang",
    )
    delivery_date = models.DateField(
        auto_now_add=True, verbose_name="Tanggal Pengiriman"
    )

    # 4 & 6. Detail Jumlah (Kita buat model terpisah agar rapi, atau field per size)
    # Di sini kita gunakan total summary untuk tampilan cepat
    delivery_detail = models.JSONField()

    # 7. Jumlah Defect di Gudang
    defect_count = models.PositiveIntegerField(null=True, blank=True)

    # 8. Keterangan Tambahan Admin Gudang (Jika ada selisih dengan Forecast)
    detail = models.TextField(
        blank=True,
        null=True,
        help_text="Keterangan / alasan barang yang dikirim defect",
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = WarehouseDeliveryManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_warehouse_delivery", "Can add warehouse delivery"),
            ("view_warehouse_delivery", "Can view warehouse delivery"),
            ("change_warehouse_delivery", "Can change warehouse delivery"),
            ("delete_warehouse_delivery", "Can delete warehouse delivery"),
        ]
        verbose_name = "Warehouse Delivery"
        verbose_name_plural = "Warehouse Delivery"

    def __str__(self):
        return f"Receipt goods for {self.forecast.id} - {self.delivery_date}"
