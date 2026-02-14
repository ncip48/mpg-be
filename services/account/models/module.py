from __future__ import annotations

import logging
import random
import string
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.common.models import get_subid_model

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "ModuleQuerySet",
    "ModuleManager",
    "Module",
)


class ModuleQuerySet(models.QuerySet):
    pass


_ModuleManagerBase = models.Manager.from_queryset(ModuleQuerySet)  # type: type[ModuleQuerySet]


class ModuleManager(_ModuleManagerBase):
    pass


def generate_random_code(length=16):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


class Module(get_subid_model()):
    """
    Custom Module model to group permissions.
    """

    code = models.CharField(
        _("code"), max_length=256, default=generate_random_code, unique=True
    )
    description = models.TextField(
        _("description"), blank=True, null=True, max_length=512
    )
    is_active = models.BooleanField(default=True)

    objects = ModuleManager()

    class Meta:
        verbose_name = _("module")
        verbose_name_plural = _("modules")

    def __str__(self) -> str:
        return self.code
