from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.account.models import Module
from django.contrib.auth.models import Permission
from services.account.rest.permission.serializers import PermissionSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ModuleSerializer",
    "ModuleSerializerSimple",
)


class ModuleSerializerSimple(BaseModelSerializer):
    class Meta:
        model = Module
        fields = ["pk", "code", "description"]


class ModuleSerializer(BaseModelSerializer):
    """
    Serializer for Module management by superusers.
    Handles CRUD for Modules and assignment of permissions.
    """

    code = serializers.CharField()

    class Meta:
        model = Module
        fields = ["pk", "code", "description", "is_active"]

    def get_fields(self):
        fields = super().get_fields()

        request = self.context.get("request")
        if request and request.method in ["PUT", "PATCH"]:
            fields["code"].read_only = True

        return fields
