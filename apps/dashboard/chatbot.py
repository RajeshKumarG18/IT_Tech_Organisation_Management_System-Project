import re
import random
import json
import os
from datetime import datetime, timedelta
from django.conf import settings


class OrganizationChatBot:
    """LLM-powered Organization ChatBot with natural language responses"""
    
    # LLM Configuration
    OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', os.environ.get('OPENAI_API_KEY', ''))
    LLM_MODEL = getattr(settings, 'LLM_MODEL', 'gpt-3.5-turbo')
    LLM_ENABLED = bool(OPENAI_API_KEY)
    
    # System prompt for the LLM
    LLM_SYSTEM_PROMPT = """You are a professional virtual assistant for an IT Organisation Management System called {org_name}. 

Your role is to help employees navigate the organization system, answer questions about:
- Employee management and profiles
- Department structure and roles
- Leave requests and attendance tracking
- Work logs and daily tasks
- Company announcements and projects
- Dashboard, Org Chart, Schedule, and Reports features
- Login, password reset, and system access
- General company policies and procedures

IMPORTANT SECURITY RULES:
- NEVER share passwords, credentials, tokens, or sensitive information
- NEVER provide admin credentials or system access codes
- If asked about sensitive topics, politely decline and redirect

Keep responses concise, professional, and helpful. When you don't know something, admit it and suggest contacting HR or system administrator."""
    """Advanced Organization ChatBot with professional responses"""
    
    # Extended topics with more keywords
    HELP_TOPICS = {
        'login': ['login', 'log in', 'sign in', 'logout', 'log out', 'sign out', 'how to login', 'how to sign in'],
        'password': ['password', 'reset', 'forgot password', 'change password', 'password reset', 'forgot my password'],
        'employee': ['employee', 'staff', 'worker', 'team member', 'personnel', 'add employee', 'new employee', 'employee details'],
        'department': ['department', 'dept', 'team', 'division', 'unit', 'teams', 'organizational structure'],
        'role': ['role', 'position', 'job', 'title', 'designation', 'job title', 'employee role'],
        'leave': ['leave', 'vacation', 'holiday', 'time off', 'absence', 'sick', 'sick leave', 'annual leave', 'leave request', 'apply leave'],
        'attendance': ['attendance', 'check in', 'check out', 'present', 'absent', 'attendance tracking', 'daily attendance', 'clock in', 'clock out'],
        'worklog': ['worklog', 'work log', 'daily work', 'task log', 'daily log', 'work summary', 'log work', 'submit work'],
        'announcement': ['announcement', 'notice', 'news', 'update', 'company news', 'latest news', 'notifications'],
        'project': ['project', 'projects', 'progress', 'project status', 'ongoing project', 'active project'],
        'notification': ['notification', 'alert', 'message', 'notify', 'notifications', 'bell icon'],
        'profile': ['profile', 'account', 'my details', 'my profile', 'view profile', 'edit profile', 'update profile'],
        'dashboard': ['dashboard', 'stats', 'report', 'overview', 'summary', 'home', 'main page', 'statistics'],
        'org_chart': ['org chart', 'organization', 'hierarchy', 'structure', 'reporting', 'reporting structure', 'company hierarchy', 'organization chart'],
        'schedule': ['schedule', 'scheduling', 'calendar', 'events', 'upcoming events', 'event'],
        'reports': ['report', 'reports', 'analytics', 'statistics', 'data', 'charts', 'insights', 'metrics'],
        'admin': ['admin', 'administration', 'admin panel', 'settings', 'configuration', 'system settings'],
        'help': ['help', 'what can you do', 'capabilities', 'features', 'how does this work', 'guide', 'tutorial'],
        'contact': ['contact', 'reach', 'talk to someone', 'support', 'help desk', 'hr contact', 'admin contact'],
    }
    
    # Security - Blocked patterns
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
    
    # Professional and comprehensive responses
    RESPONSES = {
        'greeting': [
            "Hello! Welcome to {org_name}! I'm your virtual assistant. How can I help you today?",
            "Hi there! I'm here to help you navigate our organization system. What would you like to know?",
            "Welcome! I'm your {org_name} assistant. Feel free to ask me anything about our organization!",
            "Hello! How can I assist you today? I'm here to help with any questions about our organization system.",
        ],
        'employee': [
            "To manage employees, navigate to the Dashboard and click on 'Employees' in the sidebar. If you have admin privileges, you can add, edit, or view employee details from the Employees section.",
            "Employee management is available through the Employees menu in the sidebar. You can view all employees, add new ones, and update existing records. For adding employees, you'll need admin or HR permissions.",
            "Our employee management system allows you to view and manage employee records. Access the Employees section from the sidebar. For creating new employee accounts, please contact your HR or system administrator.",
        ],
        'department': [
            "Departments can be viewed in the Organization Chart (Org Chart) accessible from the sidebar. To add or modify departments, you'll need admin privileges. Contact your system administrator for assistance.",
            "Our organization is structured into various departments. You can view the complete department hierarchy by accessing the Org Chart from the sidebar menu.",
            "To see all departments and their structures, go to the Org Chart in the sidebar. For department management (adding/editing), please contact your administrator.",
        ],
        'role': [
            "Job roles define employee positions within the organization. Roles can be managed through the Admin Panel. Contact your system administrator to add or modify roles.",
            "Employee roles and positions are managed by administrators. To create or update job roles, please reach out to your system admin through the Admin Panel.",
            "Roles represent different job positions in our organization. You can view role information in employee profiles. For role management, please contact your HR department.",
        ],
        'leave': [
            "To request leave: 1) Go to the Work Log section from the sidebar, 2) Look for leave request options, 3) Fill in your details and submit for approval. Your manager will review the request.",
            "Leave requests can be submitted through the Work Log section. Navigate to Work Log > Leave Request, fill in your details including dates and reason, then submit. You'll be notified once your request is approved.",
            "To apply for leave, go to the Work Log section in the sidebar. Complete the leave request form with your details. Your manager will be notified and will approve or reject the request.",
        ],
        'attendance': [
            "To track your attendance: 1) Go to the Dashboard, 2) Look for 'Check In' when you start work, 3) Use 'Check Out' when you leave. This records your daily attendance automatically.",
            "Daily attendance is tracked through the Check In/Check Out feature on your dashboard. Simply click the appropriate button when you arrive at and leave from work each day.",
            "You can mark your daily attendance from the Dashboard. Use 'Check In' when you start your day and 'Check Out' when you finish. This helps maintain accurate attendance records.",
        ],
        'worklog': [
            "To submit a work log: 1) Navigate to Work Log from the sidebar, 2) Fill in your daily tasks and activities, 3) Include project details if applicable, 4) Submit your log.",
            "Work logs help track your daily activities. Go to Work Log in the sidebar, enter your work details, projects worked on, and submit regularly to maintain a record of your work.",
            "Submitting work logs is easy - go to Work Log from the sidebar, enter what you worked on today including projects and duration, and submit. Regular work logs help with performance tracking.",
        ],
        'announcement': [
            "Company announcements appear on your dashboard. Check the Announcements widget for the latest updates, news, and important information from management.",
            "Stay informed by checking the Announcements section on your dashboard. Important company news, updates, and notifications are posted there regularly.",
            "Recent company announcements and news can be viewed on your dashboard in the Announcements widget. This is where you'll find important updates from leadership.",
        ],
        'project': [
            "Project status and progress are displayed on your dashboard in the Projects widget. You can view ongoing projects, their progress, and team assignments there.",
            "To track projects, check the Projects section on your dashboard. Active projects, their status, and progress are all displayed there for easy monitoring.",
            "Our project management system shows all active projects on the dashboard. You can view project details, team members, and progress updates from the Projects widget.",
        ],
        'notification': [
            "Click the bell icon in the top-right corner of the navbar to view your notifications. You'll find alerts, updates, and important messages there.",
            "Your notification bell is in the top navigation bar. Click on it to see recent alerts, messages, and updates specific to your account.",
            "Stay updated by checking the notification bell in the top navbar. It shows all your alerts, pending approvals, and important system notifications.",
        ],
        'profile': [
            "To view or edit your profile: 1) Click on 'Profile' in the sidebar, 2) You can update your personal details, contact information, and view your employment details.",
            "Access your profile from the sidebar by clicking 'Profile'. Here you can view and update your personal information, contact details, and employment history.",
            "Your profile can be managed through the Profile section in the sidebar. Update your details, view your employment information, and manage your account settings there.",
        ],
        'dashboard': [
            "Your dashboard is your central hub! It provides an overview of: Employee statistics, Department info, Recent activities, Announcements, Project status, Quick actions, and more. It's designed to give you a complete picture of the organization at a glance.",
            "The dashboard shows your organization's key metrics and information. You'll find stats, charts, recent activities, announcements, project updates, and quick action buttons all in one place.",
            "Welcome to your executive dashboard! Here you can see: Total employees, Active employees, Department overview, Recent activities, Announcements, Project progress, and quick access to all major features.",
        ],
        'org_chart': [
            "The Org Chart shows your company's complete organizational structure. Access it from the sidebar to view reporting relationships, team hierarchies, and department structures.",
            "View our organization hierarchy through the Org Chart in the sidebar. It displays the complete structure from leadership down to all team members.",
            "The Organization Chart (Org Chart) provides a visual representation of our company structure. Access it from the sidebar to understand reporting lines and team compositions.",
        ],
        'schedule': [
            "View upcoming events and schedules from the Schedule section in the sidebar. You can see company events, meetings, and scheduled activities there.",
            "The Schedule page shows all upcoming events and activities. Navigate to Schedule from the sidebar to view event details, dates, and locations.",
            "Stay updated with upcoming events through the Schedule section. Access it from the sidebar to see company events, meetings, and other scheduled activities.",
        ],
        'reports': [
            "The Reports section provides analytics and insights about the organization. Access it from the sidebar to view: Employee statistics, Department performance, Work logs summary, and more data-driven insights.",
            "Our Reports section offers comprehensive analytics. Navigate to Reports from the sidebar to access: Employee metrics, Department data, Work statistics, and various organizational insights.",
            "Access detailed reports and analytics from the Reports section in the sidebar. View employee counts, department stats, work logs, and other important organizational data.",
        ],
        'admin': [
            "The Admin Panel provides system configuration options. Access it from the sidebar (if you have admin permissions) or through the Admin Panel link in the dashboard.",
            "System administration features are available in the Admin Panel. Contact your system administrator if you need access to configuration settings.",
            "For system settings and administration, use the Admin Panel. You'll need appropriate permissions to access administrative features. Contact your admin for access.",
        ],
        'password': [
            "To reset your password: 1) Go to the login page, 2) Click 'Forgot Password?', 3) Enter your username/email, 4) Follow the reset instructions sent to your email.",
            "If you've forgotten your password, click 'Forgot Password?' on the login page. You'll receive an email with instructions to reset your password securely.",
            "Password reset is available through the 'Forgot Password?' link on the login screen. Enter your credentials and follow the email instructions to create a new password.",
        ],
        'login': [
            "To log in: 1) Go to the login page, 2) Enter your username, 3) Enter your password, 4) Click 'Sign In'. Make sure your credentials are correct.",
            "Login using your provided username and password on the login page. If you don't have an account, contact your administrator to get one.",
            "Sign in with your username and password. After logging in, you'll have access to the dashboard and all features based on your role and permissions.",
        ],
        'contact': [
            "For additional assistance, you can: 1) Contact your manager directly, 2) Reach out to HR department, 3) Use the Admin Panel to find contact information.",
            "Need more help? Contact your supervisor or HR department. You can also access the Admin Panel for system administrator contact details.",
            "For questions beyond what I can help with, please contact: Your direct manager, HR department, or System Administrator through the Admin Panel.",
        ],
        'schedule_detailed': [
            "The Schedule page shows upcoming company events and activities. You can view event names, dates, times, and locations. Check back regularly for new events.",
            "Stay informed about company events through the Schedule section. All upcoming meetings, events, and important dates are listed there with full details.",
            "Company events and schedules are managed through the Schedule page. Navigate there from the sidebar to see all upcoming activities and important dates.",
        ],
        'reports_detailed': [
            "The Reports section provides valuable analytics. Access it to view: Employee count by department, Role distribution, Work log summaries, Attendance statistics, and more organizational insights.",
            "Our reporting system offers comprehensive data analysis. Use the Reports page to view: Department performance, Employee statistics, Work patterns, and other key metrics.",
            "Reports and analytics help understand organizational trends. The Reports section provides: Employee data, Department insights, Work statistics, and performance metrics.",
        ],
        'help': [
            "I can help you with information about: Employees, Departments, Roles, Leave requests, Attendance tracking, Work logs, Announcements, Projects, Notifications, Profile, Dashboard, Org Chart, Schedule, Reports, Login, Password reset, and more! Just ask me a question.",
            "I'm here to assist! I can provide information about: navigating the system, finding specific features, understanding organization structure, submitting requests, and answering common questions about our organization.",
            "Feel free to ask me about: employee management, department structure, leave requests, attendance, work logs, dashboard features, org chart, reports, or any other aspect of our organization system.",
        ],
        'thanks': [
            "You're welcome! I'm happy to help. Is there anything else you'd like to know about our organization system?",
            "Glad I could assist! Don't hesitate to ask if you have more questions. I'm here to help!",
            "You're welcome! Feel free to reach out anytime you need assistance. Is there anything else I can help you with?",
        ],
        'goodbye': [
            "Goodbye! Thank you for using the {org_name} assistant. Have a great day! Feel free to come back anytime you need assistance.",
            "Take care! I hope I was able to help. Remember, I'm always here if you have more questions. Goodbye!",
            "Thank you for using our chatbot service. If you need any further assistance, don't hesitate to return. Have a wonderful day!",
        ],
        'security': [
            "I cannot provide any confidential information such as passwords, credentials, tokens, or other sensitive data. This is for your security and privacy protection.",
            "I'm sorry, but I can't help with that. For security reasons, I don't provide access credentials, passwords, tokens, or other sensitive information.",
            "That information is confidential and protected. I don't have access to share credentials, passwords, or other sensitive system information.",
        ],
        'default': [
            "I'm not quite sure I understood that. Could you try rephrasing your question? I can help with employees, departments, leave, attendance, work logs, projects, dashboard, org chart, reports, and more!",
            "I want to make sure I give you the right information. Could you ask your question differently? I'm here to help with various aspects of our organization system.",
            "I may not have understood your question correctly. Let me know if you'd like help with: employees, departments, roles, leave, attendance, work logs, announcements, projects, profile, dashboard, org chart, schedule, reports, or login assistance.",
        ],
    }
    
    @classmethod
    def get_response(cls, user_message, user=None, conversation_history=None):
        """Process user message and return professional bot response"""
        if not user_message:
            return random.choice(cls.RESPONSES['greeting']).format(org_name='IT Org')
        
        # Try LLM first if enabled
        if cls.LLM_ENABLED:
            llm_response, error = cls.get_llm_response(user_message, conversation_history, user)
            if llm_response:
                return llm_response
        
        message_lower = user_message.lower().strip()
        
        # Get organization name if user is provided
        org_name = 'IT Org'
        try:
            from apps.employees.models import OrganizationSettings
            settings = OrganizationSettings.get_settings()
            org_name = settings.organization_name
        except:
            pass
        
        # Check for blocked patterns
        for pattern in cls.BLOCKED_PATTERNS:
            if re.search(pattern, message_lower):
                return random.choice(cls.RESPONSES['security'])
        
        # Greetings
        if any(word in message_lower for word in ['hi', 'hello', 'hey', 'hiya', 'greetings', 'good morning', 'good afternoon', 'good evening']):
            return random.choice(cls.RESPONSES['greeting']).format(org_name=org_name)
        
        # Thanks
        if any(word in message_lower for word in ['thanks', 'thank', 'appreciate', 'grateful', 'thank you', 'thx']):
            return random.choice(cls.RESPONSES['thanks'])
        
        # Help request
        if any(word in message_lower for word in ['help', 'what can you do', 'capabilities', 'features', 'how does this work', 'guide', 'tutorial', 'what can you help with']):
            return random.choice(cls.RESPONSES['help'])
        
        # Goodbyes
        if any(word in message_lower for word in ['bye', 'goodbye', 'see you', 'stop', 'that is all', 'nothing else', 'exit']):
            return random.choice(cls.RESPONSES['goodbye']).format(org_name=org_name)
        
        # Casual acknowledgments - short responses without default message
        ack_words = ['ok', 'okay', 'okk', 'sure', 'yeah', 'yes', 'yup', 'fine', 'alright', 'cool', 'got it', 'understood', 'i see', 'k']
        if message_lower.strip() in ack_words or re.match(r'^(ok|okay|sure|fine|alright|cool)\.?$', message_lower.strip()):
            return "Great! Is there anything else I can help you with? Feel free to ask about employees, departments, projects, or any other topic!"
        
        # Match topics with priority order
        matched_topic = None
        
        # First check for more specific topics
        specific_topics = ['schedule_detailed', 'reports_detailed']
        for topic in specific_topics:
            for keyword in cls.HELP_TOPICS.get(topic.replace('_detailed', ''), []):
                if keyword in message_lower:
                    matched_topic = topic
                    break
            if matched_topic:
                break
        
        # Then check regular topics
        if not matched_topic:
            for topic, keywords in cls.HELP_TOPICS.items():
                for keyword in keywords:
                    if keyword in message_lower:
                        matched_topic = topic
                        break
                if matched_topic:
                    break
        
        # Return response if topic matched
        if matched_topic:
            topic_key = matched_topic + '_detailed' if matched_topic in ['schedule', 'reports'] else matched_topic
            response_list = cls.RESPONSES.get(topic_key, cls.RESPONSES.get(matched_topic, cls.RESPONSES['default']))
            response = random.choice(response_list)
            if '{org_name}' in response:
                response = response.format(org_name=org_name)
            return response
        
        # Default response
        default_response = random.choice(cls.RESPONSES['default'])
        if '{org_name}' in default_response:
            default_response = default_response.format(org_name=org_name)
        return default_response
    
    @classmethod
    def get_llm_response(cls, user_message, conversation_history=None, user=None):
        """Get response from LLM (OpenAI GPT)"""
        if not cls.LLM_ENABLED:
            return None, "LLM not configured"
        
        try:
            import requests
            
            org_name = 'IT Org'
            try:
                from apps.employees.models import OrganizationSettings
                settings = OrganizationSettings.get_settings()
                org_name = settings.organization_name
            except:
                pass
            
            system_prompt = cls.LLM_SYSTEM_PROMPT.format(org_name=org_name)
            
            messages = [{"role": "system", "content": system_prompt}]
            
            if conversation_history:
                for msg in conversation_history[-5:]:
                    messages.append({
                        "role": "user" if msg.get('is_user') else "assistant",
                        "content": msg.get('message', '')
                    })
            
            messages.append({"role": "user", "content": user_message})
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {cls.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": cls.LLM_MODEL,
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'], None
            else:
                return None, f"API error: {response.status_code}"
                
        except ImportError:
            return None, "requests library not installed"
        except Exception as e:
            return None, str(e)
