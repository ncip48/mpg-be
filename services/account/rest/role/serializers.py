from __future__ import annotations
from services.account.rest.module.serializers import ModuleSerializerSimple
from services.account.models import Module
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
        fields = ["pk", "name", "color"]


class RoleSerializer(BaseModelSerializer):
    """
    Serializer for Role management by superusers.
    Handles CRUD for roles and assignment of permissions.
    """

    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all(),
        required=False,
    )

    modules = serializers.SlugRelatedField(
        slug_field="subid",
        queryset=Module.objects.all(),
        many=True,
        required=True,
        write_only=True,
    )

    class Meta:
        model = Role
        fields = ["pk", "name", "color", "permissions", "modules"]

    # -------------------------
    # CREATE
    # -------------------------
    def create(self, validated_data):
        modules = validated_data.pop("modules", [])
        permissions = validated_data.pop("permissions", [])

        role = super().create(validated_data)

        role.module.set(modules)
        role.permissions.set(permissions)

        return role

    # -------------------------
    # UPDATE
    # -------------------------
    def update(self, instance, validated_data):
        modules = validated_data.pop("modules", None)
        permissions = validated_data.pop("permissions", None)

        instance = super().update(instance, validated_data)

        if modules is not None:
            instance.module.set(modules)

        if permissions is not None:
            instance.permissions.set(permissions)

        return instance

    # -------------------------
    # READ REPRESENTATION
    # -------------------------
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        representation["permissions"] = PermissionSerializer(
            instance.permissions.all(), many=True
        ).data

        representation["modules"] = ModuleSerializerSimple(
            instance.module.all(), many=True
        ).data

        return representation
