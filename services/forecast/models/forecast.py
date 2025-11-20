from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models

# from django.utils.translation import gettext_lazy as _
from core.common.models import get_subid_model
from services.printer.models.printer import Printer
from services.product.models.fabric_type import FabricType

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ForecastQuerySet",
    "ForecastManager",
    "Forecast",
)


class ForecastQuerySet(models.QuerySet):
    pass


_ForecastManagerBase = models.Manager.from_queryset(ForecastQuerySet)  # type: type[ForecastQuerySet]


class ForecastManager(_ForecastManagerBase):
    pass


class Forecast(get_subid_model()):
    # Konveksi
    order_item = models.ForeignKey(
        "order.OrderItem",
        on_delete=models.CASCADE,
        related_name="order_forms",
        null=True,
        blank=True,
    )

    # Marketplace
    order = models.ForeignKey(
        "order.Order",
        on_delete=models.CASCADE,
        related_name="order_forms",
        null=True,
        blank=True,
    )

    date_forecast = models.DateField()
    print_status = models.BooleanField(default=False)

    created_by = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ForecastManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("view_forecast", "Can view forecast"),
            ("change_forecast", "Can change forecast"),
            ("delete_forecast", "Can delete forecast"),
        ]
        verbose_name = "Forecast"
        verbose_name_plural = "Forecasts"

    def __str__(self):
        return f"Forecasting for {self.created_by}"
