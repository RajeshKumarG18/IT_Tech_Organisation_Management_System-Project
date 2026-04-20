# IT Tech Organization Management System

A production-ready Django-based IT Organization Management System with comprehensive features for managing organizational structure, employees, roles, and departments.

##  Project Overview

### Architecture
- **Framework**: Django 5.x (MVT Architecture)
- **API Layer**: Django Rest Framework (DRF)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL (with SQLite fallback for development)
- **UI**: Bootstrap 5 + D3.js for visualizations

### Core Technologies
- Python 3.10+
- PostgreSQL (production) / SQLite (development)
- Django Rest Framework
- SimpleJWT Authentication
- CORS Headers
- D3.js (Org Chart visualization)

---

##  Project Structure

```
IT Tech Organisation Management System/
├── core/                          # Core configuration
│   ├── settings.py              # Django settings
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py              # WSGI entry point
├── apps/                         # Application modules
│   ├── accounts/            # User authentication & profiles
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── admin.py
│   │   └── management/
│   │       └── commands/
│   │           └── seed_data.py
│   ├── employees/            # Employee management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── admin.py
│   ├── roles/               # Role management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── admin.py
│   ├── departments/         # Department management
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── admin.py
│   └── dashboard/           # Dashboard & web views
│       ├── views.py
│       ├── web_views.py
│       └── urls.py
├── templates/                   # HTML templates
│   ├── base.html
│   ├── dashboard/
│   ├── employees/
│   └── registration/
├── static/
│   ├── css/styles.css
│   └── js/
└── requirements.txt
```

---

##  Database Schema

### Organization Levels (6 Levels)
- **Executive Leadership** (CEO, CTO, CIO, CHRO)
- **Upper Management** (VP, Directors)
- **Middle Management** (Managers)
- **Senior Professionals** (Senior Engineers, etc.)
- **Junior Professionals** (Engineers, etc.)
- **Support Functions** (HR, Finance, IT Support)

### Models

#### 1. CustomUser
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| username | Char | Unique username |
| email | Email | Unique email |
| user_type | Enum | ADMIN, EXECUTIVE, MANAGER, HR, EMPLOYEE |
| first_name | Char | First name |
| last_name | Char | Last name |

#### 2. Department
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | Char | Department name |
| code | Char | Unique code |
| description | Text | Description |
| parent_department | FK | Parent department (self-referential) |

#### 3. Role
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| title | Char | Role title |
| level | Enum | 6 organization levels |
| department | FK | Department |
| description | Text | Role description |
| responsibilities | Text | Key responsibilities |

#### 4. Employee
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| employee_id | Char | Unique employee ID |
| user | OneToOne | User profile |
| first_name | Char | First name |
| last_name | Char | Last name |
| email | Email | Email |
| phone | Char | Phone number |
| department | FK | Department |
| role | FK | Role |
| reporting_manager | FK | Self-reference (manager) |
| date_of_joining | Date | Join date |
| status | Enum | ACTIVE, INACTIVE, ON_LEAVE, TERMINATED |
| profile_image | Image | Profile photo |

---

##  API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/accounts/token/` | Get JWT token |
| POST | `/api/accounts/token/refresh/` | Refresh JWT token |

### Employees
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employees/` | List employees |
| POST | `/api/employees/` | Create employee |
| GET | `/api/employees/{id}/` | Get employee |
| PUT | `/api/employees/{id}/` | Update employee |
| DELETE | `/api/employees/{id}/` | Delete employee |

### Departments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/departments/` | List departments |
| POST | `/api/departments/` | Create department |

### Roles
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/roles/` | List roles |
| POST | `/api/roles/` | Create role |

### Dashboard
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/dashboard/org-chart/` | Organization chart data |
| GET | `/api/dashboard/api/` | Dashboard statistics |

---

##  UI Routes

| Endpoint | Description |
|----------|-------------|
| `/login/` | Login page |
| `/dashboard/` | Main dashboard |
| `/employees/` | Employee list |
| `/org-chart/` | Organization chart |
| `/worklog/` | Work log |
| `/profile/` | User profile |

---

##  Getting Started

### 1. Clone and Setup
```bash
git clone <repository-url>
cd "IT Tech Organisation Management System"
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Run Migrations
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

### 3. Seed Initial Data
```bash
python3 manage.py seed_data
```

### 4. Run Server
```bash
python3 manage.py runserver
```

### 5. Access
- **Web UI**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/
- **API**: http://127.0.0.1:8000/api/

---

##  Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Manager | manager | manager123 |
| Employee | employee | employee123 |

---

##  Features

### ✅ Implemented
- [x] Django MVT Architecture
- [x] Role-based authentication
- [x] Employee management (CRUD)
- [x] Department hierarchy
- [x] Role management with 6 levels
- [x] Manager-subordinate relationships
- [x] Role-based dashboards
- [x] D3.js Organization Chart
- [x] JWT Authentication
- [x] REST APIs with DRF
- [x] Search and filtering
- [x] Pagination
- [x] PostgreSQL support
- [x] Seed data management

### 🚧 Planned
- [ ] API Documentation (Swagger/OpenAPI)
- [ ] Multi-tenancy
- [ ] Audit logging
- [ ] WebSocket notifications

---

##  Theme Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Primary (Orange) | #FF6B00 | Buttons, highlights |
| Secondary (Dark Blue) | #0B1F3A | Sidebar, headers |

---

##  License

MIT License - See LICENSE file for details.

---

##  Author

IT Tech Organisation Management System
Built with Django + DRF + Bootstrap + D3.js