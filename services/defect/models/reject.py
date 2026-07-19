from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from core.common.models import get_subid_model

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "RejectQuerySet",
    "RejectManager",
    "Reject",
)


class RejectQuerySet(models.QuerySet):
    pass


_RejectManagerBase = models.Manager.from_queryset(RejectQuerySet)


class RejectManager(_RejectManagerBase):
    pass


class Reject(get_subid_model()):
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        related_name="rejects",
    )
    object_id = models.PositiveBigIntegerField()
    source = GenericForeignKey("content_type", "object_id")

    qty = models.PositiveIntegerField()

    defect = models.CharField(max_length=255)

    hpp = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
    )

    note = models.TextField(blank=True)
    
    created_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = RejectManager()

    class Meta:
        default_permissions = ()
        permissions = [
            # --- Deposit Permissions ---
            ("can_add_defect", "Can add defect"),
            ("can_view_defect", "Can view defect"),
            ("can_change_defect", "Can change defect"),
            ("can_delete_defect", "Can delete defect"),
        ]
        verbose_name = "Reject"
        verbose_name_plural = "Rejects"

    def __str__(self):
        return f"{self.subid} - {self.defect}"