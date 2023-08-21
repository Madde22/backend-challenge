from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from user.models import User


class UserAdminConfig(UserAdmin):
    # ordering, list_display, etc..
    list_display = (
        'id', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'last_login')
    search_fields = ('id', 'first_name', 'last_name', 'email')

    model = User
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"), {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "deleted_by")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_email_verified",
                    "is_mobile_verified",
                    "is_deleted",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "deleted_at",
                    "last_login",
                    "date_joined"
                )}),
    )
    readonly_fields = ('date_joined', 'updated_at', 'created_at', 'deleted_at')


admin.site.register(User, UserAdminConfig)
