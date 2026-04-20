from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    OrganizationLevelViewSet, UserViewSet, 
    RegisterView, LoginView
)

router = DefaultRouter()
router.register(r'levels', OrganizationLevelViewSet, basename='org-levels')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', lambda r: Response({'message': 'Logged out'}), name='logout'),
]