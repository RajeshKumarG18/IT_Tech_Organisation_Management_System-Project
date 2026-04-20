from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Department
from .serializers import DepartmentSerializer, DepartmentTreeSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related('parent_department', 'head').prefetch_related('sub_departments')
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['name', 'code', 'description']
    ordering_fields = ['name', 'code', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        parent_id = self.request.query_params.get('parent')
        if parent_id:
            queryset = queryset.filter(parent_department_id=parent_id)
        
        root_only = self.request.query_params.get('root_only')
        if root_only and root_only.lower() == 'true':
            queryset = queryset.filter(parent_department__isnull=True)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def tree(self, request):
        root_departments = Department.objects.filter(parent_department__isnull=True).prefetch_related(
            'sub_departments__sub_departments'
        )
        serializer = DepartmentTreeSerializer(root_departments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        department = self.get_object()
        employees = department.employees.filter(status='ACTIVE')
        from apps.employees.serializers import EmployeeListSerializer
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        department = self.get_object()
        
        def get_department_with_children(dept):
            data = DepartmentSerializer(dept).data
            children = dept.sub_departments.all()
            data['children'] = [get_department_with_children(c) for c in children]
            return data
        
        return Response(get_department_with_children(department))