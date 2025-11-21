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
    "PrintVerificationQuerySet",
    "PrintVerificationManager",
    "PrintVerification",
)


class PrintVerificationQuerySet(models.QuerySet):
    pass


_PrintVerificationManagerBase = models.Manager.from_queryset(PrintVerificationQuerySet)  # type: type[PrintVerificationQuerySet]


class PrintVerificationManager(_PrintVerificationManagerBase):
    pass


class PrintVerification(get_subid_model()):
    # OneToOne: Each Forecast has exactly one verification result
    forecast = models.OneToOneField(
        Forecast, on_delete=models.CASCADE, related_name="verification"
    )

    # 1. User / Personil Print (Who checked it)
    verified_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
        help_text="Personil Print yang melakukan pengecekan",
    )

    # 2. Timestamp (When verification happened)
    verified_at = models.DateTimeField(auto_now_add=True)

    # 4. Hasil Pengecekan (Yes/No)
    # True = Ya, Sesuai
    # False = Tidak Sesuai
    is_approved = models.BooleanField(
        default=True, verbose_name="Apakah hasil pengecekan sudah sesuai?"
    )

    # Data if "Tidak Sesuai" (Nullable)
    rejected_quantity = models.PositiveIntegerField(
        default=0, help_text="Jumlah hasil yang tidak sesuai (pcs)"
    )
    rejection_note = models.TextField(
        blank=True, null=True, help_text="Keterangan bagian yang tidak sesuai"
    )

    # 5. Completion Time (When print was actually finished)
    # This might differ from verified_at if they verify after finishing
    finished_at = models.DateTimeField(
        null=True, blank=True, help_text="Waktu print selesai dikerjakan"
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = PrintVerificationManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_print_verification", "Can add print verification"),
            ("view_print_verification", "Can view print verification"),
            ("change_print_verification", "Can change print verification"),
            ("delete_print_verification", "Can delete print verification"),
        ]
        verbose_name = "Print Verification"
        verbose_name_plural = "Print Verifications"

    def __str__(self):
        return f"Verification for {self.forecast.id} - {self.is_approved}"
