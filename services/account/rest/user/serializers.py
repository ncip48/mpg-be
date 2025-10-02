from __future__ import annotations
from rest_framework import serializers
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.serializers import BaseModelSerializer
from services.account.models import User, Role
from services.account.rest.role.serializers import RoleSerializerSimple

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ProfileSerializer",
    "UserSerializer",
)

class ProfileSerializer(BaseModelSerializer):
    """
    Serializer for the User model, including roles and aggregated permissions.
    """
    roles = RoleSerializerSimple(many=True, read_only=True)
    permissions = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    is_admin = serializers.BooleanField(read_only=True)
    is_registered = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = [
            'pk', 'first_name', 'last_name', 'email', 'photo',
            'is_admin', 'is_registered', 'is_active', 'is_superuser', 'roles',
            'permissions', 'modules'
        ]

    def get_permissions(self, obj):
        """
        Returns a list of all permission strings for the user.
        """
        return sorted(list(obj.get_all_permissions()))

    def get_modules(self, obj):
        """
        Returns a list of app labels (modules) the user has access to.
        """
        permissions = obj.get_all_permissions()
        modules = set(p.split('.')[0] for p in permissions)
        return sorted(list(modules))

class UserSerializer(BaseModelSerializer):
    """
    Serializer for User management by superusers.
    Handles CRUD for users and assignment of roles.
    """
    # Accept roles as a list of subids (assume subid is a unique field on Role)
    roles = serializers.SlugRelatedField(
        many=True,
        slug_field='subid',
        queryset=Role.objects.all(),
        required=False
    )
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['pk', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser', 'roles', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def to_representation(self, instance):
        """
        Represent roles with more detail on read.
        """
        representation = super().to_representation(instance)
        representation['roles'] = RoleSerializerSimple(instance.roles.all(), many=True).data
        return representation

    def create(self, validated_data):
        roles_data = validated_data.pop('roles', None)
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)

        if password:
            user.set_password(password)
        
        user.save() # Save user before setting many-to-many relationship

        if roles_data:
            user.roles.set(roles_data)
        
        return user

    def update(self, instance, validated_data):
        roles_data = validated_data.pop('roles', None)
        password = validated_data.pop('password', None)

        # Update user fields using the default update method
        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)
            instance.save()

        if roles_data is not None:
            instance.roles.set(roles_data)

        return instance