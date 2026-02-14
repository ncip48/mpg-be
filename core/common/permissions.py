from rest_framework.permissions import BasePermission
from django.utils.translation import gettext_lazy as _

from services.account.models import Module


class HasRolePermission(BasePermission):
    """
    Custom RBAC permission checker.
    Supports dynamic permissions via get_required_perms()
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        # 🔥 Support dynamic permissions
        if hasattr(view, "get_required_perms"):
            required_perms = view.get_required_perms()
        else:
            required_perms = getattr(view, "required_perms", [])

        # No permission required → allow
        if not required_perms:
            return True

        # At least ONE permission is enough
        return any(request.user.has_perm(perm) for perm in required_perms)


class HasModulePermission(BasePermission):
    message = _("User does not have access to this module.")

    def has_permission(self, request, view) -> bool:
        required_code = getattr(view, "required_module_code", None)

        # kalau view tidak butuh module permission
        if not required_code:
            return True

        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            return False

        if user and user.is_superuser:
            return True

        return Module.objects.filter(
            code=required_code,
            role__users=user,  # <-- relasi reverse
            is_active=True,
        ).exists()
