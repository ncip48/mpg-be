from rest_framework.permissions import BasePermission

class HasRolePermission(BasePermission):
    """
    Custom RBAC permission checker.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        required_perms = getattr(view, "required_perms", [])

        if not required_perms:
            return True
        
        for perm in required_perms:
            has_perm = request.user.has_perm(perm)
            if has_perm:
                return True
        return False
