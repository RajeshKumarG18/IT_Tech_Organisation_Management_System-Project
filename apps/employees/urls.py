from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeViewSet, WorkLogViewSet, AttendanceViewSet, CandidateViewSet, AptitudeTestViewSet, TestAttemptViewSet, NotificationViewSet, LeaveRequestViewSet, AnnouncementViewSet, EventViewSet, ProjectViewSet, ChatBotViewSet, PayrollViewSet

router = DefaultRouter()
router.register(r'', EmployeeViewSet, basename='employees')
router.register(r'worklogs', WorkLogViewSet, basename='worklogs')
router.register(r'attention', AttendanceViewSet, basename='attendance')
router.register(r'candidates', CandidateViewSet, basename='candidates')
router.register(r'tests', AptitudeTestViewSet, basename='tests')
router.register(r'attempts', TestAttemptViewSet, basename='attempts')
router.register(r'notifications', NotificationViewSet, basename='notifications')
router.register(r'leave-requests', LeaveRequestViewSet, basename='leave-requests')
router.register(r'announcements', AnnouncementViewSet, basename='announcements')
router.register(r'events', EventViewSet, basename='events')
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'chatbot', ChatBotViewSet, basename='chatbot')
router.register(r'payrolls', PayrollViewSet, basename='payrolls')

urlpatterns = [
    path('', include(router.urls)),
]