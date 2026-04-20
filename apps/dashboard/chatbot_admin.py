from django.contrib import admin
from django.urls import path
from django.shortcuts import render


def chatbot_view(request):
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


# Register ChatBot URL with Django admin
admin.site_urls = [
    path('chatbot/', admin.admin_view(chatbot_view), name='chatbot'),
] + admin.site.urls