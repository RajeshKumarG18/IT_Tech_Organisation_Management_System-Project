from django.contrib import admin
from .models import Role


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['title', 'level', 'department', 'employee_count', 'created_at']
    list_filter = ['level', 'department']
    search_fields = ['title', 'description', 'responsibilities']
    ordering = ['level', 'title']
    raw_id_fields = ['department']