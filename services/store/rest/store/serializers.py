from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.store.models.store import Store

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "StoreSerializer",
)
        
class StoreSerializer(BaseModelSerializer):
    """
    Serializer for Store management by superusers.
    Handles CRUD for Store and assignment of permissions.
    """

    class Meta:
        model = Store
        fields = ['pk', 'name']