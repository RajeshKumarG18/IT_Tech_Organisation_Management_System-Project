from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, Count
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
import random
import string

from .models import Employee, WorkLog, Attendance, Candidate, AptitudeTest, Question, TestAttempt, Answer, ProctoringLog, Notification, LeaveRequest, Announcement, Event, Project
from .serializers import (
    EmployeeSerializer, EmployeeListSerializer, 
    EmployeeDetailSerializer, EmployeeCreateSerializer,
    WorkLogSerializer, AttendanceSerializer,
    CheckInSerializer, CheckOutSerializer,
    CandidateSerializer, CandidateCreateSerializer,
    AptitudeTestSerializer, QuestionSerializer,
    TestAttemptSerializer, AnswerSerializer,
    NotificationSerializer, LeaveRequestSerializer,
    AnnouncementSerializer, EventSerializer,
    ProjectSerializer
)


def generate_password(length=12):
    chars = string.ascii_letters + string.digits + '!@#$%^&*'
    return ''.join(random.choice(chars) for _ in range(length))


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.select_related(
        'department', 'role', 'role__department', 
        'reporting_manager', 'user'
    ).prefetch_related('subordinates')
    permission_classes = [IsAuthenticated]
    search_fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone']
    ordering_fields = ['first_name', 'last_name', 'date_of_joining', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        dept_id = self.request.query_params.get('department')
        if dept_id:
            queryset = queryset.filter(department_id=dept_id)
        
        role_id = self.request.query_params.get('role')
        if role_id:
            queryset = queryset.filter(role_id=role_id)
        
        level = self.request.query_params.get('level')
        if level:
            queryset = queryset.filter(role__level=level)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        manager_id = self.request.query_params.get('manager')
        if manager_id:
            queryset = queryset.filter(reporting_manager_id=manager_id)
        
        has_manager = self.request.query_params.get('has_manager')
        if has_manager:
            if has_manager.lower() == 'true':
                queryset = queryset.filter(reporting_manager__isnull=False)
            else:
                queryset = queryset.filter(reporting_manager__isnull=True)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            return EmployeeListSerializer
        if self.action == 'retrieve':
            return EmployeeDetailSerializer
        if self.action == 'create':
            return EmployeeCreateSerializer
        return EmployeeSerializer
    
    @action(detail=False, methods=['get'])
    def org_chart(self, request):
        employees = self.queryset.filter(status='ACTIVE')
        
        def build_tree(emp):
            return {
                'id': emp.id,
                'name': emp.full_name,
                'title': emp.role.title,
                'department': emp.department.name,
                'level': emp.role.level,
                'children': [build_tree(sub) for sub in emp.subordinates.filter(status='ACTIVE')]
            }
        
        roots = employees.filter(reporting_manager__isnull=True)
        data = [build_tree(root) for root in roots]
        
        return Response(data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        total = self.queryset.count()
        active = self.queryset.filter(status='ACTIVE').count()
        inactive = self.queryset.filter(status='INACTIVE').count()
        on_leave = self.queryset.filter(status='ON_LEAVE').count()
        
        by_department = list(
            self.queryset.values('department__name')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        by_level = list(
            self.queryset.values('role__level')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        by_status = list(
            self.queryset.values('status')
            .annotate(count=Count('id'))
        )
        
        return Response({
            'total': total,
            'active': active,
            'inactive': inactive,
            'on_leave': on_leave,
            'by_department': by_department,
            'by_level': by_level,
            'by_status': by_status,
        })
    
    @action(detail=True, methods=['get'])
    def team(self, request, pk=None):
        employee = self.get_object()
        team = employee.subordinates.all()
        serializer = EmployeeListSerializer(team, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def subordinates_tree(self, request, pk=None):
        employee = self.get_object()
        
        def build_subtree(emp):
            return {
                'id': emp.id,
                'name': emp.full_name,
                'title': emp.role.title,
                'children': [build_subtree(sub) for sub in emp.subordinates.filter(status='ACTIVE')]
            }
        
        data = build_subtree(employee)
        return Response(data)
    
    @action(detail=True, methods=['get'])
    def hierarchy(self, request, pk=None):
        employee = self.get_object()
        path = employee.get_hierarchy_path()
        serializer = EmployeeListSerializer(path, many=True)
        return Response(serializer.data)


class WorkLogViewSet(viewsets.ModelViewSet):
    queryset = WorkLog.objects.select_related('employee').all()
    serializer_class = WorkLogSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['project', 'feature', 'work_description']
    ordering_fields = ['date', 'created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_superuser:
            queryset = queryset.filter(employee=user.employee)
        
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        project = self.request.query_params.get('project')
        if project:
            queryset = queryset.filter(project__icontains=project)
        
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset


class AttendanceViewSet(viewsets.ModelViewSet):
    queryset = Attendance.objects.select_related('employee').all()
    serializer_class = AttendanceSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['date', 'check_in']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        if not user.is_superuser:
            queryset = queryset.filter(employee=user.employee)
        
        date_from = self.request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        
        date_to = self.request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def check_in(self, request):
        serializer = CheckInSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'checked_in', 'message': 'Check-in successful'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def check_out(self, request):
        serializer = CheckOutSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'checked_out', 'message': 'Check-out successful'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        today = timezone.now().date()
        user = request.user
        
        if user.is_superuser:
            attendances = Attendance.objects.filter(date=today).select_related('employee')
        else:
            attendances = Attendance.objects.filter(employee=user.employee, date=today)
        
        serializer = AttendanceSerializer(attendances, many=True)
        return Response(serializer.data)


# ====================== RECRUITMENT VIEW SETS ======================

class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    permission_classes = [IsAuthenticated]
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'position_applied']
    ordering_fields = ['created_at', 'status']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CandidateCreateSerializer
        return CandidateSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        candidate_type = self.request.query_params.get('candidate_type')
        if candidate_type:
            queryset = queryset.filter(candidate_type=candidate_type)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve_for_test(self, request, pk=None):
        candidate = self.get_object()
        test_id = request.data.get('test_id')
        
        if not test_id:
            return Response({'error': 'test_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            test = AptitudeTest.objects.get(id=test_id)
        except AptitudeTest.DoesNotExist:
            return Response({'error': 'Test not found'}, status=status.HTTP_404_NOT_FOUND)
        
        password = generate_password()
        username = f"candidate_{candidate.id}"
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': candidate.email,
                'first_name': candidate.first_name,
                'last_name': candidate.last_name,
                'user_type': 'EMPLOYEE',
            }
        )
        
        if created:
            user.set_password(password)
            user.save()
        
        candidate.user = user
        candidate.status = 'APPROVED'
        candidate.save()
        
        TestAttempt.objects.create(
            candidate=candidate,
            test=test
        )
        
        email_message = f"""
Dear {candidate.full_name},

Your application for the position of {candidate.position_applied} has been shortlisted.

You are now eligible to attempt the aptitude test.

Login Credentials:
Username: {username}
Password: {password}

Test Details:
- Test Name: {test.name}
- Duration: {test.duration_minutes} minutes
- Total Questions: {test.total_questions}

Please login and attempt the test. The test will be proctored - ensure you have:
1. A working webcam
2. Stable internet connection
3. No other tabs open during the test

The test will auto-submit when time expires or you can submit manually.

Important: Any attempt to cheat (switch tabs, copy questions, take screenshots, or leave the camera frame) will result in automatic test termination.

Best of luck!

Regards,
HR Team
        """
        
        try:
            send_mail(
                subject=f'Aptitude Test Login Credentials - {candidate.position_applied}',
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@itorg.com',
                recipient_list=[candidate.email],
                fail_silently=False,
            )
        except:
            pass
        
        return Response({
            'message': 'Candidate approved and credentials sent',
            'username': username,
            'password': password,
            'email_sent': True
        })
    
    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def register(self, request):
        serializer = CandidateCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Application submitted successfully. HR will review and send login credentials via email.',
                'status': 'success'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AptitudeTestViewSet(viewsets.ModelViewSet):
    queryset = AptitudeTest.objects.all()
    serializer_class = AptitudeTestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return AptitudeTest.objects.filter(is_active=True)
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        test = self.get_object()
        questions = test.questions.all().order_by('?')[:test.total_questions]
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


class TestAttemptViewSet(viewsets.ModelViewSet):
    queryset = TestAttempt.objects.select_related('candidate', 'test').all()
    serializer_class = TestAttemptSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def start_test(self, request):
        candidate = request.user.candidate
        test_id = request.data.get('test_id')
        
        try:
            attempt = TestAttempt.objects.get(candidate=candidate, test_id=test_id, started_at__isnull=True)
        except TestAttempt.DoesNotExist:
            return Response({'error': 'No test attempt found'}, status=status.HTTP_404_NOT_FOUND)
        
        attempt.started_at = timezone.now()
        attempt.save()
        
        questions = attempt.test.questions.all().order_by('?')[:attempt.test.total_questions]
        
        return Response({
            'attempt_id': attempt.id,
            'test_name': attempt.test.name,
            'duration_minutes': attempt.test.duration_minutes,
            'total_questions': len(questions),
            'questions': QuestionSerializer(questions, many=True).data
        })
    
    @action(detail=False, methods=['post'])
    def submit_answer(self, request):
        attempt_id = request.data.get('attempt_id')
        question_id = request.data.get('question_id')
        selected_answer = request.data.get('selected_answer')
        time_taken = request.data.get('time_taken_seconds', 0)
        
        try:
            attempt = TestAttempt.objects.get(id=attempt_id)
            question = Question.objects.get(id=question_id)
        except (TestAttempt.DoesNotExist, Question.DoesNotExist):
            return Response({'error': 'Invalid attempt or question'}, status=status.HTTP_400_BAD_REQUEST)
        
        is_correct = selected_answer == question.correct_answer
        marks = question.marks if is_correct else 0
        
        answer, _ = Answer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                'selected_answer': selected_answer,
                'is_correct': is_correct,
                'marks_obtained': marks,
                'time_taken_seconds': time_taken
            }
        )
        
        return Response({'is_correct': is_correct, 'marks_obtained': marks})
    
    @action(detail=False, methods=['post'])
    def complete_test(self, request):
        attempt_id = request.data.get('attempt_id')
        
        try:
            attempt = TestAttempt.objects.get(id=attempt_id)
        except TestAttempt.DoesNotExist:
            return Response({'error': 'Attempt not found'}, status=status.HTTP_404_NOT_FOUND)
        
        answers = attempt.answers.all()
        attempt.score = sum(a.marks_obtained for a in answers)
        attempt.total_marks = sum(q.marks for q in attempt.test.questions.all())
        
        if attempt.total_marks > 0:
            attempt.percentage = (attempt.score / attempt.total_marks) * 100
        
        attempt.is_passed = attempt.percentage >= attempt.test.passing_percentage
        attempt.completed_at = timezone.now()
        attempt.result_release_date = timezone.now() + timedelta(days=1)
        attempt.save()
        
        return Response({
            'message': 'Test submitted successfully',
            'score': attempt.score,
            'total_marks': attempt.total_marks,
            'percentage': attempt.percentage,
            'is_passed': attempt.is_passed,
            'result_will_be_released_on': attempt.result_release_date
        })
    
    @action(detail=False, methods=['post'])
    def log_proctoring(self, request):
        attempt_id = request.data.get('attempt_id')
        event_type = request.data.get('event_type')
        details = request.data.get('details', '')
        
        try:
            attempt = TestAttempt.objects.get(id=attempt_id)
        except TestAttempt.DoesNotExist:
            return Response({'error': 'Attempt not found'}, status=status.HTTP_404_NOT_FOUND)
        
        ProctoringLog.objects.create(
            attempt=attempt,
            event_type=event_type,
            details=details
        )
        
        if event_type == 'TAB_SWITCH':
            attempt.tab_switch_count += 1
            if attempt.tab_switch_count >= 3:
                attempt.is_terminated = True
                attempt.termination_reason = 'Too many tab switches detected'
                attempt.result_release_date = timezone.now() + timedelta(days=1)
        elif event_type == 'COPY_ATTEMPT':
            attempt.copy_attempt_count += 1
            if attempt.copy_attempt_count >= 2:
                attempt.is_terminated = True
                attempt.termination_reason = 'Copy attempt detected'
                attempt.result_release_date = timezone.now() + timedelta(days=1)
        elif event_type == 'SCREENSHOT':
            attempt.screenshot_attempt_count += 1
            if attempt.screenshot_attempt_count >= 1:
                attempt.is_terminated = True
                attempt.termination_reason = 'Screenshot attempt detected'
                attempt.result_release_date = timezone.now() + timedelta(days=1)
        elif event_type == 'NO_FACE':
            attempt.no_face_count += 1
            if attempt.no_face_count >= 5:
                attempt.is_terminated = True
                attempt.termination_reason = 'Face not detected for extended period'
                attempt.result_release_date = timezone.now() + timedelta(days=1)
        elif event_type == 'FACE_DETECTED':
            attempt.faces_detected += 1
        
        attempt.save()
        
        if attempt.is_terminated:
            return Response({
                'terminated': True,
                'reason': attempt.termination_reason
            })
        
        return Response({'logged': True})
    
    @action(detail=False, methods=['get'])
    def my_results(self, request):
        candidate = request.user.candidate
        attempts = TestAttempt.objects.filter(candidate=candidate)
        
        results = []
        for attempt in attempts:
            if attempt.completed_at:
                result = {
                    'test_name': attempt.test.name,
                    'score': attempt.score,
                    'total_marks': attempt.total_marks,
                    'percentage': round(attempt.percentage, 2),
                    'is_passed': attempt.is_passed,
                    'completed_at': attempt.completed_at,
                    'result_released': attempt.result_released,
                    'result_release_date': attempt.result_release_date,
                    'is_terminated': attempt.is_terminated,
                    'termination_reason': attempt.termination_reason if attempt.is_terminated else None
                }
                
                if attempt.result_release_date and timezone.now() >= attempt.result_release_date:
                    result['result_available'] = True
                else:
                    result['result_available'] = False
                
                results.append(result)
        
        return Response(results)


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    def list(self, request):
        notifications = self.get_queryset()
        unread_count = notifications.filter(is_read=False).count()
        serializer = self.get_serializer(notifications, many=True)
        return Response({
            'notifications': serializer.data,
            'unread_count': unread_count
        })
    
    @action(detail=False, methods=['post'])
    def mark_read(self, request):
        notification_ids = request.data.get('notification_ids', [])
        if notification_ids:
            Notification.objects.filter(id__in=notification_ids, user=request.user).update(is_read=True)
        return Response({'success': True})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'success': True})


class LeaveRequestViewSet(viewsets.ModelViewSet):
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return LeaveRequest.objects.select_related('employee').all()
    
    def get_permissions(self):
        if self.request.user.user_type in ['ADMIN', 'HR', 'MANAGER']:
            return super().get_permissions()
        return [IsAuthenticated()]


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = AnnouncementSerializer
    permission_classes = [IsAuthenticated]
    queryset = Announcement.objects.filter(is_active=True)
    
    def get_permissions(self):
        if self.request.user.user_type in ['ADMIN', 'HR', 'MANAGER']:
            return super().get_permissions()
        return [IsAuthenticated()]


class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]
    queryset = Event.objects.filter(start_datetime__gte=timezone.now())
    
    def get_permissions(self):
        if self.request.user.user_type in ['ADMIN', 'HR', 'MANAGER']:
            return super().get_permissions()
        return [IsAuthenticated()]


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    queryset = Project.objects.select_related('team').all()


class ChatBotViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def create(self, request):
        from apps.dashboard.chatbot import OrganizationChatBot
        from apps.employees.models import ChatBotConversation
        
        user_message = request.data.get('message', '').strip()
        
        if not user_message:
            return Response({'response': 'Hello! How can I help you?'}, status=status.HTTP_200_OK)
        
        bot_response = OrganizationChatBot.get_response(user_message, request.user)
        
        if request.user.is_authenticated:
            ChatBotConversation.objects.create(
                user=request.user,
                user_message=user_message,
                bot_response=bot_response
            )
        
        return Response({'response': bot_response}, status=status.HTTP_200_OK)
    
    def list(self, request):
        from apps.employees.models import ChatBotConversation
        
        if not request.user.is_authenticated:
            return Response({'conversations': []}, status=status.HTTP_200_OK)
        
        conversations = ChatBotConversation.objects.filter(
            user=request.user
        ).order_by('-created_at')[:20]
        
        return Response({
            'conversations': [
                {
                    'user_message': c.user_message,
                    'bot_response': c.bot_response,
                    'created_at': c.created_at
                }
                for c in conversations
            ]
        })