from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "FabricTypeQuerySet",
    "FabricTypeManager",
    "FabricType",
)


class FabricTypeQuerySet(models.QuerySet):
    pass


_FabricTypeManagerBase = models.Manager.from_queryset(FabricTypeQuerySet)  # type: type[FabricTypeQuerySet]


class FabricTypeManager(_FabricTypeManagerBase):
    pass


class FabricType(get_subid_model()):
    """
    FabricType model
    """

    name = models.CharField(max_length=100, unique=True)
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = FabricTypeManager()

    class Meta:
        default_permissions = ()
        permissions = ()
        verbose_name = _("fabric type")
        verbose_name_plural = _("fabric types")

    def __str__(self) -> str:
        return f"{self.name}: {self.additional_price}"
