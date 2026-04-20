import re
import random
from datetime import datetime, timedelta


class OrganizationChatBot:
    """Organization ChatBot with security restrictions - Never shares credentials"""
    
    # Topics the bot can help with
    HELP_TOPICS = {
        'login': ['login', 'log in', 'sign in', 'logout', 'log out'],
        'password': ['password', 'reset', 'forgot password'],
        'employee': ['employee', 'staff', 'worker', 'team member', 'personnel'],
        'department': ['department', 'dept', 'team', 'division', 'unit'],
        'role': ['role', 'position', 'job', 'title', 'designation'],
        'leave': ['leave', 'vacation', 'holiday', 'time off', 'absence', 'sick'],
        'attendance': ['attendance', 'check in', 'check out', 'present', 'absent'],
        'worklog': ['worklog', 'work log', 'daily work', 'task log'],
        'announcement': ['announcement', 'notice', 'news', 'update'],
        'project': ['project', 'projects', 'progress'],
        'notification': ['notification', 'alert', 'message'],
        'profile': ['profile', 'account', 'my details'],
        'dashboard': ['dashboard', 'stats', 'report', 'overview', 'summary'],
        'org_chart': ['org chart', 'organization', 'hierarchy', 'structure', 'reporting'],
    }
    
    # Blocked patterns that request credentials/sensitive info
    BLOCKED_PATTERNS = [
        r'password', r'passwd', r'credentials', r'cred',
        r'secret', r'token', r'api key', r'apikey',
        r'secret key', r'access token', r'auth.*',
        r'database.*password', r'db.*pass', r'sql.*pass',
        r'admin.*password', r'superuser.*pass',
        r'jwt.*', r'Bearer.*', r'authorization',
        r'private.*key', r'public.*key', r'RSA',
        r'AWS.*secret', r'AWS.*key',
        r'environment.*variable', r'\.env',
        r'config.*password', r'settings.*pass',
    ]
    
    # Responses for different topics
    RESPONSES = {
        'greeting': [
            "Hello! How can I help you today?",
            "Hi there! What would you like to know?",
            "Welcome! I'm here to help. What do you need?",
        ],
        'employee': [
            "To add an employee, go to Dashboard > Employees > Add Employee button. Or ask your HR/Admin to create one from the admin panel.",
            "You can manage employees from the Employees section in the sidebar. Admins can add/edit through admin panel.",
            "Employee records are managed by HR and Admin users. To add a new employee, navigate to the Employees section.",
        ],
        'department': [
            "Departments represent different teams in your organization. Ask your admin to create them via the admin panel.",
            "To view departments, check the Dashboard or Org Chart. For adding new ones, contact your administrator.",
            "Department structure can be viewed in the Org Chart. Contact HR to add new departments.",
        ],
        'role': [
            "Roles define job positions. Ask your administrator to create roles via the admin panel.",
            "Job roles can be managed by admins through the Roles section in admin panel.",
            "To add or modify roles, please contact your system administrator.",
        ],
        'leave': [
            "To request leave, go to the Work Log section and look for leave request options.",
            "Leave requests can be submitted through the system. Contact HR for approval.",
            "Check with your manager or HR about submitting leave requests.",
        ],
        'attendance': [
            "Attendance can be tracked via the Check In/Check Out buttons in the dashboard.",
            "Use the attendance feature in your profile to check in when you arrive and check out when you leave.",
            "Daily attendance is recorded through the Check In/Check Out options in the dashboard.",
        ],
        'worklog': [
            "Work logs can be submitted from the Work Log section in the sidebar.",
            "To log your daily work, navigate to Work Log and fill in the details.",
            "Keep track of your tasks by submitting work logs regularly.",
        ],
        'announcement': [
            "Announcements appear on your dashboard. Check the Announcements widget.",
            "Company announcements are displayed in the dashboard's Announcements section.",
            "Recent announcements can be found on your executive dashboard.",
        ],
        'project': [
            "Project status is shown in the Projects widget on the dashboard.",
            "Check the Project Status section for ongoing project progress.",
            "Active projects and their progress are displayed on the dashboard.",
        ],
        'notification': [
            "Click the bell icon in the top navbar to view your notifications.",
            "Your notifications appear as a dropdown from the bell icon in the navbar.",
            "Check the notification bell in the top-right corner for alerts.",
        ],
        'profile': [
            "Click 'Profile' in the sidebar to view and edit your profile.",
            "Update your profile details from the Profile section.",
            "Your profile can be edited from the Profile menu in the sidebar.",
        ],
        'dashboard': [
            "The dashboard shows an overview of your organization - stats, charts, projects, and more.",
            "Your executive dashboard contains key metrics and visualizations.",
            "Check the Dashboard for stats, charts, quick actions, and more.",
        ],
        'org_chart': [
            "View the Org Chart from the sidebar to see the company hierarchy.",
            "The Org Chart shows reporting structure and team layouts.",
            "Access Org Chart from the sidebar to view organizational hierarchy.",
        ],
        'password': [
            "Use the 'Forgot Password?' link on the login page to reset your password.",
            "For password reset, click 'Forgot Password?' on the login screen.",
            "Contact your administrator if you need help with login credentials.",
        ],
        'login': [
            "Log in from the login page with your username and password.",
            "Use your credentials to sign in. If you forgot, use the reset option.",
            "You can log out by clicking Logout in the sidebar.",
        ],
        'help': [
            "I can help with: employees, departments, roles, leave, attendance, worklog, announcements, projects, notifications, profile, dashboard, org chart, and login.",
            "Ask me about: adding employees, viewing stats, checking notifications, org chart, projects, and more.",
            "Try asking about: dashboard, employee management, worklogs, or company announcements.",
        ],
        'thanks': [
            "You're welcome! Let me know if you need anything else.",
            "Happy to help! Feel free to ask more questions.",
            "Glad I could help! What else can I assist you with?",
        ],
        'default': [
            "I'm not sure about that. Try asking about employees, departments, projects, dashboard, or other topics.",
            "I didn't quite get that. I can help with organization matters - try asking differently!",
            "Sorry, I don't understand. Try asking about employees, dashboard, projects, or help.",
        ],
        'security': [
            "I cannot share any credentials, passwords, tokens, or sensitive information. This is for your security.",
            "I'm sorry, but I can't help with that. I don't share credentials or sensitive data.",
            "That information is confidential. I'm designed not to share any credential details.",
        ],
    }
    
    @classmethod
    def get_response(cls, user_message, user=None):
        """Process user message and return bot response"""
        if not user_message:
            return random.choice(cls.RESPONSES['greeting'])
        
        message_lower = user_message.lower().strip()
        
        # Check for blocked patterns (credentials/sensitive info)
        for pattern in cls.BLOCKED_PATTERNS:
            if re.search(pattern, message_lower):
                return random.choice(cls.RESPONSES['security'])
        
        # Check for greetings
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'hiya', 'greetings']):
            return random.choice(cls.RESPONSES['greeting'])
        
        # Check for thanks
        if any(word in message_lower for word in ['thanks', 'thank', 'appreciate', 'grateful']):
            return random.choice(cls.RESPONSES['thanks'])
        
        # Check for help request
        if any(word in message_lower for word in ['help', 'what can you do', 'capabilities', 'features']):
            return random.choice(cls.RESPONSES['help'])
        
        # Check for exit/bye
        if any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'stop']):
            return "Goodbye! Feel free to come back if you need more help."
        
        # Match topic based on keywords
        for topic, keywords in cls.HELP_TOPICS.items():
            if any(keyword in message_lower for keyword in keywords):
                return random.choice(cls.RESPONSES.get(topic, cls.RESPONSES['default']))
        
        # Default response
        return random.choice(cls.RESPONSES['default'])