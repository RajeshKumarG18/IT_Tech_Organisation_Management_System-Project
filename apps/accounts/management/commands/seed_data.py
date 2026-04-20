"""
Seed data command for IT Organization Management System
Preloads departments, roles, and creates sample employees
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.employees.models import Employee
from apps.departments.models import Department
from apps.roles.models import Role
import random

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed initial data for the IT Organization Management System'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=' * 50))
        self.stdout.write('Seeding IT Organization Management System...')
        self.stdout.write(self.style.WARNING('=' * 50))
        
        # Create Organizations Levels
        self._create_organization_levels()
        
        # Create Departments
        departments = self._create_departments()
        
        # Create Roles
        roles = self._create_roles(departments)
        
        # Create Admin User
        self._create_admin_user()
        
        # Create Sample Employees
        self._create_sample_employees(roles, departments)
        
        self.stdout.write(self.style.SUCCESS('\n' + '=' * 50))
        self.stdout.write('Seeding completed successfully!')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('\nLogin credentials:'))
        self.stdout.write(self.style.SUCCESS('  Admin: admin / admin123'))
        self.stdout.write(self.style.SUCCESS('  Manager: manager / manager123'))
        self.stdout.write(self.style.SUCCESS('  Employee: employee / employee123'))
    
    def _create_organization_levels(self):
        self.stdout.write('\nCreating organization levels...')
        from apps.accounts.models import OrganizationLevel
        
        levels = [
            ('EXECUTIVE', 'Executive Leadership', 1),
            ('UPPER_MANAGEMENT', 'Upper Management', 2),
            ('MIDDLE_MANAGEMENT', 'Middle Management', 3),
            ('SENIOR_PROFESSIONAL', 'Senior Professional', 4),
            ('JUNIOR_PROFESSIONAL', 'Junior Professional', 5),
            ('SUPPORT', 'Support Function', 6),
        ]
        
        for name, display, order in levels:
            OrganizationLevel.objects.get_or_create(
                name=name,
                defaults={'display_name': display, 'level_order': order}
            )
            self.stdout.write(f'  ✓ {display}')
    
    def _create_departments(self):
        self.stdout.write('\nCreating departments...')
        
        departments_data = [
            {'name': 'Engineering', 'code': 'ENG', 'description': 'Software development and technical infrastructure'},
            {'name': 'Product', 'code': 'PROD', 'description': 'Product management and design'},
            {'name': 'Human Resources', 'code': 'HR', 'description': 'Employee management and recruitment'},
            {'name': 'Finance', 'code': 'FIN', 'description': 'Financial planning and accounting'},
            {'name': 'IT Support', 'code': 'IT', 'description': 'Technical support and infrastructure'},
            {'name': 'Legal', 'code': 'LEG', 'description': 'Legal and compliance'},
            {'name': 'Admin', 'code': 'ADM', 'description': 'Administrative services'},
            {'name': 'Marketing', 'code': 'MKT', 'description': 'Marketing and communications'},
        ]
        
        departments = {}
        for dept_data in departments_data:
            dept, created = Department.objects.get_or_create(
                code=dept_data['code'],
                defaults=dept_data
            )
            departments[dept_data['code']] = dept
            self.stdout.write(f'  ✓ {dept.name}')
        
        return departments
    
    def _create_roles(self, departments):
        self.stdout.write('\nCreating roles...')
        
        roles_data = [
            # Executive Leadership
            {'title': 'CEO', 'level': 'EXECUTIVE', 'department': 'ENG', 'responsibilities': 'Company strategy, board relations, major decisions'},
            {'title': 'CTO', 'level': 'EXECUTIVE', 'department': 'ENG', 'responsibilities': 'Technology strategy, innovation, technical direction'},
            {'title': 'CIO', 'level': 'EXECUTIVE', 'department': 'IT', 'responsibilities': 'IT strategy, digital transformation'},
            {'title': 'CHRO', 'level': 'EXECUTIVE', 'department': 'HR', 'responsibilities': 'HR strategy, talent management'},
            
            # Upper Management
            {'title': 'VP Engineering', 'level': 'UPPER_MANAGEMENT', 'department': 'ENG', 'responsibilities': 'Engineering teams oversight, technical roadmap'},
            {'title': 'VP HR', 'level': 'UPPER_MANAGEMENT', 'department': 'HR', 'responsibilities': 'HR policies, talent acquisition'},
            {'title': 'Director Engineering', 'level': 'UPPER_MANAGEMENT', 'department': 'ENG', 'responsibilities': 'Engineering direction, project oversight'},
            {'title': 'Director Product', 'level': 'UPPER_MANAGEMENT', 'department': 'PROD', 'responsibilities': 'Product strategy, roadmap planning'},
            {'title': 'Head of HR', 'level': 'UPPER_MANAGEMENT', 'department': 'HR', 'responsibilities': 'HR operations, employee relations'},
            {'title': 'CFO', 'level': 'UPPER_MANAGEMENT', 'department': 'FIN', 'responsibilities': 'Financial strategy, planning'},
            
            # Middle Management
            {'title': 'Engineering Manager', 'level': 'MIDDLE_MANAGEMENT', 'department': 'ENG', 'responsibilities': 'Team management, sprint planning'},
            {'title': 'Product Manager', 'level': 'MIDDLE_MANAGEMENT', 'department': 'PROD', 'responsibilities': 'Product lifecycle, stakeholder management'},
            {'title': 'HR Manager', 'level': 'MIDDLE_MANAGEMENT', 'department': 'HR', 'responsibilities': 'HR team, recruitment processes'},
            {'title': 'Project Manager', 'level': 'MIDDLE_MANAGEMENT', 'department': 'ENG', 'responsibilities': 'Project coordination, timeline management'},
            {'title': 'Finance Manager', 'level': 'MIDDLE_MANAGEMENT', 'department': 'FIN', 'responsibilities': 'Financial reporting, budget management'},
            
            # Senior Professionals
            {'title': 'Senior Software Engineer', 'level': 'SENIOR_PROFESSIONAL', 'department': 'ENG', 'responsibilities': 'Complex development, code reviews, mentoring'},
            {'title': 'Senior Data Scientist', 'level': 'SENIOR_PROFESSIONAL', 'department': 'ENG', 'responsibilities': 'Data analysis, ML models, insights'},
            {'title': 'DevOps Engineer', 'level': 'SENIOR_PROFESSIONAL', 'department': 'ENG', 'responsibilities': 'CI/CD, infrastructure, cloud management'},
            {'title': 'HR Business Partner', 'level': 'SENIOR_PROFESSIONAL', 'department': 'HR', 'responsibilities': 'Employee relations, HR advisory'},
            {'title': 'UX Designer', 'level': 'SENIOR_PROFESSIONAL', 'department': 'PROD', 'responsibilities': 'User research, design systems'},
            
            # Junior Professionals
            {'title': 'Software Engineer', 'level': 'JUNIOR_PROFESSIONAL', 'department': 'ENG', 'responsibilities': 'Feature development, testing'},
            {'title': 'QA Engineer', 'level': 'JUNIOR_PROFESSIONAL', 'department': 'ENG', 'responsibilities': 'Quality assurance, test automation'},
            {'title': 'System Analyst', 'level': 'JUNIOR_PROFESSIONAL', 'department': 'IT', 'responsibilities': 'System analysis, requirements'},
            {'title': 'HR Executive', 'level': 'JUNIOR_PROFESSIONAL', 'department': 'HR', 'responsibilities': 'Recruitment, onboarding'},
            {'title': 'Marketing Executive', 'level': 'JUNIOR_PROFESSIONAL', 'department': 'MKT', 'responsibilities': 'Marketing campaigns, content'},
            
            # Support Functions
            {'title': 'HR Coordinator', 'level': 'SUPPORT', 'department': 'HR', 'responsibilities': 'HR admin, records management'},
            {'title': 'Finance Analyst', 'level': 'SUPPORT', 'department': 'FIN', 'responsibilities': 'Financial analysis, reporting'},
            {'title': 'IT Support Specialist', 'level': 'SUPPORT', 'department': 'IT', 'responsibilities': 'Technical support, helpdesk'},
            {'title': 'Legal Counsel', 'level': 'SUPPORT', 'department': 'LEG', 'responsibilities': 'Legal matters, contracts'},
            {'title': 'Administrative Assistant', 'level': 'SUPPORT', 'department': 'ADM', 'responsibilities': 'Office management, scheduling'},
        ]
        
        roles = {}
        for role_data in roles_data:
            dept = departments[role_data['department']]
            role, created = Role.objects.get_or_create(
                title=role_data['title'],
                department=dept,
                defaults={
                    'level': role_data['level'],
                    'responsibilities': role_data['responsibilities']
                }
            )
            roles[role_data['title']] = role
            self.stdout.write(f'  ✓ {role.title} ({role.get_level_display()})')
        
        return roles
    
    def _create_admin_user(self):
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@itorg.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
                user_type='ADMIN'
            )
            self.stdout.write(self.style.SUCCESS(f'\n✓ Admin user created: {admin.username}'))
    
    def _create_sample_employees(self, roles, departments):
        self.stdout.write('\nCreating sample employees...')
        
        # Sample employee data
        employees_data = [
            {'username': 'ceo', 'first_name': 'John', 'last_name': 'Smith', 'role': 'CEO', 'department': 'ENG', 'manager': None},
            {'username': 'cto', 'first_name': 'Sarah', 'last_name': 'Johnson', 'role': 'CTO', 'department': 'ENG', 'manager': 'ceo'},
            {'username': 'chro', 'first_name': 'Michael', 'last_name': 'Brown', 'role': 'CHRO', 'department': 'HR', 'manager': 'ceo'},
            {'username': 'cfo', 'first_name': 'Emily', 'last_name': 'Davis', 'role': 'CFO', 'department': 'FIN', 'manager': 'ceo'},
            
            {'username': 'vp_eng', 'first_name': 'David', 'last_name': 'Wilson', 'role': 'VP Engineering', 'department': 'ENG', 'manager': 'cto'},
            {'username': 'vp_hr', 'first_name': 'Jessica', 'last_name': 'Taylor', 'role': 'VP HR', 'department': 'HR', 'manager': 'chro'},
            {'username': 'dir_eng', 'first_name': 'Chris', 'last_name': 'Anderson', 'role': 'Director Engineering', 'department': 'ENG', 'manager': 'vp_eng'},
            {'username': 'dir_prod', 'first_name': 'Amanda', 'last_name': 'Martinez', 'role': 'Director Product', 'department': 'PROD', 'manager': 'cto'},
            
            {'username': 'eng_mgr', 'first_name': 'Ryan', 'last_name': 'Garcia', 'role': 'Engineering Manager', 'department': 'ENG', 'manager': 'dir_eng'},
            {'username': 'prod_mgr', 'first_name': 'Nicole', 'last_name': 'Robinson', 'role': 'Product Manager', 'department': 'PROD', 'manager': 'dir_prod'},
            {'username': 'hr_mgr', 'first_name': 'Steven', 'last_name': 'Clark', 'role': 'HR Manager', 'department': 'HR', 'manager': 'vp_hr'},
            {'username': 'fin_mgr', 'first_name': 'Lauren', 'last_name': 'Lewis', 'role': 'Finance Manager', 'department': 'FIN', 'manager': 'cfo'},
            
            {'username': 'senior_dev1', 'first_name': 'Kevin', 'last_name': 'Lee', 'role': 'Senior Software Engineer', 'department': 'ENG', 'manager': 'eng_mgr'},
            {'username': 'senior_dev2', 'first_name': 'Michelle', 'last_name': 'Walker', 'role': 'Senior Software Engineer', 'department': 'ENG', 'manager': 'eng_mgr'},
            {'username': 'devops', 'first_name': 'Brian', 'last_name': 'Hall', 'role': 'DevOps Engineer', 'department': 'ENG', 'manager': 'eng_mgr'},
            {'username': 'ux_designer', 'first_name': 'Stephanie', 'last_name': 'Allen', 'role': 'UX Designer', 'department': 'PROD', 'manager': 'prod_mgr'},
            {'username': 'hrbp', 'first_name': 'Daniel', 'last_name': 'Young', 'role': 'HR Business Partner', 'department': 'HR', 'manager': 'hr_mgr'},
            
            {'username': 'dev1', 'first_name': 'Jennifer', 'last_name': 'King', 'role': 'Software Engineer', 'department': 'ENG', 'manager': 'senior_dev1'},
            {'username': 'dev2', 'first_name': 'Matthew', 'last_name': 'Wright', 'role': 'Software Engineer', 'department': 'ENG', 'manager': 'senior_dev1'},
            {'username': 'qa1', 'first_name': 'Ashley', 'last_name': 'Lopez', 'role': 'QA Engineer', 'department': 'ENG', 'manager': 'eng_mgr'},
            {'username': 'hr_exec', 'first_name': 'Justin', 'last_name': 'Hill', 'role': 'HR Executive', 'department': 'HR', 'manager': 'hr_mgr'},
            
            {'username': 'it_support', 'first_name': 'Brittany', 'last_name': 'Scott', 'role': 'IT Support Specialist', 'department': 'IT', 'manager': 'cto'},
            {'username': 'admin_asst', 'first_name': 'Tyler', 'last_name': 'Green', 'role': 'Administrative Assistant', 'department': 'ADM', 'manager': 'ceo'},
        ]
        
        # Create mapping from username to User
        user_map = {}
        
        for emp_data in employees_data:
            username = emp_data['username']
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@itorg.com',
                    password=f'{username}123',
                    first_name=emp_data['first_name'],
                    last_name=emp_data['last_name'],
                    user_type='EMPLOYEE'
                )
                user_map[username] = user
                
                # Create Employee profile
                role = roles[emp_data['role']]
                department = departments[emp_data['department']]
                manager = None
                if emp_data['manager']:
                    manager_user = user_map.get(emp_data['manager'])
                    if manager_user:
                        manager = Employee.objects.filter(user=manager_user).first()
                
                employee, created = Employee.objects.get_or_create(
                    user=user,
                    defaults={
                        'employee_id': f'EMP{Employee.objects.count() + 1:04d}',
                        'first_name': emp_data['first_name'],
                        'last_name': emp_data['last_name'],
                        'email': user.email,
                        'department': department,
                        'role': role,
                        'reporting_manager': manager,
                        'date_of_joining': '2024-01-15',
                        'status': 'ACTIVE'
                    }
                )
                
                status_icon = '✓' if created else 'o'
                self.stdout.write(f'  {status_icon} {employee.full_name} - {role.title}')