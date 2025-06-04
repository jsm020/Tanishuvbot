from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {'fields': ('telegram_id', 'password')}),
        ('Personal info', {'fields': ('name', 'gender', 'age', 'latitude', 'longitude')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_banned', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('telegram_id', 'name', 'gender', 'age', 'latitude', 'longitude', 'password1', 'password2'),
        }),
    )
    list_display = ('telegram_id', 'name', 'gender', 'age', 'is_banned', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('telegram_id', 'name')
    ordering = ('telegram_id',)
    filter_horizontal = ('groups', 'user_permissions')

admin.site.register(User, UserAdmin)
