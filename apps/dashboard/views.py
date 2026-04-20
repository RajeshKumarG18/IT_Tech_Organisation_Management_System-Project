from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta

from apps.employees.models import Employee
from apps.departments.models import Department
from apps.roles.models import Role
from apps.accounts.models import OrganizationLevel


class DashboardViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        user = request.user
        
        if user.user_type == 'ADMIN' or user.is_superuser:
            return self.executive_dashboard(request)
        elif user.user_type == 'EXECUTIVE':
            return self.executive_dashboard(request)
        elif user.user_type == 'MANAGER':
            return self.manager_dashboard(request)
        else:
            return self.employee_dashboard(request)
    
    def executive_dashboard(self, request):
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(status='ACTIVE').count()
        total_departments = Department.objects.count()
        total_roles = Role.objects.count()
        
        departments = Department.objects.annotate(
            employee_count=Count('employees')
        ).values('id', 'name', 'employee_count').order_by('-employee_count')[:10]
        
        by_level = list(
            Employee.objects.values('role__level')
            .annotate(count=Count('id'))
        )
        
        levels_data = {}
        for level_choice in Role.LEVEL_CHOICES:
            level_key = level_choice[0]
            level_name = level_choice[1]
            count = next((item['count'] for item in by_level if item['role__level'] == level_key), 0)
            levels_data[level_name] = count
        
        recent = Employee.objects.select_related('department', 'role').order_by('-created_at')[:5]
        recent_data = [
            {
                'id': e.id,
                'name': e.full_name,
                'department': e.department.name,
                'role': e.role.title,
                'date_joined': e.date_of_joining,
            }
            for e in recent
        ]
        
        org_levels = OrganizationLevel.objects.all().values('display_name', 'level_order')
        
        return Response({
            'type': 'executive',
            'stats': {
                'total_employees': total_employees,
                'active_employees': active_employees,
                'total_departments': total_departments,
                'total_roles': total_roles,
            },
            'departments': list(departments),
            'roles_by_level': levels_data,
            'recent_employees': recent_data,
            'org_levels': list(org_levels),
        })
    
    def manager_dashboard(self, request):
        user = request.user
        
        if not user.employee:
            return Response({'error': 'Employee profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        employee = user.employee
        direct_reports = employee.subordinates.all()
        
        direct_reports_data = [
            {
                'id': e.id,
                'name': e.full_name,
                'role': e.role.title,
                'status': e.status,
                'department': e.department.name,
            }
            for e in direct_reports
        ]
        
        total_team_size = employee.get_total_team_size()
        
        return Response({
            'type': 'manager',
            'team_size': total_team_size,
            'direct_reports_count': direct_reports.count(),
            'direct_reports': direct_reports_data,
            'department': {
                'id': employee.department.id,
                'name': employee.department.name,
            },
            'employee': {
                'id': employee.id,
                'name': employee.full_name,
                'role': employee.role.title,
            }
        })
    
    def employee_dashboard(self, request):
        user = request.user
        
        if not user.employee:
            return Response({'error': 'Employee profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        employee = user.employee
        
        reporting_to = None
        if employee.reporting_manager:
            reporting_to = {
                'id': employee.reporting_manager.id,
                'name': employee.reporting_manager.full_name,
                'role': employee.reporting_manager.role.title,
                'email': employee.reporting_manager.email,
            }
        
        return Response({
            'type': 'employee',
            'employee': {
                'id': employee.id,
                'employee_id': employee.employee_id,
                'name': employee.full_name,
                'email': employee.email,
                'phone': employee.phone,
                'date_of_joining': employee.date_of_joining,
            },
            'department': {
                'id': employee.department.id,
                'name': employee.department.name,
                'code': employee.department.code,
            },
            'role': {
                'id': employee.role.id,
                'title': employee.role.title,
                'level': employee.role.level,
                'level_display': employee.get_org_level(),
            },
            'reporting_to': reporting_to,
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def org_chart_data(request):
    employees = Employee.objects.filter(status='ACTIVE').select_related(
        'department', 'role', 'reporting_manager'
    )
    
    def build_node(emp):
        return {
            'id': emp.id,
            'employee_id': emp.employee_id,
            'name': emp.full_name,
            'email': emp.email,
            'title': emp.role.title,
            'department': emp.department.name,
            'level': emp.role.level,
            'level_display': emp.get_org_level(),
            'profile_image': emp.profile_image.url if emp.profile_image else None,
            'children': []
        }
    
    node_map = {}
    roots = []
    
    for emp in employees:
        node_map[emp.id] = build_node(emp)
    
    for emp in employees:
        node = node_map[emp.id]
        if emp.reporting_manager:
            parent_node = node_map.get(emp.reporting_manager.id)
            if parent_node:
                parent_node['children'].append(node)
        else:
            roots.append(node)
    
    return Response({
        'roots': roots,
        'total_nodes': len(node_map),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def reports_structure(request):
    user = request.user
    
    if not user.employee:
        return Response({'error': 'Employee profile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    employee = user.employee
    
    def build_tree(emp):
        return {
            'id': emp.id,
            'name': emp.full_name,
            'role': emp.role.title,
            'level': emp.role.level,
            'status': emp.status,
            'children': [build_tree(sub) for sub in emp.subordinates.filter(status='ACTIVE')]
        }
    
    tree = build_tree(employee)
    
    return Response(tree)