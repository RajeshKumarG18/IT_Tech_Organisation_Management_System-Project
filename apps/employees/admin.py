from django.contrib import admin
from .models import Employee, WorkLog, Attendance, Notification, LeaveRequest, Announcement, Event, Project, ChatBotConversation, OrganizationSettings, Payroll


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'full_name', 'email', 'department', 'role', 'reporting_manager', 'status', 'date_of_joining']
    list_filter = ['status', 'department', 'role__level']
    search_fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone']
    ordering = ['-date_of_joining']
    raw_id_fields = ['department', 'role', 'reporting_manager', 'user']
    date_hierarchy = 'date_of_joining'
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('employee_id', 'user', 'first_name', 'last_name', 'email', 
                       'phone', 'date_of_birth', 'address', 'emergency_contact', 'profile_image')
        }),
        ('Employment Details', {
            'fields': ('department', 'role', 'reporting_manager', 'date_of_joining', 'status')
        }),
    )


@admin.register(WorkLog)
class WorkLogAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'project', 'category', 'work_mode', 'duration']
    list_filter = ['date', 'category', 'work_mode', 'project']
    search_fields = ['employee__first_name', 'employee__last_name', 'project', 'work_description']
    date_hierarchy = 'date'
    raw_id_fields = ['employee']


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'check_in', 'check_out', 'status', 'has_checkin_photo', 'has_checkout_photo']
    list_filter = ['date', 'status']
    search_fields = ['employee__first_name', 'employee__last_name']
    date_hierarchy = 'date'
    raw_id_fields = ['employee']
    readonly_fields = ['check_in_photo', 'check_out_photo']
    
    def has_checkin_photo(self, obj):
        return bool(obj.check_in_photo)
    has_checkin_photo.boolean = True
    has_checkin_photo.short_description = 'Check In Photo'
    
    def has_checkout_photo(self, obj):
        return bool(obj.check_out_photo)
    has_checkout_photo.boolean = True
    has_checkout_photo.short_description = 'Check Out Photo'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username']
    date_hierarchy = 'created_at'
    raw_id_fields = ['user']


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'status', 'created_at']
    list_filter = ['leave_type', 'status']
    search_fields = ['employee__first_name', 'employee__last_name']
    raw_id_fields = ['employee', 'reviewed_by']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'priority', 'is_active', 'created_at']
    list_filter = ['priority', 'is_active']
    search_fields = ['title', 'content']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_type', 'time_status', 'location', 'meeting_link', 'start_datetime']
    list_filter = ['event_type', 'status']
    search_fields = ['title', 'location', 'meeting_link']
    date_hierarchy = 'start_datetime'
    readonly_fields = ['time_status']
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'event_type')
        }),
        ('Location & Link', {
            'fields': ('location', 'meeting_link')
        }),
        ('Date & Time', {
            'fields': ('start_datetime', 'end_datetime', 'status', 'time_status')
        }),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'team', 'status', 'progress', 'start_date']
    list_filter = ['status', 'team']
    search_fields = ['name']
    raw_id_fields = ['team']


@admin.register(ChatBotConversation)
class ChatBotConversationAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_message', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user_message', 'bot_response']
    raw_id_fields = ['user']


@admin.register(OrganizationSettings)
class OrganizationSettingsAdmin(admin.ModelAdmin):
    list_display = ['organization_name', 'organization_short_name', 'updated_at']
    fieldsets = (
        ('Organization Information', {
            'fields': ('organization_name', 'organization_short_name')
        }),
        ('Logo & Branding', {
            'fields': ('logo', 'favicon')
        }),
        ('Color Scheme', {
            'fields': ('primary_color', 'secondary_color')
        }),
    )


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ['employee', 'month', 'year', 'gross_salary', 'total_deductions', 'net_salary', 'status']
    list_filter = ['status', 'year', 'month']
    search_fields = ['employee__first_name', 'employee__last_name', 'employee__employee_id']
    ordering = ['-year', '-month']
    raw_id_fields = ['employee', 'created_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Employee & Period', {
            'fields': ('employee', 'month', 'year', 'status')
        }),
        ('Salary', {
            'fields': ('salary',)
        }),
        ('Allowances', {
            'fields': ('allowance_hra', 'allowance_conveyance', 'allowance_medical', 'allowance_special', 'allowance_other')
        }),
        ('Deductions', {
            'fields': ('deduction_tax', 'deduction_insurance', 'deduction_other')
        }),
        ('Payment Details', {
            'fields': ('payment_date', 'payment_mode', 'transaction_id', 'created_by')
        }),
    )
    
    readonly_fields = ['gross_salary', 'total_deductions', 'net_salary', 'created_at']