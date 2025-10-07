from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.product.rest.product.utils import product_image_upload_path

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ProductQuerySet",
    "ProductManager",
    "Product",
)


class ProductQuerySet(models.QuerySet):
    pass


_ProductManagerBase = models.Manager.from_queryset(ProductQuerySet)  # type: type[ProductQuerySet]


class ProductManager(_ProductManagerBase):
    pass


class Product(get_subid_model()):
    """
    Product models 
    """
    name = models.CharField(_("name"), max_length=150, unique=True)
    printer = models.ForeignKey(
        "printer.Printer",
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("printer"),
    )
    store = models.ForeignKey(
        "store.Store",
        on_delete=models.CASCADE,
        related_name="products",
        verbose_name=_("store"),
    )
    sku = models.CharField(_("SKU"), max_length=64, unique=True)
    image = models.ImageField(
        _("image"),
        upload_to=product_image_upload_path,
        blank=True,
        null=True
    )
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = ProductManager()

    class Meta:
        verbose_name = _("product")
        verbose_name_plural = _("products")

    def __str__(self) -> str:
        return f"Product with SKU {self.sku}: {self.name}"
