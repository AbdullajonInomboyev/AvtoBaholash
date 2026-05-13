from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ['username', 'full_name', 'role', 'department', 'group', 'is_active', 'date_joined']
    list_filter   = ['role', 'department', 'is_active']
    search_fields = ['username', 'first_name', 'last_name', 'email', 'student_id']
    list_editable = ['role', 'is_active']
    ordering      = ['-date_joined']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('AvtoBaholash ma\'lumotlari', {
            'fields': ('role', 'phone', 'avatar', 'bio', 'student_id',
                       'department', 'group', 'is_accessible')
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('AvtoBaholash ma\'lumotlari', {
            'fields': ('role', 'first_name', 'last_name', 'email',
                       'phone', 'department', 'group', 'student_id')
        }),
    )
