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
    "QCFinishingQuerySet",
    "QCFinishingManager",
    "QCFinishing",
)


class QCFinishingQuerySet(models.QuerySet):
    pass


_QCFinishingManagerBase = models.Manager.from_queryset(QCFinishingQuerySet)  # type: type[QCFinishingQuerySet]


class QCFinishingManager(_QCFinishingManagerBase):
    pass


class QCFinishing(get_subid_model()):
    # OneToOne: Each Forecast has exactly one verification result
    forecast = models.OneToOneField(
        Forecast, on_delete=models.CASCADE, related_name="qc_finishings"
    )

    # 1. User / Personil Print (Who checked it)
    verified_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
        help_text="Personil QC Finishing yang melakukan pengecekan",
    )

    # 2 & 3. Realisasi Penjahit
    # Jumlah yang benar-benar diterima saat ini
    received_quantity = models.PositiveIntegerField()

    # Status Realisasi: OK (Lengkap) atau KURANG
    STATUS_REALISASI = (
        ("ok", "OK (Lengkap)"),
        ("kurang", "Kurang"),
    )
    realization_status = models.CharField(max_length=10, choices=STATUS_REALISASI)

    # 5. Kode Verifikasi Gudang
    # Kode unik baru untuk verifikasi Admin Gudang
    verification_code = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Nomor untuk verifikasi Admin Gudang",
    )

    notes = models.TextField(blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = QCFinishingManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_qc_finishing", "Can add qc finishing verification"),
            ("view_qc_finishing", "Can view qc finishing verification"),
            ("change_qc_finishing", "Can change qc finishing verification"),
            ("delete_qc_finishing", "Can delete qc finishing verification"),
        ]
        verbose_name = "QC Finishing Verification"
        verbose_name_plural = "QC Finishing Verifications"

    def save(self, *args, **kwargs):
        if not self.verification_code:
            self.verification_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Verification for {self.forecast.id} - {self.realization_status} => {self.verification_code}"
