from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib.auth.models import AbstractUser, Permission, UserManager as DjangoUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model

if TYPE_CHECKING:
    from services.account.models.role import Role

logger = logging.getLogger(__name__)

__all__ = (
    "UserQuerySet",
    "UserManager",
    "User",
)


class UserQuerySet(models.QuerySet):
    pass


# ✅ Use Django's UserManager as base
_UserManagerBase = DjangoUserManager.from_queryset(UserQuerySet)  # type: ignore


class UserManager(_UserManagerBase):
    pass


class User(AbstractUser, get_subid_model()):
    """
    Custom User model that uses roles for permissions.
    """
    email = models.EmailField(_("email address"), unique=True)
    photo = models.ImageField(upload_to="user_photos/", null=True, blank=True)
    roles: models.ManyToManyField["Role"]
    roles = models.ManyToManyField(
        "account.Role",
        verbose_name=_("roles"),
        blank=True,
        related_name="users",
    )

    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = UserManager()

    # Use email for authentication instead of username
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    @property
    def is_registered(self) -> bool:
        return self.pk is not None
    
    @property
    def fullname(self) -> str:
        """
        Returns the user's full name (first name and last name).
        """
        return f"{self.first_name} {self.last_name}".strip()

    def get_all_permissions(self, obj=None) -> set[str]:
        """
        Returns a set of permission strings that the user has.
        This includes permissions from their roles and direct user permissions.
        """
        permissions: set[str] = set()
        if not self.is_active or self.is_anonymous:
            return permissions

        if self.is_superuser:
            return {
                f"{p.content_type.app_label}.{p.codename}"
                for p in Permission.objects.all()
            }

        # Get permissions from roles
        for role in self.roles.all():
            role_permissions = role.permissions.select_related("content_type")
            permissions.update(
                f"{p.content_type.app_label}.{p.codename}" for p in role_permissions
            )

        return permissions

    def has_perm(self, perm: str, obj=None) -> bool:
        """
        Checks if the user has a specific permission ('app_label.codename').
        """
        if self.is_active and self.is_superuser:
            return True
        return perm in self.get_all_permissions()

    def has_module_perms(self, app_label: str) -> bool:
        """
        Checks if the user has any permissions for a given app.
        """
        if self.is_active and self.is_superuser:
            return True
        return any(p.startswith(app_label) for p in self.get_all_permissions())
