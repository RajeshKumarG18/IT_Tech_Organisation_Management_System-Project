from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DashboardViewSet, org_chart_data, reports_structure
from .web_views import dashboard_view, logout_view, org_chart_view, employees_list_view, custom_login_view, worklog_view, attendance_checkin, attendance_checkout, candidate_apply_view, candidate_login_view, candidate_test_view, candidate_logout_view, profile_view, chatbot_api, chatbot_history
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

router = DefaultRouter()
router.register(r'api', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False), name='home'),
    path('api/', include(router.urls)),
    path('api/org-chart/', org_chart_data, name='org-chart-data'),
    path('api/reports-structure/', reports_structure, name='reports_structure'),
    
    # Web views
    path('dashboard/', dashboard_view, name='dashboard'),
    path('profile/', profile_view, name='profile'),
    path('login/', custom_login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('org-chart/', org_chart_view, name='org-chart'),
    path('employees/', employees_list_view, name='employee-list-web'),
    path('worklog/', worklog_view, name='worklog'),
    path('worklog/create/', worklog_view, name='worklog-create'),
    path('attendance/checkin/', attendance_checkin, name='attendance-checkin'),
    path('attendance/checkout/', attendance_checkout, name='attendance-checkout'),
    
    # Recruitment / Candidate views
    path('candidate/apply/', candidate_apply_view, name='candidate-apply'),
    path('chatbot/', chatbot_api, name='chatbot-api'),
    path('chatbot/history/', chatbot_history, name='chatbot-history'),
    path('candidate/login/', candidate_login_view, name='candidate-login'),
    path('candidate/test/', candidate_test_view, name='candidate-test'),
    path('candidate/logout/', candidate_logout_view, name='candidate-logout'),
    
    # Password reset using Django's built-in views
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset.html',
        email_template_name='registration/password_reset_email.html',
        success_url='/password-reset/done/'
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/password-reset/complete/'
    ), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]