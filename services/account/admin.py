from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from services.account.models.user import User
from services.account.models.role import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "created", "updated")
    search_fields = ("name",)
    filter_horizontal = ("permissions",)  # nice multi-select widget
    ordering = ("name",)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ("email", "username", "fullname", "is_active", "is_staff", "is_superuser", "created", "updated")
    list_filter = ("is_active", "is_staff", "is_superuser", "roles")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("email",)

    # ✅ Adjust fieldsets to support custom fields
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("username", "first_name", "last_name", "photo")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "roles", "user_permissions")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    # ✅ Add fields for add-user form
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "first_name", "last_name", "password1", "password2"),
            },
        ),
    )
