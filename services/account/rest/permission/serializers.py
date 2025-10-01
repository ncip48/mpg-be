from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from django.contrib.auth.models import Permission
from core.common.serializers import BaseModelSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "PermissionSerializer",
)

class PermissionSerializer(BaseModelSerializer):
    """
    Serializer for the Permission model.
    """
    class Meta:
        model = Permission
        fields = ['pk', 'name', 'codename']