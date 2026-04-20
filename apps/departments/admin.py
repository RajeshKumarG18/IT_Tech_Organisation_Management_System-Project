from django.contrib import admin
from .models import Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'parent_department', 'created_at']
    list_filter = ['parent_department']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    raw_id_fields = ['parent_department']