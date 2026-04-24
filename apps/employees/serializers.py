from django.conf import settings
from rest_framework import serializers
from .models import Employee, WorkLog, Attendance, Candidate, AptitudeTest, Question, TestAttempt, Answer, ProctoringLog, Notification, LeaveRequest, Announcement, Event, Project, Payroll
from apps.roles.serializers import RoleListSerializer
from apps.departments.serializers import DepartmentSerializer


class EmployeeSerializer(serializers.ModelSerializer):
    role_details = RoleListSerializer(source='role', read_only=True)
    department_details = DepartmentSerializer(source='department', read_only=True)
    reporting_manager_name = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'user', 'first_name', 'last_name', 'full_name',
                  'email', 'phone', 'department', 'department_details', 'role', 
                  'role_details', 'reporting_manager', 'reporting_manager_name',
                  'date_of_joining', 'status', 'address', 'date_of_birth',
                  'emergency_contact', 'profile_image', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_reporting_manager_name(self, obj):
        if obj.reporting_manager:
            return obj.reporting_manager.full_name
        return None
    
    def create(self, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.create_user(**user_data)
            validated_data['user'] = user
        return super().create(validated_data)


class EmployeeListSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    role_title = serializers.CharField(source='role.title', read_only=True)
    reporting_manager_name = serializers.SerializerMethodField()
    org_level = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'full_name', 'email', 'phone', 'department_name',
                  'role_title', 'org_level', 'reporting_manager', 'reporting_manager_name',
                  'date_of_joining', 'status', 'profile_image']
    
    def get_reporting_manager_name(self, obj):
        if obj.reporting_manager:
            return obj.reporting_manager.full_name
        return None
    
    def get_org_level(self, obj):
        return obj.get_org_level()


class EmployeeDetailSerializer(serializers.ModelSerializer):
    role_details = RoleListSerializer(source='role', read_only=True)
    department_details = DepartmentSerializer(source='department', read_only=True)
    reporting_manager = EmployeeListSerializer(read_only=True)
    subordinates = serializers.SerializerMethodField()
    hierarchy_path = serializers.SerializerMethodField()
    full_name = serializers.CharField(read_only=True)
    total_team_size = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'first_name', 'last_name', 'full_name',
                  'email', 'phone', 'department', 'department_details', 'role',
                  'role_details', 'reporting_manager', 'subordinates', 'hierarchy_path',
                  'date_of_joining', 'status', 'address', 'date_of_birth',
                  'emergency_contact', 'profile_image', 'created_at', 'updated_at',
                  'total_team_size']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_subordinates(self, obj):
        subordinates = obj.subordinates.all()
        return EmployeeListSerializer(subordinates, many=True).data
    
    def get_hierarchy_path(self, obj):
        path = obj.get_hierarchy_path()
        return EmployeeListSerializer(path, many=True).data


class EmployeeCreateSerializer(serializers.ModelSerializer):
    user_data = serializers.DictField(write_only=True, required=False)
    
    class Meta:
        model = Employee
        fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone',
                  'department', 'role', 'reporting_manager', 'date_of_joining',
                  'status', 'address', 'date_of_birth', 'emergency_contact',
                  'profile_image', 'user_data']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user_data', {})
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        username = user_data.get('username', validated_data['email'].split('@')[0])
        password = user_data.get('password', 'ChangeMe123!')
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': validated_data['email'],
                'first_name': validated_data['first_name'],
                'last_name': validated_data['last_name'],
                'phone': validated_data.get('phone', ''),
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
        
        validated_data['user'] = user
        return super().create(validated_data)


# ====================== RECRUITMENT SERIALIZERS ======================

class CandidateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Candidate
        fields = ['id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
                  'candidate_type', 'resume', 'linkedin_profile', 'github_profile',
                  'years_experience', 'current_company', 'position_applied', 'status',
                  'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'status']


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'question_text', 'category', 'difficulty', 
                  'option_a', 'option_b', 'option_c', 'option_d', 'marks']


class AptitudeTestSerializer(serializers.ModelSerializer):
    questions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = AptitudeTest
        fields = ['id', 'name', 'description', 'duration_minutes', 'passing_percentage',
                  'total_questions', 'is_active', 'questions_count', 'created_at']
    
    def get_questions_count(self, obj):
        return obj.questions.count()


class TestAttemptSerializer(serializers.ModelSerializer):
    candidate_name = serializers.CharField(source='candidate.full_name', read_only=True)
    test_name = serializers.CharField(source='test.name', read_only=True)
    
    class Meta:
        model = TestAttempt
        fields = ['id', 'candidate', 'candidate_name', 'test', 'test_name',
                  'started_at', 'completed_at', 'score', 'total_marks', 'percentage',
                  'is_passed', 'is_terminated', 'termination_reason', 'tab_switch_count',
                  'copy_attempt_count', 'screenshot_attempt_count', 'result_released',
                  'result_release_date']


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['id', 'question', 'selected_answer', 'is_correct', 'marks_obtained', 'time_taken_seconds']


class WorkLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkLog
        fields = ['id', 'employee', 'date', 'activity_type', 'description', 'hours_worked', 'created_at']


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'check_in', 'check_out', 'check_in_photo', 'check_out_photo', 'status', 'notes']


class CheckInSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'employee', 'date', 'check_in', 'check_in_photo']


class CheckOutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance
        fields = ['id', 'check_out', 'check_out_photo', 'notes']


class CandidateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Candidate
        fields = ['first_name', 'last_name', 'email', 'phone', 'candidate_type',
                  'resume', 'linkedin_profile', 'github_profile', 'years_experience',
                  'current_company', 'position_applied']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'title', 'message', 'notification_type', 'is_read', 'link', 'created_at']
        read_only_fields = ['created_at']


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_name = serializers.SerializerMethodField()
    total_days = serializers.IntegerField(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = ['id', 'employee', 'employee_name', 'leave_type', 'start_date', 'end_date', 'total_days', 'reason', 'status', 'created_at']
        read_only_fields = ['created_at']

    def get_employee_name(self, obj):
        return obj.employee.full_name if obj.employee else None


class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['id', 'title', 'content', 'priority', 'is_active', 'created_at']
        read_only_fields = ['created_at']


class EventSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'event_type', 'location', 'meeting_link', 'start_datetime', 'end_datetime', 'created_by', 'created_by_name', 'created_at']
        read_only_fields = ['created_at']
    
    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class ProjectSerializer(serializers.ModelSerializer):
    team_name = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'team', 'team_name', 'status', 'progress', 'start_date', 'end_date', 'created_at']
        read_only_fields = ['created_at']

    def get_team_name(self, obj):
        return obj.team.name if obj.team else None


class PayrollSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(read_only=True)
    gross_salary = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_deductions = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    net_salary = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    
    class Meta:
        model = Payroll
        fields = ['id', 'employee', 'employee_name', 'salary', 'allowance_hra', 'allowance_conveyance', 
                'allowance_medical', 'allowance_special', 'allowance_other',
                'deduction_tax', 'deduction_insurance', 'deduction_other',
                'month', 'year', 'status', 'payment_date', 'payment_mode', 'transaction_id',
                'gross_salary', 'total_deductions', 'net_salary', 'created_at']
        read_only_fields = ['created_at']
    
    def get_employee_name(self, obj):
        return obj.employee.full_name