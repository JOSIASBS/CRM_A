from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):

    list_display = (
        'username', 'email', 'role', 'department', 'is_staff'
    )

    list_filter = (
        'role', 'department', 'is_staff'
    )

    fieldsets = UserAdmin.fieldsets + (
        ('Información laboral', {
            'fields': ('role', 'department','fecha_contratacion')
        }),
        ('Datos extra', {
            'fields': ('phone', 'address', 'avatar')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Información laboral', {
            'fields': ('role', 'department')
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'total_employees')

    def total_employees(self, obj):
        return obj.employees.count()

    total_employees.short_description = "Empleados"
