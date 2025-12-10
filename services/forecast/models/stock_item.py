from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.forecast.models import Forecast
from services.product.models.fabric_type import FabricType
from services.product.models.product import Product
from services.product.models.variant_type import ProductVariantType

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "StockItemQuerySet",
    "StockItemManager",
    "StockItem",
)


class StockItemQuerySet(models.QuerySet):
    pass


_StockItemManagerBase = models.Manager.from_queryset(StockItemQuerySet)  # type: type[StockItemQuerySet]


class StockItemManager(_StockItemManagerBase):
    pass


class StockItem(get_subid_model()):
    forecast = models.ForeignKey(
        Forecast,
        on_delete=models.CASCADE,
        related_name="stock_items",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="stock_items"
    )
    fabric_type = models.ForeignKey(
        FabricType, on_delete=models.CASCADE, related_name="stock_items"
    )
    variant_type = models.ForeignKey(
        ProductVariantType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="stock_items",
    )
    # price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()

    objects = StockItemManager()

    class Meta:
        default_permissions = ()
        permissions = ()

    def __str__(self):
        return (
            f"StockItem {self.pk} "
            f"(Forecast: {self.forecast.pk}, "
            f"Product: {self.product}, "
            f"Quantity: {self.quantity}, "
            f"Price: {self.price})"
        )

    @property
    def subtotal(self):
        variant_type = getattr(self, "variant_type", None)
        fabric_type = getattr(self, "fabric_type", None)
        price = getattr(self, "price", 0)
        qty = getattr(self, "quantity", 0)

        fabric_price_obj = None
        if variant_type and fabric_type:
            fabric_price_qs = getattr(variant_type, "fabric_prices", None)
            if fabric_price_qs is not None:
                fabric_price_qs_filtered = fabric_price_qs.filter(
                    fabric_type=fabric_type, variant_type=variant_type
                )
                fabric_price_obj = fabric_price_qs_filtered.first()
        if fabric_price_obj and hasattr(fabric_price_obj, "price"):
            return qty * price + fabric_price_obj.price
        return qty * price
