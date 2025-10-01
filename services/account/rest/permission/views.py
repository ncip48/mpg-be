from __future__ import annotations
from typing import TYPE_CHECKING
from django.utils.translation import gettext_lazy as _
import logging
from django.contrib.auth.models import Permission
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

__all__ = (
    "PermissionListView",
)

class PermissionListView(APIView):
    """
    A view to list all available permissions in the system.
    Accessible only by superusers.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=["Permissions"],
        operation_description="List all available permissions in the system, grouped by app. Accessible only by superusers.",
        responses={200: "A dictionary of app labels mapping to lists of permissions (pk, name, codename)."}
    )
    def get(self, request, format=None):
        """
        Return a list of all permissions, grouped by app.
        """
        permissions = Permission.objects.all().select_related('content_type')
        grouped_permissions = {}
        for perm in permissions:
            app_label = perm.content_type.app_label
            if app_label not in grouped_permissions:
                grouped_permissions[app_label] = []

            grouped_permissions[app_label].append({
                'pk': perm.id,
                'name': perm.name,
                'codename': f"{app_label}.{perm.codename}"
            })

        return Response(grouped_permissions)

