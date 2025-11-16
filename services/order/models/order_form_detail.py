from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models

# from django.utils.translation import gettext_lazy as _
from core.common.models import get_subid_model

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "OrderFormDetailQuerySet",
    "OrderFormDetailManager",
    "OrderFormDetail",
)


class OrderFormDetailQuerySet(models.QuerySet):
    pass


_OrderFormDetailManagerBase = models.Manager.from_queryset(OrderFormDetailQuerySet)  # type: type[OrderFormDetailQuerySet]


class OrderFormDetailManager(_OrderFormDetailManagerBase):
    pass


class OrderFormDetail(get_subid_model()):
    order_form = models.ForeignKey(
        "order.OrderForm",  # assuming your app name is 'order'
        on_delete=models.CASCADE,
        related_name="order_form_details",
    )
    back_name = models.CharField(max_length=100)
    jersey_number = models.CharField(max_length=100)
    shirt_size = models.CharField(max_length=100)
    pants_size = models.CharField(max_length=100)

    objects = OrderFormDetailManager()

    class Meta:
        default_permissions = ()
        permissions = ()
        verbose_name = "Order Form Detail"
        verbose_name_plural = "Order Form Details"

    def __str__(self):
        return f"{self.back_name} - {self.jersey_number} - {self.shirt_size} - {self.pants_size}"
