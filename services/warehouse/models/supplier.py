from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "SupplierQuerySet",
    "SupplierManager",
    "Supplier",
)


class SupplierQuerySet(models.QuerySet):
    pass


_SupplierManagerBase = models.Manager.from_queryset(SupplierQuerySet)  # type: type[SupplierQuerySet]


class SupplierManager(_SupplierManagerBase):
    pass


class Supplier(get_subid_model()):
    name = models.CharField(max_length=255)
    contact_info = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = SupplierManager()

    class Meta:
        default_permissions = ()
        permissions = [
            ("add_supplier", "Can add supplier"),
            ("view_supplier", "Can view supplier"),
            ("change_supplier", "Can change supplier"),
            ("delete_supplier", "Can delete supplier"),
        ]
        verbose_name = "Supplier"
        verbose_name_plural = "Suppliers"

    def __str__(self):
        return self.name
