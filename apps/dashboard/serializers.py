from rest_framework import serializers
from apps.employees.models import Employee
from apps.departments.models import Department
from apps.roles.models import Role


class DashboardStatsSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    total_roles = serializers.IntegerField()


class DepartmentStatsSerializer(serializers.Serializer):
    department_id = serializers.IntegerField()
    department_name = serializers.CharField()
    employee_count = serializers.IntegerField()
    head_name = serializers.CharField(allow_null=True)


class RoleStatsSerializer(serializers.Serializer):
    role_id = serializers.IntegerField()
    role_title = serializers.CharField()
    level = serializers.CharField()
    employee_count = serializers.IntegerField()


class ExecutiveDashboardSerializer(serializers.Serializer):
    stats = DashboardStatsSerializer()
    departments = DepartmentStatsSerializer(many=True)
    roles_by_level = serializers.DictField()
    recent_employees = serializers.ListField()
    organization_structure = serializers.DictField()


class ManagerDashboardSerializer(serializers.Serializer):
    team_size = serializers.IntegerField()
    direct_reports = serializers.ListField()
    department_info = serializers.DictField()
    team_stats = serializers.DictField()


class EmployeeDashboardSerializer(serializers.Serializer):
    employee_info = serializers.DictField()
    reporting_to = serializers.DictField(allow_null=True)
    department_info = serializers.DictField()
    role_info = serializers.DictField()