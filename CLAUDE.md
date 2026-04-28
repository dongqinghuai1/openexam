# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OPENEXAM is a multi-role educational business platform with Vue 3 admin backend and Taro/React mobile portals for teachers, students, and parents. The Django REST API uses JWT authentication with a custom RBAC permission system.

## Quick Start

```bash
# Full system via Docker
docker-compose up -d

# Access points:
# Admin:   http://127.0.0.1:3000  (admin / admin123)
# Teacher: http://127.0.0.1:3001  (teacher / teacher123)
# Student: http://127.0.0.1:3002  (13800000002 / student123)
# Parent:  http://127.0.0.1:3003  (13800000003 / parent123)
# API:     http://127.0.0.1:8000
```

## Development Commands

### Backend (Django)
```bash
cd 04_后端开发/03_业务代码

# Setup
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# Initialize database and seed data
python manage.py migrate
python manage.py init_subjects
python manage.py init_admin
python manage.py init_demo_users
python manage.py init_permissions   # Initialize RBAC permissions

# Run development server
python manage.py runserver 8000
```

### Frontend - Admin (Vue 3)
```bash
cd 03_前端开发/01_管理后台
npm install
npm run dev        # Development server
npm run build      # Production build
npm run lint       # ESLint check
```

### Frontend - Taro Portals (Teacher/Student/Parent)
```bash
cd 03_前端开发/02_教师端   # or 03_学生端, 04_家长端
npm install
npm run dev:h5     # H5 development (fixed ports: 3001/3002/3003)
npm run build:h5   # H5 production build
```

## Architecture

### Backend Modules
Located in `04_后端开发/03_业务代码/`:
- **users/** - User model, JWT authentication, RBAC (roles/permissions/menus), operation logs
- **edu/** - Educational management (students, teachers, classes, courses, schedules)
- **classroom/** - Online classroom management
- **exam/** - Examination system (questions, papers, exams, scores)
- **finance/** - Financial management (orders, refunds)
- **eduadmin/** - Django project settings, URLs, pagination, exception handling

### Authentication Flow
JWT tokens are generated on login (`users/authentication.py:generate_token`). The `PermissionMiddleware` (`users/middleware.py`) validates tokens and attaches `user_permissions` set to every request. Superusers bypass permission checks.

### RBAC Permission System
- **User** has many **Roles** through **UserRole**
- **Role** has many **Permissions**
- **Permission** links to **Menu** for UI, plus `api_path` + `method` for API access control
- Permissions are initialized via `python manage.py init_permissions`
- Permission codes: `user_management`, `role_management`, `student_management`, `teacher_management`, `course_management`, `class_management`, `schedule_management`, `exam_management`, `question_management`, `paper_management`, `score_management`, `order_management`, `refund_management`, etc.

### API Routing Convention
The backend uses `DefaultRouter(trailing_slash=False)` - URLs do NOT have trailing slashes:
- `/api/users/login` (not `/api/users/login/`)
- `/api/users/me`
- `/api/edu/students`
- `/api/exam/papers`

### Frontend Structure
- **Admin** (`03_前端开发/01_管理后台/`): Vue 3 + Vite + Element Plus + Pinia + Vue Router
  - Views organized by module: `views/edu/`, `views/exam/`, `views/finance/`, `views/system/`
- **Taro Portals** (`02_教师端/`, `03_学生端/`, `04_家长端/`): Taro + React, fixed H5 dev ports

## Key Files
- Backend settings: `04_后端开发/03_业务代码/eduadmin/settings.py`
- JWT auth: `04_后端开发/03_业务代码/users/authentication.py`
- Permission middleware: `04_后端开发/03_业务代码/users/middleware.py`
- User model: `04_后端开发/03_业务代码/users/models.py`
- Permission decorator: `04_后端开发/03_业务代码/users/permissions.py`
- Docker compose: `docker-compose.yml` (root)
- API documentation: `03_前端开发/05_接口文档/API接口文档.md`

## Environment Variables
```bash
# Backend (.env)
DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_ENGINE=postgres
REDIS_URL
SECRET_KEY
JWT_SECRET_KEY
EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD, EMAIL_USE_TLS
```
