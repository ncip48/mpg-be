from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.contrib.auth.models import Permission
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "RoleQuerySet",
    "RoleManager",
    "Role",
)


class RoleQuerySet(models.QuerySet):
    pass


_RoleManagerBase = models.Manager.from_queryset(RoleQuerySet)  # type: type[RoleQuerySet]


class RoleManager(_RoleManagerBase):
    pass


class Role(get_subid_model()):
    """
    Custom Role model to group permissions.
    """
    name = models.CharField(_("name"), max_length=150, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        blank=True,
    )
    color = models.CharField(
        max_length=7,
        default="#FFFFFF",
        help_text=_("Color for the role in UI"),
    )
    created = models.DateTimeField(_("created"), auto_now_add=True)
    updated = models.DateTimeField(_("updated"), auto_now=True)

    objects = RoleManager()

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")

    def __str__(self) -> str:
        return self.name
