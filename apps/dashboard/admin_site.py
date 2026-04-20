from django.contrib import admin
from django.shortcuts import render
from django.urls import path


class ITOrgAdminSite(admin.AdminSite):
    site_header = 'IT Tech Organisation Management System'
    site_title = 'IT Org Admin'
    index_title = 'Dashboard'
    
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        
        # Add ChatBot at the top
        app_list.insert(0, {
            'name': 'Organisation ChatBot',
            'app_label': 'chatbot',
            'models': [
                {
                    'name': 'AI Assistant',
                    'object_name': 'ChatBot',
                    'admin_url': '/admin/chatbot/',
                    'view_only': True,
                }
            ]
        })
        return app_list
    
    def get_urls(self):
        urls = super().get_urls()
        urls.insert(0, path('chatbot/', self.chatbot_view))
        return urls
    
    def chatbot_view(self, request):
        from apps.dashboard.chatbot import OrganizationChatBot
        
        response_text = ''
        if request.method == 'POST':
            message = request.POST.get('message', '').strip()
            if message:
                response_text = OrganizationChatBot.get_response(message, request.user)
        
        context = {
            'title': 'Organisation ChatBot',
            'response_text': response_text,
            'chatbot_available_topics': [
                'employee', 'department', 'role', 'leave', 'attendance', 
                'worklog', 'announcement', 'project', 'notification',
                'profile', 'dashboard', 'org_chart', 'password', 'login'
            ],
        }
        return render(request, 'admin/chatbot.html', context)


# Create the final admin site
site = ITOrgAdminSite(name='admin')

# Register models
from django.contrib.auth.models import User, Group
site.register(User)
site.register(Group)

from apps.accounts.models import CustomUser, OrganizationLevel
from apps.employees.models import Employee, WorkLog, Attendance, LeaveRequest, Announcement, Event, Project, Notification
from apps.departments.models import Department
from apps.roles.models import Role

site.register(CustomUser)
site.register(OrganizationLevel)
site.register(Employee)
site.register(WorkLog)
site.register(Attendance)
site.register(LeaveRequest)
site.register(Announcement)
site.register(Event)
site.register(Project)
site.register(Notification)
site.register(Department)
site.register(Role)

from apps.employees.models import OrganizationSettings
site.register(OrganizationSettings)