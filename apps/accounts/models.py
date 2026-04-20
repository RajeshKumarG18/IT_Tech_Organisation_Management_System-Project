from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class OrganizationLevel(models.Model):
    LEVEL_CHOICES = [
        ('EXECUTIVE', 'Executive Level'),
        ('UPPER_MANAGEMENT', 'Upper Management'),
        ('MIDDLE_MANAGEMENT', 'Middle Management'),
        ('SENIOR_PROFESSIONAL', 'Senior Professionals'),
        ('JUNIOR_PROFESSIONAL', 'Junior Professionals'),
        ('SUPPORT', 'Support Functions'),
    ]

    name = models.CharField(max_length=50, choices=LEVEL_CHOICES, unique=True)
    display_name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    level_order = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['level_order']

    def __str__(self):
        return self.display_name


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = [
        ('ADMIN', 'System Admin'),
        ('EXECUTIVE', 'Executive'),
        ('MANAGER', 'Manager'),
        ('HR', 'HR'),
        ('EMPLOYEE', 'Employee'),
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='EMPLOYEE')
    employee = models.OneToOneField('employees.Employee', on_delete=models.SET_NULL, null=True, blank=True, related_name='auth_user')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"

    @property
    def is_executive(self):
        return self.user_type == 'EXECUTIVE' or self.is_superuser

    @property
    def is_manager(self):
        return self.user_type in ['MANAGER', 'EXECUTIVE'] or self.is_superuser