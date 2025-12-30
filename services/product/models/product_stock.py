from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models

# from django.utils.translation import gettext_lazy as _
from core.common.models import get_subid_model
from services.forecast.models.forecast import Forecast
from services.forecast.models.stock_item import StockItem
from services.product.models.product import Product

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ProductStockQuerySet",
    "ProductStockManager",
    "ProductStock",
)


class ProductStockQuerySet(models.QuerySet):
    pass


_ProductStockManagerBase = models.Manager.from_queryset(ProductStockQuerySet)  # type: type[ProductStockQuerySet]


class ProductStockManager(_ProductStockManagerBase):
    pass


class ProductStock(get_subid_model()):
    forecast = models.ForeignKey(
        Forecast,
        on_delete=models.CASCADE,
        related_name="stocks",
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="stocks",
    )
    size = models.CharField(max_length=100)
    qty = models.PositiveIntegerField(default=0)

    objects = ProductStockManager()

    class Meta:
        default_permissions = ()
        permissions = ()
        verbose_name = "Product Stock"
        verbose_name_plural = "Product Stocks"

    def __str__(self):
        return f"{self.product.name} - {self.size} ({self.qty})"
