from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.viewsets import BaseViewSet
from services.account.models import Role
from services.account.rest.role.serializers import RoleSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "RoleViewSet",
)

class RoleViewSet(BaseViewSet):
    """
    A viewset for viewing and editing roles.
    Accessible only by superusers.
    """
    queryset = Role.objects.all().prefetch_related('permissions')
    serializer_class = RoleSerializer
    lookup_field = "subid"
    search_fields = ["name", "color"]
    required_perms = [
        "account.add_role",
        "account.change_role",
        "account.delete_role",
        "account.view_role",
    ]
    my_tags = ["Roles"]
