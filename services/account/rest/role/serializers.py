from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.account.models import Role
from django.contrib.auth.models import Permission
from services.account.rest.permission.serializers import PermissionSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "RoleSerializer",
    "RoleSerializerSimple",
)

class RoleSerializerSimple(BaseModelSerializer):
    class Meta:
        model = Role
        fields = ['pk', 'name', 'color']
        
class RoleSerializer(BaseModelSerializer):
    """
    Serializer for Role management by superusers.
    Handles CRUD for roles and assignment of permissions.
    """
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        required=False
    )

    class Meta:
        model = Role
        fields = ['pk', 'name', 'color', 'permissions']

    def to_representation(self, instance):
        """
        Represent permissions with more detail on read.
        """
        representation = super().to_representation(instance)
        representation['permissions'] = PermissionSerializer(instance.permissions.all(), many=True).data
        return representation