from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.product.models.fabric_type import FabricType
from services.product.models.variant_type import ProductVariantType

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "FabricPriceQuerySet",
    "FabricPriceManager",
    "FabricPrice",
)


class FabricPriceQuerySet(models.QuerySet):
    pass


_FabricPriceManagerBase = models.Manager.from_queryset(FabricPriceQuerySet)  # type: type[FabricPriceQuerySet]


class FabricPriceManager(_FabricPriceManagerBase):
    pass


class FabricPrice(get_subid_model()):
    """
    Fixed master price relation between FabricType and ProductVariantType.
    """
    fabric_type = models.ForeignKey(FabricType, on_delete=models.CASCADE, related_name="fabric_prices")
    variant_type = models.ForeignKey(ProductVariantType, on_delete=models.CASCADE, related_name="fabric_prices")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("fabric_type", "variant_type")
        verbose_name = _("fabric price")
        verbose_name_plural = _("fabric prices")

    def __str__(self):
        return f"{self.fabric_type.name} - {self.variant_type.name}: {self.price}"
