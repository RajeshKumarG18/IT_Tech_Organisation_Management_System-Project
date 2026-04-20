from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    employee_count = serializers.IntegerField(read_only=True)
    head_name = serializers.SerializerMethodField()
    parent_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'description', 'parent_department', 
                  'parent_name', 'head', 'head_name', 'employee_count',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_head_name(self, obj):
        head = obj.head
        if head:
            return head.full_name
        return None
    
    def get_parent_name(self, obj):
        if obj.parent_department:
            return obj.parent_department.name
        return None


class DepartmentTreeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    employee_count = serializers.IntegerField(read_only=True)
    head_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Department
        fields = ['id', 'name', 'code', 'head_name', 'employee_count', 'children']
    
    def get_children(self, obj):
        children = obj.sub_departments.all()
        return DepartmentTreeSerializer(children, many=True).data
    
    def get_head_name(self, obj):
        head = obj.head
        if head:
            return head.full_name
        return None