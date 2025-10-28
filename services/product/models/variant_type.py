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
    "ProductVariantTypeQuerySet",
    "ProductVariantTypeManager",
    "ProductVariantType",
)


class ProductVariantTypeQuerySet(models.QuerySet):
    pass


_ProductVariantTypeManagerBase = models.Manager.from_queryset(
    ProductVariantTypeQuerySet
)  # type: type[ProductVariantTypeQuerySet]


class ProductVariantTypeManager(_ProductVariantTypeManagerBase):
    pass


class ProductVariantType(get_subid_model()):
    code = models.CharField(max_length=1, unique=True)
    name = models.CharField(max_length=100)
    note = models.CharField(max_length=255, blank=True, null=True)

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = ProductVariantTypeManager()

    class Meta:
        default_permissions = ()
        permissions = ()
        verbose_name = _("product variant type")
        verbose_name_plural = _("product variant types")

    def __str__(self):
        return f"{self.code} - {self.name}"
