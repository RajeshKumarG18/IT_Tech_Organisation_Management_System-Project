from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
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

# Use custom admin site with ChatBot
from apps.dashboard.admin_site import site as admin_site

# Add chatbot URL at root level too
@csrf_exempt
def chatbot_page_view(request):
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

urlpatterns = [
    path('chatbot/', chatbot_page_view, name='chatbot-page'),
    path('admin/', admin_site.urls),
    re_path(r'^admin2/.*', admin.site.urls),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/employees/', include('apps.employees.urls')),
    path('api/roles/', include('apps.roles.urls')),
    path('api/departments/', include('apps.departments.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),
    path('', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)