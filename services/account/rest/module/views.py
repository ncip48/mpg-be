from __future__ import annotations
from rest_framework.exceptions import PermissionDenied
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.viewsets import BaseViewSet
from services.account.models import Module
from services.account.rest.module.serializers import (
    ModuleSerializer,
    ModuleSerializerSimple,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = ("ModuleViewSet",)


class ModuleViewSet(BaseViewSet):
    """
    A viewset for viewing and editing Modules.
    Accessible only by superusers.
    """

    my_tags = ["Modules"]
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    lookup_field = "subid"
    search_fields = ["code", "description"]
    filterset_fields = ["is_active"]
    ordering = ["-pk"]
    required_perms = [
        "account.add_module",
        "account.change_module",
        "account.delete_module",
        "account.view_module",
    ]
    serializer_map = {
        "autocomplete": ModuleSerializerSimple,
    }

    def destroy(self, request, *args, **kwargs):
        raise PermissionDenied
