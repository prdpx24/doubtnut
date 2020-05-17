from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from .models import User, UserNotificationHistory


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    list_display = ("username", "first_name", "last_name")
    list_filter = AuthUserAdmin.list_filter + ("type",)
    search_fields = ["username", "email", "first_name", "last_name"]


@admin.register(UserNotificationHistory)
class UserNotificationHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "email_subject", "email_attachment")
    search_fields = ["user__email"]
