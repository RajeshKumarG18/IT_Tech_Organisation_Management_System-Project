from rest_framework import serializers
from .models import Role


class RoleSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    employee_count = serializers.IntegerField(read_only=True)
    display_level = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'title', 'level', 'display_level', 'department', 'department_name', 
                  'description', 'responsibilities', 'employee_count',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_display_level(self, obj):
        return dict(Role.LEVEL_CHOICES).get(obj.level, obj.level)


class RoleListSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    display_level = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'title', 'level', 'display_level', 'department_name', 'employee_count']
    
    def get_display_level(self, obj):
        return dict(Role.LEVEL_CHOICES).get(obj.level, obj.level)