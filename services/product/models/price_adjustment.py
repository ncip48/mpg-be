from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.product.models.fabric_type import FabricType
from services.product.models.price_tier import ProductPriceTier

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ProductPriceAdjustmentQuerySet",
    "ProductPriceAdjustmentManager",
    "ProductPriceAdjustment",
)


class ProductPriceAdjustmentQuerySet(models.QuerySet):
    pass


_ProductPriceAdjustmentManagerBase = models.Manager.from_queryset(ProductPriceAdjustmentQuerySet)  # type: type[ProductPriceAdjustmentQuerySet]


class ProductPriceAdjustmentManager(_ProductPriceAdjustmentManagerBase):
    pass


class ProductPriceAdjustment(get_subid_model()):
    """
    ProductPriceAdjustment model
    """
    fabric_type = models.ForeignKey(FabricType, on_delete=models.CASCADE)
    product_price_tier = models.ForeignKey(ProductPriceTier, on_delete=models.CASCADE, related_name="fabric_adjustments")
    extra_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = ProductPriceAdjustmentManager()

    class Meta:
        verbose_name = _("product price adjustmen")
        verbose_name_plural = _("product price adjustmens")

    def __str__(self) -> str:
        return f"{self.fabric_type.name} - {self.product_price_tier.min_qty}-{self.product_price_tier.max_qty or '∞'} - {self.extra_price}"
    
    def final_price(self):
        return self.product_price_tier.base_price + self.extra_price
