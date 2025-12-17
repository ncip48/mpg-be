from __future__ import annotations

import logging
from collections import Counter
from typing import TYPE_CHECKING

from django.db import models

# from django.utils.translation import gettext_lazy as _
from core.common.models import get_subid_model
from services.order.models.order_form_detail import OrderFormDetail
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
        related_name="forecasts",
        null=True,
        blank=True,
    )

    # Marketplace
    order = models.ForeignKey(
        "order.Order",
        on_delete=models.CASCADE,
        related_name="forecasts",
        null=True,
        blank=True,
    )

    date_forecast = models.DateField()
    print_status = models.BooleanField(default=False)

    is_stock = models.BooleanField(default=False)
    printer = models.ForeignKey(
        "printer.Printer",
        on_delete=models.CASCADE,
        related_name="forecasts",
        null=True,
        blank=True,
    )
    sku = models.CharField(max_length=255, null=True, blank=True)
    priority_status = models.CharField(
        max_length=20,
        choices=[("reguler", "Reguler"), ("urgent", "Urgent"), ("express", "Express")],
        null=True,
        blank=True,
    )
    estimate_sent = models.DateField(blank=True, null=True)

    created_by = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ForecastManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_forecast", "Can add forecast"),
            ("view_forecast", "Can view forecast"),
            ("change_forecast", "Can change forecast"),
            ("delete_forecast", "Can delete forecast"),
        ]
        verbose_name = "Forecast"
        verbose_name_plural = "Forecasts"

    def __str__(self):
        return f"Forecasting for {self.created_by}"

    @property
    def count_po(self) -> int:
        """
        Count ALL items in OrderFormDetail (PO quantity).

        - If is_stock → use StockItem.quantity
        - Else → count OrderFormDetail rows
        """
        from services.forecast.models import StockItem
        from services.order.models import OrderForm, OrderFormDetail

        if self.is_stock:
            stock_item = StockItem.objects.filter(forecast=self).first()
            return stock_item.quantity if stock_item else 0

        # Detect source
        if self.order_item:
            order_form = OrderForm.objects.filter(order_item=self.order_item).first()
        else:
            order_form = OrderForm.objects.filter(order=self.order).first()

        if not order_form:
            return 0

        details = OrderFormDetail.objects.filter(order_form=order_form)

        return details.count()

    @property
    def details(self) -> list[dict]:
        """
        Normalize and group sizes for both stock and non-stock items:
        - "L MEN"   → "L"
        - "S WOMEN" → "S"
        - "L KIDS"  → "KIDS"
        - "XS GIRL" → "GIRL"
        """
        from services.forecast.models import StockItemSize
        from services.order.models import OrderForm

        def normalize_type(size_text: str) -> str:
            if not size_text:
                return ""

            size_upper = size_text.upper().split()

            # Priority groups
            for keyword in ("KIDS", "GIRL"):
                if keyword in size_upper:
                    return keyword

            # Default to first token (XS, S, M, L, XL, etc.)
            return size_upper[0]

        # -------------------------------
        # CASE 1: STOCK ITEM
        # -------------------------------
        if self.is_stock:
            sizes = StockItemSize.objects.filter(stock_item__forecast=self)

            if not sizes.exists():
                return []

            result: dict[str, int] = {}

            for s in sizes:
                normalized = normalize_type(s.size)
                if not normalized:
                    continue

                result[normalized] = result.get(normalized, 0) + s.qty

            return [{"type": size, "count": count} for size, count in result.items()]

        # -------------------------------
        # CASE 2: NORMAL ORDER
        # -------------------------------
        if self.order_item:
            order_form = OrderForm.objects.filter(order_item=self.order_item).first()
        else:
            order_form = OrderForm.objects.filter(order=self.order).first()

        if not order_form:
            return []

        details = OrderFormDetail.objects.filter(order_form=order_form)

        normalized = (normalize_type(d.shirt_size) for d in details if d.shirt_size)

        counter = Counter(normalized)

        return [{"type": size, "count": count} for size, count in counter.items()]
