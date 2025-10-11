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
    "ProductTypeQuerySet",
    "ProductTypeManager",
    "ProductType",
)


class ProductTypeQuerySet(models.QuerySet):
    pass


_ProductTypeManagerBase = models.Manager.from_queryset(ProductTypeQuerySet)  # type: type[ProductTypeQuerySet]


class ProductTypeManager(_ProductTypeManagerBase):
    pass


class ProductType(get_subid_model()):
    """
    ProductType model
    """
    code = models.CharField(_("product type code"), max_length=50, unique=True)
    code_description = models.CharField(_("product type code description"), max_length=150)
    description = models.CharField(_("product type description"), max_length=150)

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = ProductTypeManager()

    class Meta:
        verbose_name = _("product type")
        verbose_name_plural = _("product types")

    def __str__(self) -> str:
        return f"{self.code} - {self.description}"
