from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.forecast.models.forecast import Forecast

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "QCCuttingVerificationQuerySet",
    "QCCuttingVerificationManager",
    "QCCuttingVerification",
)


class QCCuttingVerificationQuerySet(models.QuerySet):
    pass


_QCCuttingVerificationManagerBase = models.Manager.from_queryset(
    QCCuttingVerificationQuerySet
)  # type: type[QCCuttingVerificationQuerySet]


class QCCuttingVerificationManager(_QCCuttingVerificationManagerBase):
    pass


class QCCuttingVerification(get_subid_model()):
    # --- 1. Defect Area Options (Bagian yang rusak) ---
    class DefectArea(models.TextChoices):
        ATASAN = "atasan", "Atasan"
        LENGAN_KANAN = "lengan_kanan", "Lengan Kanan"
        LENGAN_KIRI = "lengan_kiri", "Lengan Kiri"
        BAGIAN_DEPAN = "bagian_depan", "Bagian Depan"
        BAGIAN_BELAKANG = "bagian_belakang", "Bagian Belakang"
        KERAH = "kerah", "Kerah"
        CELANA_KIRI = "celana_kiri", "Celana Kiri"
        CELANA_KANAN = "celana_kanan", "Celana Kanan"
        SATU_STEL = "satu_stel", "Satu Stel (Atasan dan Celana)"
        LAINNYA = "lainnya", "Keterangan Lainnya"

    # --- Relationships ---
    forecast = models.OneToOneField(
        Forecast, on_delete=models.CASCADE, related_name="qc_cutting_verification"
    )

    # --- 2. User / QC Officer ---
    checked_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
        help_text="QC yang melakukan proses pengecekan",
    )

    # --- 3. Verification Status ---
    verified_at = models.DateTimeField(auto_now_add=True)

    # "Apakah hasil pengecekan sudah sesuai?"
    is_approved = models.BooleanField(
        default=True, verbose_name="Hasil Pengecekan Sesuai?"
    )

    # --- 4. Reject Details (Only used if is_approved = False) ---
    rejected_quantity = models.PositiveIntegerField(
        default=0, help_text="Jumlah hasil yang tidak sesuai (pcs)"
    )

    # "Bagian yang rusak"
    # defect_area = models.CharField(
    #     max_length=50,
    #     choices=DefectArea.choices,
    #     blank=True,
    #     null=True,
    #     help_text="Pilih bagian yang rusak jika tidak sesuai",
    # )
    defect_area = models.JSONField(
        help_text="Pilih bagian yang rusak jika tidak sesuai",
    )

    defect_note = models.TextField(
        blank=True,
        null=True,
        verbose_name="Keterangan Lainnya",
        help_text="Detail kerusakan jika memilih 'Keterangan Lainnya' atau info tambahan",
    )

    # "Opsi upload foto hasil yang reject"
    defect_image = models.ImageField(
        upload_to="qc_cutting_defects/",
        blank=True,
        null=True,
        help_text="Upload foto bukti reject",
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = QCCuttingVerificationManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_qc_cutting_verification", "Can add QC cutting verification"),
            ("view_qc_cutting_verification", "Can view QC cutting verification"),
            ("change_qc_cutting_verification", "Can change QC cutting verification"),
            ("delete_qc_cutting_verification", "Can delete QC cutting verification"),
        ]
        verbose_name = "QC Cutting Verification"
        verbose_name_plural = "QC Cutting Verifications"

    def __str__(self):
        status = "PASS" if self.is_approved else "REJECT"
        return f"QC Cutting {self.forecast.id} - {status}"
