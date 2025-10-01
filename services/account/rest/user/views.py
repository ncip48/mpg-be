from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from core.common.viewsets import BaseViewSet
from services.account.models.user import User
from services.account.rest.user.serializers import UserSerializer

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "UserViewSet",
)

class UserViewSet(BaseViewSet):
    """
    A viewset for viewing and editing users.
    Accessible only by superusers.
    """
    queryset = User.objects.all().prefetch_related('roles').order_by('id')
    serializer_class = UserSerializer
    lookup_field = "subid"
    search_fields = ["first_name", "last_name", "email",]
    required_perms = ["account.add_user", "account.change_user", "account.delete_user", "account.view_user"]
    my_tags = ["Users"]
