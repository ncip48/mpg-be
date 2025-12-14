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
    "QCFinishingDefectQuerySet",
    "QCFinishingDefectManager",
    "QCFinishingDefect",
)


class QCFinishingDefectQuerySet(models.QuerySet):
    pass


_QCFinishingDefectManagerBase = models.Manager.from_queryset(QCFinishingDefectQuerySet)  # type: type[QCFinishingDefectQuerySet]


class QCFinishingDefectManager(_QCFinishingDefectManagerBase):
    pass


class QCFinishingDefect(get_subid_model()):
    # OneToOne: Each Forecast has exactly one verification result
    forecast = models.OneToOneField(
        Forecast, on_delete=models.CASCADE, related_name="qc_finishing_defect"
    )

    # 1. User / QC Finishing
    checked_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
        help_text="QC Finishing yang menemukan defect",
    )

    # 5. Jumlah yang dikembalikan ke penjahit
    quantity_rejected = models.PositiveIntegerField(
        verbose_name="Jumlah Reject/Kembali"
    )

    # Detail tambahan untuk alasan pengembalian
    reason = models.TextField(blank=True, null=True, help_text="Alasan dikembalikan")

    # Status perbaikan
    is_repaired = models.BooleanField(
        default=False,
        help_text="Centang jika penjahit sudah memperbaiki dan mengembalikan lagi",
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = QCFinishingDefectManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_qc_finishing_defect", "Can add qc finishing defect verification"),
            ("view_qc_finishing_defect", "Can view qc finishing defect verification"),
            (
                "change_qc_finishing_defect",
                "Can change qc finishing defect verification",
            ),
            (
                "delete_qc_finishing_defect",
                "Can delete qc finishing defect verification",
            ),
        ]
        verbose_name = "QC Finishing Defect Verification"
        verbose_name_plural = "QC Finishing Defect Verifications"

    def __str__(self):
        return f"Verification for {self.forecast.id} - {self.checked_by} => {self.quantity_rejected}"
