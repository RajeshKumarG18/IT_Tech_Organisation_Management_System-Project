from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db import models
from django.db.models import Count
from django.utils import timezone
from django.conf import settings

from apps.employees.models import Employee, Candidate, AptitudeTest, TestAttempt, LeaveRequest, Announcement, Event, Project, ChatBotConversation
from apps.departments.models import Department
from apps.roles.models import Role
from apps.accounts.models import OrganizationLevel
from datetime import timedelta


def logout_view(request):
    logout(request)
    return redirect('login')


def schedule_view(request):
    """Schedule management view"""
    from apps.employees.models import Event, LeaveRequest
    from datetime import datetime
    
    today = timezone.now().date()
    now = timezone.now()
    
    # Get all events - filter out invalid ones (end <= start) for display
    all_events = Event.objects.filter(start_datetime__date__gte=today).order_by('start_datetime')
    
    # Filter events: either upcoming (start > now) or live (now between start and end)
    events = []
    for event in all_events:
        # Include if: upcoming OR live OR has meeting link
        if event.start_datetime > now:
            events.append(event)  # Upcoming
        elif event.end_datetime > now and event.end_datetime > event.start_datetime:
            events.append(event)  # Live but has valid duration
        elif event.meeting_link:
            events.append(event)  # Has meeting link, show it
    
    pending_leaves = LeaveRequest.objects.filter(status='PENDING').order_by('start_date')[:10]
    
    context = {
        'title': 'Schedule',
        'events': events,
        'pending_leaves': pending_leaves,
    }
    return render(request, 'dashboard/schedule.html', context)


def reports_view(request):
    """Reports view"""
    from apps.employees.models import Employee, WorkLog, Event
    from apps.departments.models import Department
    from apps.roles.models import Role
    from django.db.models import Count
    from django.utils import timezone
    
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='ACTIVE').count()
    total_departments = Department.objects.count()
    total_roles = Role.objects.count()
    recent_worklogs = WorkLog.objects.order_by('-date')[:20]
    
    # Get upcoming and past meetings
    now = timezone.now()
    
    # Separate events by time validity
    valid_events = Event.objects.filter(end_datetime__gt=models.F('start_datetime'))
    invalid_time_events = Event.objects.filter(end_datetime__lte=models.F('start_datetime'))
    
    # Live meetings (currently happening) - only valid events
    live_meetings = valid_events.filter(
        start_datetime__lte=now, 
        end_datetime__gte=now
    )
    
    # Upcoming meetings (not started yet) - valid events only
    upcoming_valid = valid_events.filter(start_datetime__gt=now)
    
    # Invalid time events - if start is in future, show as upcoming
    invalid_upcoming = invalid_time_events.filter(start_datetime__gt=now)
    
    # Past meetings - valid events that ended
    past_valid = valid_events.filter(end_datetime__lt=now)
    
    # Invalid time events - if start is in past, show in past
    invalid_past = invalid_time_events.filter(start_datetime__lte=now)
    
    # Combine upcoming: live + valid upcoming + invalid upcoming
    all_upcoming = list(live_meetings) + list(upcoming_valid) + list(invalid_upcoming)
    
    # Combine past: valid past + invalid past
    all_past = list(past_valid) + list(invalid_past)
    
    total_meetings = Event.objects.count()
    live_count = live_meetings.count()
    upcoming_count = len(all_upcoming)
    past_count = len(all_past)
    
    context = {
        'title': 'Reports',
        'total_employees': total_employees,
        'active_employees': active_employees,
        'total_departments': total_departments,
        'total_roles': total_roles,
        'recent_worklogs': recent_worklogs,
        'upcoming_meetings': all_upcoming,
        'past_meetings': all_past,
        'live_meetings': live_count,
        'total_meetings': total_meetings,
    }
    return render(request, 'dashboard/reports.html', context)


def candidate_logout_view(request):
    logout(request)
    return redirect('candidate-login')


def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    context = {'user': user}
    
    if user.user_type in ['ADMIN', 'EXECUTIVE', 'MANAGER', 'HR'] or user.is_superuser:
        context['dashboard_type'] = 'executive'
        
        # Demo data - showing sample organization stats
        context['stats'] = {
            'total_employees': 6,
            'active_employees': 6,
            'total_departments': 22,
            'total_roles': 68,
        }
        
        # Sample department data for chart
        departments = [
            {'name': 'Engineering', 'employee_count': 15},
            {'name': 'Human Resources', 'employee_count': 8},
            {'name': 'Product', 'employee_count': 6},
            {'name': 'Finance', 'employee_count': 5},
            {'name': 'IT Support', 'employee_count': 4},
            {'name': 'Marketing', 'employee_count': 3},
            {'name': 'Admin', 'employee_count': 2},
        ]
        context['departments'] = departments
        
        # Sample level data for chart
        context['roles_by_level'] = {
            'Executive Leadership': 2,
            'Upper Management': 5,
            'Middle Management': 8,
            'Senior Professional': 15,
            'Junior Professional': 20,
            'Support Function': 10,
        }
        
        # No employee data in database currently
        context['recent_employees'] = []
        
        # Real data from database
        context['leave_requests'] = list(LeaveRequest.objects.filter(status='PENDING').select_related('employee')[:5].values(
            'id', 'employee__first_name', 'employee__last_name', 'leave_type', 'start_date', 'end_date'
        ))
        
        context['announcements'] = list(Announcement.objects.filter(is_active=True)[:3].values(
            'id', 'title', 'content', 'priority', 'created_at'
        ))
        
        context['events'] = list(Event.objects.filter(start_datetime__gte=timezone.now())[:4].values(
            'id', 'title', 'location', 'start_datetime', 'end_datetime'
        ))
        
        context['projects'] = list(Project.objects.select_related('team')[:4].values(
            'id', 'name', 'team__name', 'status', 'progress'
        ))

        context['total_employees_count'] = Employee.objects.count()
        
    elif user.user_type in ['MANAGER', 'HR']:
        context['dashboard_type'] = 'manager'
        
        if user.employee:
            employee = user.employee
            direct_reports = employee.subordinates.all()
            
            context['team_size'] = employee.get_total_team_size()
            context['direct_reports_count'] = direct_reports.count()
            context['direct_reports'] = [
                {
                    'name': e.full_name,
                    'role': e.role.title,
                    'department': e.department.name,
                    'status': e.status,
                }
                for e in direct_reports
            ]
            context['department'] = {'name': employee.department.name}
    
    else:
        context['dashboard_type'] = 'employee'
        
        if user.employee:
            employee = user.employee
            
            context['employee'] = {
                'name': employee.full_name,
                'email': employee.email,
                'phone': employee.phone,
                'employee_id': employee.employee_id,
                'date_of_joining': employee.date_of_joining,
                'role': employee.role.title,
            }
            
            context['department'] = {
                'name': employee.department.name,
                'code': employee.department.code,
            }
            
            context['role'] = {
                'title': employee.role.title,
                'level_display': employee.get_org_level(),
            }
            
            if employee.reporting_manager:
                context['reporting_to'] = {
                    'name': employee.reporting_manager.full_name,
                    'role': employee.reporting_manager.role.title,
                    'email': employee.reporting_manager.email,
                }
    
    return render(request, 'dashboard/dashboard.html', context)


def custom_login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        
        if user is None and '@' in username:
            try:
                user_obj = get_user_model().objects.get(email=username)
                user = authenticate(request, username=user_obj.username, password=password)
            except get_user_model().DoesNotExist:
                pass
        
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'registration/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def password_change_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        user = request.user
        
        # Verify current password
        if not user.check_password(current_password):
            messages.error(request, 'Current password is incorrect')
        elif len(new_password) < 8:
            messages.error(request, 'New password must be at least 8 characters')
        elif new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match')
        else:
            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password changed successfully! Please login with your new password.')
            logout(request)
            return redirect('login')
    
    return render(request, 'registration/password_change.html')


def org_chart_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    return render(request, 'dashboard/org_chart.html')


def employees_list_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    employees = Employee.objects.select_related('department', 'role').order_by('-date_of_joining')
    
    search = request.GET.get('search')
    if search:
        employees = employees.filter(
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(employee_id__icontains=search) |
            models.Q(department__name__icontains=search)
        )
    
    paginator = Paginator(employees, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'employees/employee_list.html', {
        'page_obj': page_obj,
        'search': search
    })


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    employee = getattr(request.user, 'employee_profile', None)
    
    # Auto-create employee if none exists
    if not employee:
        from apps.departments.models import Department
        from apps.roles.models import Role
        from apps.employees.models import Employee
        from datetime import date
        
        dept = Department.objects.first()
        
        if not dept:
            messages.error(request, 'No department found. Please create a department first.')
            return redirect('dashboard')
        
        role = Role.objects.filter(department=dept).first()
        if not role:
            role = Role.objects.first()
        
        # Generate employee ID
        last_emp = Employee.objects.order_by('-id').first()
        new_id = int(last_emp.employee_id.replace('EMP', '')) + 1 if last_emp and last_emp.employee_id else 1
        emp_id = f'EMP{new_id:04d}'
        
        employee = Employee.objects.create(
            employee_id=emp_id,
            user=request.user,
            first_name=request.user.first_name or request.user.username,
            last_name=request.user.last_name or '',
            email=request.user.email,
            phone='',
            department=dept,
            role=role,
            date_of_joining=date.today(),
            status='ACTIVE'
        )
        # Create welcome notification
        from apps.employees.models import Notification
        Notification.create_notification(
            user=request.user,
            title='Welcome to IT Org!',
            message=f'Your employee profile has been created. Employee ID: {emp_id}',
            notification_type='SUCCESS',
            link='/profile/'
        )
        messages.success(request, 'Employee profile created successfully!')
        return redirect('profile')
    
    if request.method == 'POST':
        employee.first_name = request.POST.get('first_name', employee.first_name)
        employee.last_name = request.POST.get('last_name', employee.last_name)
        employee.phone = request.POST.get('phone', employee.phone)
        employee.address = request.POST.get('address', employee.address)
        
        if request.FILES.get('profile_image'):
            employee.profile_image = request.FILES.get('profile_image')
        
        employee.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    context = {
        'employee': employee,
        'user': request.user
    }
    return render(request, 'employees/profile.html', context)


def worklog_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if not hasattr(request.user, 'employee'):
        return redirect('dashboard')
    
    from apps.employees.models import WorkLog, Attendance
    from django.utils import timezone
    
    today = timezone.now().date()
    
    if request.method == 'POST':
        from apps.employees.models import WorkLog
        from datetime import timedelta
        from django.http import JsonResponse
        
        try:
            hours = float(request.POST.get('duration_hours', 8))
            duration = timedelta(hours=hours)
            
            WorkLog.objects.create(
                employee=request.user.employee,
                date=request.POST.get('date'),
                project=request.POST.get('project'),
                feature=request.POST.get('feature', ''),
                category=request.POST.get('category'),
                work_description=request.POST.get('work_description'),
                duration=duration,
                work_mode=request.POST.get('work_mode')
            )
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'Work log saved successfully!'})
            
            messages.success(request, 'Work log saved successfully!')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)}, status=400)
            messages.error(request, f'Error: {str(e)}')
            return redirect('worklog')
    
    recent_logs = WorkLog.objects.filter(
        employee=request.user.employee
    ).order_by('-date')[:5]
    
    attendance = Attendance.objects.filter(
        employee=request.user.employee,
        date=today
    ).first()
    
    return render(request, 'employees/worklog.html', {
        'today': today,
        'recent_logs': recent_logs,
        'attendance': attendance,
    })


def attendance_checkin(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        from apps.employees.models import Attendance
        from django.utils import timezone
        
        today = timezone.now().date()
        photo = request.FILES.get('check_in_photo')
        
        attendance, created = Attendance.objects.get_or_create(
            employee=request.user.employee,
            date=today,
            defaults={'status': 'PRESENT'}
        )
        attendance.check_in = timezone.now()
        attendance.check_in_photo = photo
        attendance.status = 'PRESENT'
        attendance.save()
        
        messages.success(request, 'Check-in successful!')
    
    return redirect('worklog')


def attendance_checkout(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        from apps.employees.models import Attendance
        from django.utils import timezone
        
        today = timezone.now().date()
        photo = request.FILES.get('check_out_photo')
        
        try:
            attendance = Attendance.objects.get(
                employee=request.user.employee,
                date=today
            )
            attendance.check_out = timezone.now()
            attendance.check_out_photo = photo
            attendance.save()
            messages.success(request, 'Check-out successful!')
        except Attendance.DoesNotExist:
            messages.error(request, 'No check-in record found')
    
    return redirect('worklog')


# ====================== RECRUITMENT VIEWS ======================

def candidate_apply_view(request):
    if request.method == 'POST':
        from apps.employees.models import Candidate
        
        candidate = Candidate.objects.create(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            phone=request.POST.get('phone'),
            candidate_type=request.POST.get('candidate_type'),
            years_experience=int(request.POST.get('years_experience', 0)),
            current_company=request.POST.get('current_company', ''),
            position_applied=request.POST.get('position_applied'),
            resume=request.FILES.get('resume'),
            linkedin_profile=request.POST.get('linkedin_profile', ''),
            github_profile=request.POST.get('github_profile', ''),
        )
        
        messages.success(request, 'Application submitted successfully! HR will review and send login credentials via email.')
        return redirect('candidate-apply')
    
    return render(request, 'recruitment/apply.html')


def candidate_login_view(request):
    if request.user.is_authenticated:
        if hasattr(request.user, 'candidate'):
            return redirect('candidate-test')
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None and hasattr(user, 'candidate'):
            login(request, user)
            return redirect('candidate-test')
        else:
            messages.error(request, 'Invalid credentials or you are not a candidate')
    
    return render(request, 'recruitment/candidate_login.html')


def candidate_test_view(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'candidate'):
        return redirect('candidate-login')
    
    candidate = request.user.candidate
    
    # Check if there's an approved test attempt
    try:
        attempt = TestAttempt.objects.filter(
            candidate=candidate,
            status='APPROVED'
        ).first()
        
        if not attempt:
            messages.info(request, 'No test assigned yet. Please wait for HR to approve your application.')
            return render(request, 'recruitment/waiting.html')
        
        # Check if already completed
        if attempt.completed_at:
            if timezone.now() >= attempt.result_release_date:
                return render(request, 'recruitment/result.html', {
                    'attempt': attempt,
                    'show_result': True
                })
            else:
                return render(request, 'recruitment/waiting.html', {
                    'message': f'Result will be available on {attempt.result_release_date.strftime("%Y-%m-%d %H:%M")}'
                })
        
        # Start test
        test = attempt.test
        questions = list(test.questions.all().order_by('?')[:test.total_questions])
        
        return render(request, 'recruitment/aptitude_test.html', {
            'test': test,
            'questions': questions,
            'questions_json': [q.question_text for q in questions],
            'total_questions': len(questions),
            'duration_minutes': test.duration_minutes,
            'attempt_id': attempt.id,
        })
    
    except Exception as e:
        messages.error(request, str(e))
        return redirect('candidate-login')


@api_view(['POST'])
@permission_classes([AllowAny])
def chatbot_api(request):
    """ChatBot API endpoint"""
    from apps.dashboard.chatbot import OrganizationChatBot
    
    message = request.data.get('message', '').strip()
    
    if not message:
        return JsonResponse({'response': 'Hello! How can I help you?'})
    
    conversation_history = None
    if request.user.is_authenticated:
        recent_conversations = ChatBotConversation.objects.filter(
            user=request.user
        ).order_by('-created_at')[:5]
        conversation_history = [
            {'message': c.user_message, 'is_user': True}
            for c in recent_conversations
        ] + [
            {'message': c.bot_response, 'is_user': False}
            for c in recent_conversations
        ]
    
    response_text = OrganizationChatBot.get_response(message, request.user, conversation_history)
    
    if request.user.is_authenticated:
        ChatBotConversation.objects.create(
            user=request.user,
            user_message=message,
            bot_response=response_text
        )
    
    return JsonResponse({'response': response_text, 'llm_enabled': OrganizationChatBot.LLM_ENABLED})


@api_view(['GET'])
@permission_classes([AllowAny])
def chatbot_history(request):
    """Get ChatBot conversation history"""
    if not request.user.is_authenticated:
        return JsonResponse({'conversations': []})
    
    conversations = ChatBotConversation.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]
    
    return JsonResponse({
        'conversations': [
            {
                'user_message': c.user_message,
                'bot_response': c.bot_response,
                'created_at': c.created_at.isoformat()
            }
            for c in conversations
        ]
    })