from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.utils.translation import gettext_lazy as _

from core.common.serializers import BaseModelSerializer
from services.warehouse.models import (
    Supplier,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("SupplierSerializer",)


class SupplierSerializer(BaseModelSerializer):
    """
    Serializer for Supplier management.
    """

    class Meta:
        model = Supplier
        fields = ["pk", "name", "contact_info"]
