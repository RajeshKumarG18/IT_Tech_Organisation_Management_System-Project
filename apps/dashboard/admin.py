from django.contrib import admin
from django.urls import path, re_path
from django.shortcuts import render


class DashboardAdminSite(admin.AdminSite):
    site_header = 'IT Tech Organisation Management System'
    site_title = 'IT Org Admin'
    index_title = 'Dashboard'
    
    def get_urls(self):
        urls = super().get_urls()
        # Insert ChatBot URL at the beginning
        urls.insert(0, re_path(r'^chatbot/$', self.chatbot_view, name='chatbot'))
        return urls
    
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        # Add ChatBot link to the top of sidebar
        app_list.insert(0, {
            'name': 'Organisation ChatBot',
            'app_label': 'chatbot',
            'models': [{
                'name': 'Chat Assistant',
                'object_name': 'chatbot',
                'perms': {'add': True, 'change': True, 'delete': True, 'view': True},
                'admin_url': '/admin/chatbot/',
                'add_url': '/admin/chatbot/',
            }]
        })
        return app_list
    
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


dashboard_site = DashboardAdminSite(name='dashboard_admin')