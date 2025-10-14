from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.product.models.variant_type import ProductVariantType

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ProductPriceTierQuerySet",
    "ProductPriceTierManager",
    "ProductPriceTier",
)


class ProductPriceTierQuerySet(models.QuerySet):
    pass


_ProductPriceTierManagerBase = models.Manager.from_queryset(ProductPriceTierQuerySet)  # type: type[ProductPriceTierQuerySet]


class ProductPriceTierManager(_ProductPriceTierManagerBase):
    pass


class ProductPriceTier(get_subid_model()):
    """
    ProductPriceTier model
    """
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE, related_name="price_tiers")
    variant_type = models.ForeignKey(
        ProductVariantType, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="price_tiers"
    )
    min_qty = models.PositiveIntegerField()
    max_qty = models.PositiveIntegerField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2)

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = ProductPriceTierManager()

    class Meta:
        verbose_name = _("price tier")
        verbose_name_plural = _("price tiers")
        ordering = ["min_qty"]
        unique_together = ("product", "variant_type", "min_qty", "max_qty")

    def __str__(self):
        return f"{self.product.name} - {self.variant_type.code if self.variant_type else "(std)"} ({self.min_qty}-{self.max_qty or '∞'})"
