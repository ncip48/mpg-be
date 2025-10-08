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
    
    identity = models.CharField(
        max_length=15,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Auto-generated customer code, e.g., CUSTK-0001"),
    )
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
        return f"{self.identity or ''} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.identity:
            prefix = "CUSTK" if self.source == "konveksi" else "CUSTM"

            # Find the highest code for this source
            latest = (
                Customer.objects.filter(source=self.source, identity__startswith=prefix)
                .aggregate(max_code=models.Max("identity"))
                .get("max_code")
            )

            # Determine next number
            if latest:
                # Extract numeric + optional suffix parts
                import re

                match = re.match(rf"{prefix}-(\d{{4}})([A-Z]?)", latest)
                if match:
                    num_part = int(match.group(1))
                    suffix = match.group(2) or ""

                    if num_part < 9999:
                        num_part += 1
                    else:
                        num_part = 1
                        suffix = chr(ord(suffix) + 1) if suffix else "A"
                else:
                    num_part = 1
                    suffix = ""
            else:
                num_part = 1
                suffix = ""

            # Generate final ID
            self.identity = f"{prefix}-{num_part:04d}{suffix}"

        super().save(*args, **kwargs)
