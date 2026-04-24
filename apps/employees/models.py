import datetime
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Payroll(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('PROCESSED', 'Processed'),
        ('PAID', 'Paid'),
    ]
    
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='payrolls')
    salary = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    allowance_hra = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='House Rent Allowance')
    allowance_conveyance = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Conveyance Allowance')
    allowance_medical = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Medical Allowance')
    allowance_special = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Special Allowance')
    allowance_other = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Other Allowances')
    deduction_tax = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Tax Deduction (TDS)')
    deduction_insurance = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Insurance')
    deduction_other = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text='Other Deductions')
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.IntegerField(validators=[MinValueValidator(2020), MaxValueValidator(2050)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    payment_date = models.DateTimeField(null=True, blank=True)
    payment_mode = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['employee', 'month', 'year']
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.month}/{self.year}"
    
    @property
    def gross_salary(self):
        return (self.salary or 0) + (self.allowance_hra or 0) + (self.allowance_conveyance or 0) + (self.allowance_medical or 0) + (self.allowance_special or 0) + (self.allowance_other or 0)
    
    @property
    def total_deductions(self):
        return (self.deduction_tax or 0) + (self.deduction_insurance or 0) + (self.deduction_other or 0)
    
    @property
    def net_salary(self):
        return self.gross_salary - self.total_deductions


class Employee(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
        ('ON_LEAVE', 'On Leave'),
        ('TERMINATED', 'Terminated'),
    ]

    employee_id = models.CharField(max_length=20, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    department = models.ForeignKey('departments.Department', on_delete=models.PROTECT, related_name='employees')
    role = models.ForeignKey('roles.Role', on_delete=models.PROTECT, related_name='employees')
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    date_of_joining = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(max_length=100, blank=True)
    profile_image = models.ImageField(upload_to='employee_profiles/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_of_joining']

    def __str__(self):
        return f"{self.employee_id} - {self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_manager(self):
        return self.subordinates.exists()

    def get_org_level(self):
        return self.role.level

    def get_hierarchy_path(self):
        path = [self]
        current = self.reporting_manager
        while current:
            path.append(current)
            current = current.reporting_manager
        return path

    def get_direct_subordinates_count(self):
        return self.subordinates.count()

    def get_total_team_size(self):
        count = self.subordinates.count()
        for subordinate in self.subordinates.all():
            count += subordinate.get_total_team_size()
        return count


class WorkLog(models.Model):
    WORK_MODE_CHOICES = [
        ('OFFICE', 'Office'),
        ('REMOTE', 'Remote'),
        ('HYBRID', 'Hybrid'),
    ]

    CATEGORY_CHOICES = [
        ('DEVELOPMENT', 'Development'),
        ('MEETING', 'Meeting'),
        ('RESEARCH', 'Research'),
        ('TESTING', 'Testing'),
        ('DOCUMENTATION', 'Documentation'),
        ('MAINTENANCE', 'Maintenance'),
        ('DEPLOYMENT', 'Deployment'),
        ('CODE_REVIEW', 'Code Review'),
        ('TRAINING', 'Training'),
        ('OTHER', 'Other'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='work_logs')
    date = models.DateField()
    project = models.CharField(max_length=200)
    feature = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    work_description = models.TextField()
    duration = models.DurationField()
    work_mode = models.CharField(max_length=20, choices=WORK_MODE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date} - {self.project}"


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    check_in_photo = models.ImageField(upload_to='attendance/photos/', null=True, blank=True)
    check_out_photo = models.ImageField(upload_to='attendance/photos/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('ON_LEAVE', 'On Leave'),
    ], default='ABSENT')
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date', '-check_in']
        unique_together = ['employee', 'date']

    def __str__(self):
        return f"{self.employee.full_name} - {self.date}"

    @property
    def work_hours(self):
        if self.check_in and self.check_out:
            return self.check_out - self.check_in
        return None


# ====================== RECRUITMENT MODELS ======================

class Candidate(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved for Test'),
        ('TEST_STARTED', 'Test Started'),
        ('TEST_COMPLETED', 'Test Completed'),
        ('REJECTED', 'Rejected'),
    ]
    
    CANDIDATE_TYPE_CHOICES = [
        ('FRESHER', 'Fresher'),
        ('EXPERIENCED', 'Experienced'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    candidate_type = models.CharField(max_length=20, choices=CANDIDATE_TYPE_CHOICES)
    resume = models.FileField(upload_to='resumes/')
    linkedin_profile = models.URLField(blank=True)
    github_profile = models.URLField(blank=True)
    years_experience = models.IntegerField(default=0)
    current_company = models.CharField(max_length=200, blank=True)
    position_applied = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='candidate')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class AptitudeTest(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    duration_minutes = models.IntegerField(default=60)
    passing_percentage = models.IntegerField(default=60)
    total_questions = models.IntegerField(default=50)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Question(models.Model):
    CATEGORY_CHOICES = [
        ('QUANTITATIVE', 'Quantitative Aptitude'),
        ('VERBAL', 'Verbal Ability'),
        ('LOGICAL', 'Logical Reasoning'),
        ('TECHNICAL', 'Technical'),
        ('CODING', 'Coding'),
    ]

    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    ]

    test = models.ForeignKey(AptitudeTest, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    marks = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.question_text[:50]}..."


class TestAttempt(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='test_attempts')
    test = models.ForeignKey(AptitudeTest, on_delete=models.CASCADE)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    score = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    percentage = models.FloatField(default=0)
    is_passed = models.BooleanField(default=False)
    is_terminated = models.BooleanField(default=False)
    termination_reason = models.TextField(blank=True)
    tab_switch_count = models.IntegerField(default=0)
    copy_attempt_count = models.IntegerField(default=0)
    screenshot_attempt_count = models.IntegerField(default=0)
    faces_detected = models.IntegerField(default=0)
    no_face_count = models.IntegerField(default=0)
    proctoring_logs = models.TextField(blank=True)
    result_released = models.BooleanField(default=False)
    result_release_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.candidate.full_name} - {self.test.name}"


class ProctoringLog(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='logs')
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50)
    details = models.TextField()
    screenshot = models.ImageField(upload_to='proctoring/', null=True, blank=True)

    class Meta:
        ordering = ['timestamp']


class Answer(models.Model):
    attempt = models.ForeignKey(TestAttempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    is_correct = models.BooleanField(default=False)
    marks_obtained = models.IntegerField(default=0)
    time_taken_seconds = models.IntegerField(default=0)

    class Meta:
        unique_together = ['attempt', 'question']


class Notification(models.Model):
    TYPE_CHOICES = [
        ('INFO', 'Information'),
        ('SUCCESS', 'Success'),
        ('WARNING', 'Warning'),
        ('URGENT', 'Urgent'),
    ]

    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='INFO')
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        self.is_read = True
        self.save()

    @classmethod
    def create_notification(cls, user, title, message, notification_type='INFO', link=''):
        """Helper to create a notification"""
        return cls.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link
        )


class LeaveRequest(models.Model):
    TYPE_CHOICES = [
        ('ANNUAL', 'Annual Leave'),
        ('SICK', 'Sick Leave'),
        ('PERSONAL', 'Personal Leave'),
        ('UNPAID', 'Unpaid Leave'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reviewed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee.full_name} - {self.leave_type} ({self.start_date} to {self.end_date})"

    @property
    def total_days(self):
        return (self.end_date - self.start_date).days + 1


class Announcement(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    priority = models.CharField(max_length=20, choices=[('NORMAL', 'Normal'), ('HIGH', 'High'), ('URGENT', 'Urgent')], default='NORMAL')
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Event(models.Model):
    EVENT_TYPES = [
        ('MEETING', 'Meeting'),
        ('TRAINING', 'Training'),
        ('EVENT', 'Company Event'),
        ('HOLIDAY', 'Holiday'),
        ('OTHER', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, default='MEETING')
    location = models.CharField(max_length=200, blank=True, default='')
    meeting_link = models.URLField(max_length=500, blank=True, default='', help_text='URL for meeting (Google Meet, Zoom, etc.)')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='SCHEDULED', help_text='Auto-updated based on time')
    created_by = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['start_datetime']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    @property
    def time_status(self):
        """Auto-determine status based on current time"""
        try:
            from django.utils import timezone
            now = timezone.now()
            
            if self.start_datetime and self.end_datetime:
                if self.end_datetime <= self.start_datetime:
                    return self.status if self.status else 'SCHEDULED'
                
                if now < self.start_datetime:
                    return 'SCHEDULED'
                elif now >= self.start_datetime and now <= self.end_datetime:
                    return 'IN_PROGRESS'
                else:
                    return 'COMPLETED'
            return self.status if self.status else 'SCHEDULED'
        except Exception:
            return self.status if self.status else 'SCHEDULED'
    
    @property
    def is_upcoming(self):
        return self.time_status == 'SCHEDULED'
    
    @property
    def is_in_progress(self):
        return self.time_status == 'IN_PROGRESS'
    
    @property
    def is_completed(self):
        return self.time_status == 'COMPLETED'


class Project(models.Model):
    STATUS_CHOICES = [
        ('PLANNING', 'Planning'),
        ('IN_PROGRESS', 'In Progress'),
        ('ON_HOLD', 'On Hold'),
        ('COMPLETED', 'Completed'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    team = models.ForeignKey('departments.Department', on_delete=models.CASCADE, related_name='projects')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNING')
    progress = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.status})"


class ChatBotConversation(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE, related_name='chatbot_conversations')
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Chat with {self.user.username} at {self.created_at}"


class OrganizationSettings(models.Model):
    """Model to store organization name and logo settings"""
    organization_name = models.CharField(max_length=200, default="IT Org")
    organization_short_name = models.CharField(max_length=50, default="IT Org")
    logo = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='organization_logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default="#FF6B00")
    secondary_color = models.CharField(max_length=7, default="#0B1F3A")
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Organization Settings"
        verbose_name_plural = "Organization Settings"

    def __str__(self):
        return self.organization_name

    def save(self, *args, **kwargs):
        if self.pk is None and OrganizationSettings.objects.exists():
            org = OrganizationSettings.objects.first()
            self.pk = org.pk
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        """Get or create organization settings"""
        settings, created = cls.objects.get_or_create(pk=1, defaults={
            'organization_name': 'IT Tech Organisation Management System',
            'organization_short_name': 'IT Org',
        })
        return settings