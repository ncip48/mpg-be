from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.account.models.user import User
from services.warehouse.models.material import Material

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "IssuingQuerySet",
    "IssuingManager",
    "Issuing",
)


class IssuingQuerySet(models.QuerySet):
    pass


_IssuingManagerBase = models.Manager.from_queryset(IssuingQuerySet)  # type: type[IssuingQuerySet]


class IssuingManager(_IssuingManagerBase):
    pass


class Issuing(get_subid_model()):
    """
    (4) Input by Leader.
    Material exiting for production.
    """

    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    forecast_date = models.DateField(help_text="Tanggal Forecast")

    qty_out = models.IntegerField()
    date_out = models.DateField(default=timezone.now)

    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    objects = IssuingManager()

    class Meta:
        default_permissions = ()
        verbose_name = "Issuing"
        verbose_name_plural = "Issuings"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # LOGIC: Update Master Stock (Subtract)
        self.material.current_stock -= self.qty_out
        self.material.save()

    def __str__(self):
        return f"OUT - {self.material.name} - {self.qty_out}"
