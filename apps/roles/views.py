from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Role
from .serializers import RoleSerializer, RoleListSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.select_related('department').all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'description']
    ordering_fields = ['level', 'title', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(level=level)
        
        department_id = self.request.query_params.get('department')
        if department_id:
            queryset = queryset.filter(department_id=department_id)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RoleListSerializer
        return RoleSerializer
    
    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        role = self.get_object()
        from apps.employees.serializers import EmployeeListSerializer
        employees = role.employees.all()
        serializer = EmployeeListSerializer(employees, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_level(self, request):
        level = request.query_params.get('level')
        if not level:
            return Response({'error': 'level parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        roles = self.queryset.filter(level=level)
        serializer = RoleListSerializer(roles, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def levels(self, request):
        return Response(Role.LEVEL_CHOICES)