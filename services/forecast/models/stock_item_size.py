from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models

# from django.utils.translation import gettext_lazy as _
from core.common.models import get_subid_model
from services.forecast.models.stock_item import StockItem

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "StockItemSizeQuerySet",
    "StockItemSizeManager",
    "StockItemSize",
)


class StockItemSizeQuerySet(models.QuerySet):
    pass


_StockItemSizeManagerBase = models.Manager.from_queryset(StockItemSizeQuerySet)  # type: type[StockItemSizeQuerySet]


class StockItemSizeManager(_StockItemSizeManagerBase):
    pass


class StockItemSize(get_subid_model()):
    stock_item = models.ForeignKey(
        StockItem,
        on_delete=models.CASCADE,
        related_name="stock_item_sizes",
    )
    size = models.CharField(max_length=100)

    objects = StockItemSizeManager()

    class Meta:
        default_permissions = ()
        permissions = ()
        verbose_name = "Stock Item Size"
        verbose_name_plural = "Stock Item Sizes"

    def __str__(self):
        return f"{self.stock_item} - {self.size}"
