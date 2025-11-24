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
    "SewerQuerySet",
    "SewerManager",
    "Sewer",
)


class SewerQuerySet(models.QuerySet):
    pass


_SewerManagerBase = models.Manager.from_queryset(SewerQuerySet)  # type: type[SewerQuerySet]


class SewerManager(_SewerManagerBase):
    pass


class Sewer(get_subid_model()):
    """
    Sewer models
    """

    name = models.CharField(_("name"), max_length=150, unique=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = SewerManager()

    class Meta:
        verbose_name = _("sewer")
        verbose_name_plural = _("sewers")

    def __str__(self) -> str:
        return self.name
