from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'username', 'is_staff', 'is_active']
    ordering = ['email']
    search_fields = ['email', 'username']

    # Don't redefine fieldsets unless you're adding NEW fields
    # fieldsets = UserAdmin.fieldsets + (
    #     (None, {'fields': ('email',)}),
    # )

    # Same here, avoid redefining add_fieldsets unless needed
    # add_fieldsets = UserAdmin.add_fieldsets + (
    #     (None, {'fields': ('email',)}),
    # )

admin.site.register(CustomUser, CustomUserAdmin)
