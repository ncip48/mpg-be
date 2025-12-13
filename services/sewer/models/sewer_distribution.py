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
    "SewerDistributionQuerySet",
    "SewerDistributionManager",
    "SewerDistribution",
)


class SewerDistributionQuerySet(models.QuerySet):
    pass


_SewerDistributionManagerBase = models.Manager.from_queryset(SewerDistributionQuerySet)  # type: type[SewerDistributionQuerySet]


class SewerDistributionManager(_SewerDistributionManagerBase):
    pass


class SewerDistribution(get_subid_model()):
    """
    SewerDistribution models
    """

    # Link to the main Forecast
    forecast = models.ForeignKey(
        Forecast, on_delete=models.CASCADE, related_name="sewer_distributions"
    )

    # --- 1. User / QC Potong (Distributor) ---
    distributed_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="distributions_created",
        help_text="QC Potong yang melakukan pembagian",
    )

    # --- 5. Sewer (Penjahit) ---
    # Assuming you have a User or Employee model for Sewers
    sewer = models.ForeignKey(
        "sewer.Sewer",
        on_delete=models.SET_NULL,
        null=True,
        related_name="assigned_sewing_jobs",
        verbose_name="Nama Penjahit",
    )

    # --- 6. Quantity & Size ---
    quantity = models.PositiveIntegerField(
        help_text="Jumlah yang dibagikan ke penjahit"
    )

    # If size is strictly tied to Forecast, fetch it from there.
    # If one forecast has multiple sizes (mixed), add a size field here.
    # Based on your previous inputs, size seems tied to Forecast properties.

    # --- 4. Accessories Checklist (Kelengkapan) ---
    # has_rib = models.BooleanField(default=False, verbose_name="Acc RIP")
    # has_collar = models.BooleanField(default=False, verbose_name="Acc Kerah")
    # has_sleeve = models.BooleanField(default=False, verbose_name="Acc Lengan")
    # has_pocket = models.BooleanField(default=False, verbose_name="Acc Saku")

    accessories = models.JSONField(default=[])

    # Extra notes for missing items or specific instructions
    notes = models.TextField(blank=True, null=True)

    is_full = models.BooleanField(default=True, verbose_name="Apakah Lengkap")

    # --- 7. Barcode / Tracking System ---
    tracking_code = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        help_text="Nomor Barcode unik untuk tracking",
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = SewerDistributionManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_sewer_distribution", "Can add sewer distribution"),
            ("view_sewer_distribution", "Can view sewer distribution"),
            ("change_sewer_distribution", "Can change sewer distribution"),
            ("delete_sewer_distribution", "Can delete sewer distribution"),
        ]
        verbose_name = _("sewer")
        verbose_name_plural = _("sewers")

    def save(self, *args, **kwargs):
        if not self.tracking_code:
            self.tracking_code = str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tracking_code} - {self.sewer} ({self.quantity})"
