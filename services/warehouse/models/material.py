from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "MaterialQuerySet",
    "MaterialManager",
    "Material",
)


class MaterialQuerySet(models.QuerySet):
    pass


_MaterialManagerBase = models.Manager.from_queryset(MaterialQuerySet)  # type: type[MaterialQuerySet]


class MaterialManager(_MaterialManagerBase):
    pass


class Material(get_subid_model()):
    """
    Represents the Master Bahan Baku.
    The 'current_stock' field allows for real-time dashboard viewing.
    """

    class UnitChoices(models.TextChoices):
        PCS = "PCS", "Pcs"
        KOLI = "KOLI", "Koli"
        ROLL = "ROLL", "Roll"
        DUS = "DUS", "Dus"

    class CategoryChoices(models.TextChoices):
        KAIN = "KAIN", "Kain"
        KERTAS = "KERTAS", "Kertas"
        TINTA = "TINTA", "Tinta"
        PLASTIK = "PLASTIK", "Plastik"

    code = models.CharField(max_length=50, unique=True)  # Internal code
    name = models.CharField(max_length=255)  # e.g., "Kain Cotton 30s"
    category = models.CharField(max_length=50, choices=CategoryChoices.choices)
    description = models.TextField(
        blank=True, help_text="Specific details (e.g., jenis kain)"
    )
    unit = models.CharField(max_length=10, choices=UnitChoices.choices)

    # This field updates automatically via Signals/Logic based on In/Out
    current_stock = models.IntegerField(default=0)

    objects = MaterialManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_material", "Can add material"),
            ("view_material", "Can view material"),
            ("change_material", "Can change material"),
            ("delete_material", "Can delete material"),
        ]
        verbose_name = "Material"
        verbose_name_plural = "Materials"

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"
