from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.printer.models.printer import Printer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "PrinterSerializer",
)
        
class PrinterSerializer(BaseModelSerializer):
    """
    Serializer for Printer management by superusers.
    Handles CRUD for printer and assignment of permissions.
    """

    class Meta:
        model = Printer
        fields = ['pk', 'name']