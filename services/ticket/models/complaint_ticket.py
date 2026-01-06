from __future__ import annotations

import logging
import random
import time
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ComplaintTicketQuerySet",
    "ComplaintTicketManager",
    "ComplaintTicket",
)


class ComplaintTicketQuerySet(models.QuerySet):
    pass


_ComplaintTicketManagerBase = models.Manager.from_queryset(ComplaintTicketQuerySet)  # type: type[ComplaintTicketQuerySet]


class ComplaintTicketManager(_ComplaintTicketManagerBase):
    pass


def generate_order_id():
    ts = int(time.time() * 1000)
    rand = random.randint(100, 999)
    return f"TK-{ts}-{rand}"


class ComplaintTicket(get_subid_model()):
    STATUS_CHOICES = [
        ("WAITING_QC", "Menunggu QC"),
        ("QC_ACCEPTED", "Diterima QC"),
        ("QC_REJECTED", "Ditolak QC"),
        ("WAITING_APPROVAL", "Menunggu Approval"),
        ("APPROVED", "Disetujui"),
        ("IN_PROGRESS", "Diproses Produksi"),
        ("CLOSED", "Closed"),
    ]

    COMPLAINT_TYPE = [
        ("SIZE", "Salah Ukuran"),
        ("DEFECT", "Cacat"),
        ("COLOR", "Warna Tidak Sesuai"),
        ("DESIGN", "Salah Design"),
    ]

    REQUEST_TYPE = [
        ("REPLACE", "Ganti Barang"),
        ("REPAIR", "Perbaikan"),
        ("REFUND", "Refund"),
    ]

    identifier = models.CharField(
        max_length=20, null=True, blank=True, default=generate_order_id
    )

    order = models.ForeignKey(
        "order.Order",
        on_delete=models.SET_NULL,
        null=True,
    )

    customer_name = models.CharField(max_length=255)
    received_date = models.DateField()

    complaint_type = models.CharField(max_length=20, choices=COMPLAINT_TYPE)
    customer_request = models.CharField(max_length=20, choices=REQUEST_TYPE)

    status = models.CharField(
        max_length=30, choices=STATUS_CHOICES, default="WAITING_QC"
    )

    evidence_image = models.ImageField(
        upload_to="complaints/",
        null=True,
        blank=True,
    )

    created_by = models.ForeignKey(
        "account.User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="complaints_created",
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = ComplaintTicketManager()

    class Meta:
        verbose_name = _("ticket complaint")
        verbose_name_plural = _("ticket complaints")
        default_permissions = ()
        permissions = [
            # --- Marketplace Order Permissions ---
            ("can_add_complaint_ticket", "Can add complaint ticket"),
            ("can_view_complaint_ticket", "Can view complaint ticket"),
            ("can_change_complaint_ticket", "Can change complaint ticket"),
            ("can_delete_complaint_ticket", "Can delete complaint ticket"),
        ]

    def __str__(self) -> str:
        return self.order
