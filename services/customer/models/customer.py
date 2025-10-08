from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "CustomerQuerySet",
    "CustomerManager",
    "Customer",
)


class CustomerQuerySet(models.QuerySet):
    pass


_CustomerManagerBase = models.Manager.from_queryset(CustomerQuerySet)  # type: type[CustomerQuerySet]


class CustomerManager(_CustomerManagerBase):
    pass


class Customer(get_subid_model()):
    """
    Customer models 
    """
    CUSTOMER_SOURCE_CHOICES = [
        ("konveksi", "Konveksi"),
        ("marketplace", "Marketplace"),
    ]
    
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=50)
    address = models.TextField()
    source = models.CharField(
        max_length=20,
        choices=CUSTOMER_SOURCE_CHOICES,
    )
    
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = CustomerManager()

    class Meta:
        verbose_name = _("customer")
        verbose_name_plural = _("customers")

    def __str__(self) -> str:
        return self.name
