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
    "StoreQuerySet",
    "StoreManager",
    "Store",
)


class StoreQuerySet(models.QuerySet):
    pass


_StoreManagerBase = models.Manager.from_queryset(StoreQuerySet)  # type: type[StoreQuerySet]


class StoreManager(_StoreManagerBase):
    pass


class Store(get_subid_model()):
    """
    Store models 
    """
    name = models.CharField(_("name"), max_length=150, unique=True)
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = StoreManager()

    class Meta:
        verbose_name = _("store")
        verbose_name_plural = _("stores")

    def __str__(self) -> str:
        return self.name
