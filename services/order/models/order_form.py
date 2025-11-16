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
    "OrderFormQuerySet",
    "OrderFormManager",
    "OrderForm",
)


class OrderFormQuerySet(models.QuerySet):
    pass


_OrderFormManagerBase = models.Manager.from_queryset(OrderFormQuerySet)  # type: type[OrderFormQuerySet]


class OrderFormManager(_OrderFormManagerBase):
    pass


class OrderForm(get_subid_model()):
    order_item = models.ForeignKey(
        "order.OrderItem",  # assuming your app name is 'order'
        on_delete=models.CASCADE,
        related_name="order_forms",
    )
    form_type = models.CharField(
        max_length=20,
        choices=[("konveksi", "Konveksi"), ("marketplace", "Marketplace")],
    )
    team_name = models.CharField(max_length=255, null=True, blank=True)

    design_front = models.FileField(
        upload_to="designs/", max_length=255, null=True, blank=True
    )
    design_back = models.FileField(
        upload_to="designs/", max_length=255, null=True, blank=True
    )

    jersey_pattern = models.CharField(max_length=255, null=True, blank=True)
    jersey_type = models.CharField(max_length=255, null=True, blank=True)
    jersey_cutting = models.CharField(max_length=255, null=True, blank=True)
    collar_type = models.CharField(max_length=255, null=True, blank=True)
    pants_cutting = models.CharField(max_length=255, null=True, blank=True)

    promo_logo_ez = models.CharField(max_length=255, null=True, blank=True)
    tag_size_bottom = models.CharField(max_length=255, null=True, blank=True)
    tag_size_shoulder = models.CharField(max_length=255, null=True, blank=True)

    logo_chest_right = models.FileField(
        upload_to="logos/", max_length=255, null=True, blank=True
    )
    logo_center = models.FileField(
        upload_to="logos/", max_length=255, null=True, blank=True
    )
    logo_chest_left = models.FileField(
        upload_to="logos/", max_length=255, null=True, blank=True
    )
    logo_back = models.FileField(
        upload_to="logos/", max_length=255, null=True, blank=True
    )
    logo_pants = models.FileField(
        upload_to="logos/", max_length=255, null=True, blank=True
    )

    created_by = models.ForeignKey("account.User", on_delete=models.SET_NULL, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = OrderFormManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("view_orderform", "Can view order form"),
            ("add_orderform", "Can add order form"),
            ("change_orderform", "Can change order form"),
            ("delete_orderform", "Can delete order form"),
        ]
        verbose_name = "Order Form"
        verbose_name_plural = "Order Forms"

    def __str__(self):
        return f"Form for ({self.team_name or 'No Team Name'})"
