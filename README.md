# IT Tech Organisation Management System

A professional Django-based IT Organization Management System with comprehensive features for managing organizational structure, employees, roles, departments, attendance, work logs, events, and more.


## Project Overview



### Architecture

- **Framework**: Django 5.x (MVT Architecture)
- **API Layer**: Django Rest Framework (DRF)
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Database**: PostgreSQL (with SQLite fallback for development)
- **UI**: Bootstrap 5 + Chart.js for visualizations


### Core Technologies

- Python 3.10+
- PostgreSQL (production) / SQLite (development)
- Django Rest Framework
- SimpleJWT Authentication
- CORS Headers
- Chart.js (Dashboard visualizations)

---


## Project Structure


```
IT Tech Organisation Management System/
├── core/                          # Core configuration
│   ├── settings.py              # Django settings
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py              # WSGI entry point
├── apps/                         # Application modules
│   ├── accounts/            # User authentication & profiles
│   ├── employees/            # Employee management
│   ├── roles/               # Role management
│   ├── departments/         # Department management
│   └── dashboard/           # Dashboard & web views
├── templates/                   # HTML templates
│   ├── base.html
│   ├── dashboard/
│   ├── employees/
│   └── registration/
├── static/
│   └── css/styles.css
├── media/                      # Uploaded files
└── requirements.txt
```


---


## Database Schema


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

#### 4. Employee
| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| employee_id | Char | Unique employee ID |
| user | OneToOne | User profile |
| department | FK | Department |
| role | FK | Role |
| reporting_manager | FK | Self-reference (manager) |
| date_of_joining | Date | Join date |
| status | Enum | ACTIVE, INACTIVE, ON_LEAVE, TERMINATED |
| profile_image | Image | Profile photo |

#### 5. Attendance
| Field | Type | Description |
|-------|------|-------------|
| employee | FK | Employee |
| date | Date | Attendance date |
| check_in | DateTime | Check in time |
| check_out | DateTime | Check out time |
| check_in_photo | Image | Check in photo (face capture) |
| check_out_photo | Image | Check out photo (face capture) |
| status | Enum | PRESENT, ABSENT, LATE, ON_LEAVE |

#### 6. WorkLog
| Field | Type | Description |
|-------|------|-------------|
| employee | FK | Employee |
| date | Date | Work date |
| project | Char | Project name |
| feature | Char | Feature/task |
| category | Enum | DEVELOPMENT, MEETING, etc. |
| work_description | Text | Work description |
| duration | Duration | Work duration |
| work_mode | Enum | OFFICE, REMOTE, HYBRID |

#### 7. Event
| Field | Type | Description |
|-------|------|-------------|
| title | Char | Event title |
| description | Text | Event description |
| event_type | Enum | MEETING, TRAINING, etc. |
| location | Char | Event location |
| meeting_link | URL | Meeting link (Zoom, Google Meet) |
| start_datetime | DateTime | Start time |
| end_datetime | DateTime | End time |
| status | Enum | SCHEDULED, IN_PROGRESS, COMPLETED |
| created_by | FK | User who created |

#### 8. LeaveRequest
| Field | Type | Description |
|-------|------|-------------|
| employee | FK | Employee |
| leave_type | Enum | ANNUAL, SICK, etc. |
| start_date | Date | Start date |
| end_date | End date |
| reason | Text | Reason |
| status | Enum | PENDING, APPROVED, REJECTED |

#### 9. Announcement
| Field | Type | Description |
|-------|------|-------------|
| title | Char | Announcement title |
| content | Text | Content |
| priority | Enum | LOW, NORMAL, HIGH, URGENT |
| created_by | FK | User |
| created_at | DateTime | Created time |

#### 10. Project
| Field | Type | Description |
|-------|------|-------------|
| name | Char | Project name |
| description | Text | Description |
| team | FK | Department/Team |
| status | Enum | PLANNING, IN_PROGRESS, etc. |
| progress | Integer | Progress percentage |
| start_date | Date | Start date |
| end_date | Date | End date |

#### 11. OrganizationSettings
| Field | Type | Description |
|-------|------|-------------|
| organization_name | Char | Organization name |
| logo | Image | Logo image |
| favicon | Image | Favicon |

---

## API Endpoints

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

### ChatBot
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/dashboard/chatbot/` | ChatBot API |

---

## UI Routes

| Endpoint | Description |
|----------|-------------|
| `/login/` | Login page |
| `/logout/` | Logout |
| `/dashboard/` | Main dashboard |
| `/profile/` | User profile |
| `/employees/` | Employee list |
| `/org-chart/` | Organization chart |
| `/worklog/` | Work log & attendance |
| `/schedule/` | Events & leave requests |
| `/reports/` | Reports & analytics |
| `/chatbot/` | Organization ChatBot |
| `/admin/` | Admin panel |

---

## Getting Started

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

## Default Login Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin |  |  |

---

## Features Implemented

### ✅ Core Features
- [x] Django MVT Architecture
- [x] Role-based authentication (ADMIN, EXECUTIVE, MANAGER, HR, EMPLOYEE)
- [x] Employee management (CRUD)
- [x] Department hierarchy
- [x] Role management with 6 levels
- [x] Manager-subordinate relationships
- [x] JWT Authentication
- [x] REST APIs with DRF

### ✅ Dashboard Features
- [x] Executive dashboard with stats widgets
- [x] Orange (#FF6B00) + Dark Blue (#0B1F3A) theme
- [x] Stats ticker
- [x] Quick actions buttons
- [x] Interactive charts (Chart.js)
- [x] Mini stat cards
- [x] Recent activity feed
- [x] Notifications & alerts
- [x] Calendar widget
- [x] Task list
- [x] Skills matrix
- [x] Training status
- [x] Top performers
- [x] Upcoming events
- [x] Leave requests
- [x] Announcements
- [x] Project status
- [x] Mobile-responsive sidebar

### ✅ Organization Management
- [x] Organization Settings (name, logo, favicon)
- [x] Dynamic organization name updates everywhere
- [x] Custom admin panel

### ✅ ChatBot Features
- [x] Organisation ChatBot with detailed responses
- [x] Advanced keyword matching
- [x] Security - blocks sensitive info requests
- [x] Casual acknowledgment handling
- [x] Floating ChatBot widget in sidebar
- [x] ChatBot accessible from both main app and Admin Panel
- [x] Conversation history storage
- [x] LLM Integration support (OpenAI GPT)

### ✅ Schedule & Reports
- [x] Schedule page (`/schedule/`)
- [x] Upcoming events with meeting links
- [x] Pending leave requests
- [x] Reports page (`/reports/`)
- [x] Employee statistics
- [x] Work logs table
- [x] Meeting records (upcoming & past)
- [x] Meeting statistics

### ✅ Meetings/Events
- [x] Meeting link field (Zoom, Google Meet URLs)
- [x] Event types (Meeting, Training, Holiday, etc.)
- [x] Auto status based on time (Scheduled, In Progress, Completed)
- [x] Clickable meeting links
- [x] Past meetings tracking in Reports

### ✅ Attendance & Work Log
- [x] Check In with face capture
- [x] Check Out with face capture
- [x] Camera access for photo capture
- [x] Photo preview before submitting
- [x] Retake photo option
- [x] 3-step work log workflow:
  - Step 1: Fill work details
  - Step 2: Capture photo & Check Out
  - Step 3: Save (enables only when both complete)
- [x] Attendance photo display
- [x] Recent work logs display
- [x] Read-only photos in admin

### ✅ UI/UX Features
- [x] Professional dashboard layout
- [x] Animated backgrounds
- [x] Hover effects on cards
- [x] Custom scrollbar
- [x] Gradient stat cards with trends
- [x] Chart animations
- [x] Responsive design

### ✅ Bug Fixes
- [x] Fixed duplicate sidebar links
- [x] URL namespace warning resolved
- [x] Login error message in red
- [x] ChatBot "ok" response improved

---

## Theme Colors

| Color | Hex | Usage |
|-------|-----|-------|
| Primary (Orange) | #FF6B00 | Buttons, highlights, gradients |
| Secondary (Dark Blue) | #0B1F3A | Sidebar, headers, backgrounds |

---

## Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=*
OPENAI_API_KEY=your-openai-api-key  # Optional - for LLM ChatBot
```

---

## License

MIT License

---

## Author

IT Tech Organisation Management System
Built with Django + DRF + Bootstrap + Chart.js