from rest_framework.permissions import BasePermission


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
