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
    "PrinterQuerySet",
    "PrinterManager",
    "Printer",
)


class PrinterQuerySet(models.QuerySet):
    pass


_PrinterManagerBase = models.Manager.from_queryset(PrinterQuerySet)  # type: type[PrinterQuerySet]


class PrinterManager(_PrinterManagerBase):
    pass


class Printer(get_subid_model()):
    """
    Printer models 
    """
    name = models.CharField(_("name"), max_length=150, unique=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = PrinterManager()

    class Meta:
        verbose_name = _("printer")
        verbose_name_plural = _("printers")

    def __str__(self) -> str:
        return self.name
