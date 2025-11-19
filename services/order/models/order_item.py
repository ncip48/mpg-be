from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model
from services.customer.models.customer import Customer
from services.deposit.models import Deposit
from services.order.models.order import Order
from services.product.models.fabric_type import FabricType
from services.product.models.product import Product
from services.product.models.variant_type import ProductVariantType

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "OrderItemQuerySet",
    "OrderItemManager",
    "OrderItem",
)


class OrderItemQuerySet(models.QuerySet):
    pass


_OrderItemManagerBase = models.Manager.from_queryset(OrderItemQuerySet)  # type: type[OrderItemQuerySet]


class OrderItemManager(_OrderItemManagerBase):
    pass


class OrderItem(get_subid_model()):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="items", null=True, blank=True
    )
    deposit = models.ForeignKey(
        Deposit, on_delete=models.CASCADE, related_name="items", null=True, blank=True
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="items")
    fabric_type = models.ForeignKey(
        FabricType, on_delete=models.CASCADE, related_name="items"
    )
    variant_type = models.ForeignKey(
        ProductVariantType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
    )
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.PositiveIntegerField()

    objects = OrderItemManager()

    class Meta:
        default_permissions = ()
        permissions = ()

    def __str__(self):
        return (
            f"OrderItem {self.pk} "
            f"(Order: {self.order.pk}, "
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
