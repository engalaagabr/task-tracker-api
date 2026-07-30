# Task Tracker API

Task Tracker API is a Django REST Framework backend that provides JWT-authenticated project and task management. Each authenticated user manages their own projects, and tasks are managed as nested resources under projects.

## Features

- User registration endpoint
- JWT token obtain and refresh endpoints
- CRUD for projects
- CRUD for tasks under `/projects/{project_id}/tasks/`
- Task filtering (`status`, `priority`)
- Task search (`title`, `description`)
- Task ordering (`due_date`, `created_at`, `priority`)
- Page-number pagination (`PAGE_SIZE=10`)

## Tech Stack

- Python
- Django
- Django REST Framework
- djangorestframework-simplejwt
- django-filter
- drf-nested-routers
- SQLite (default local DB)

## Architecture

```text
User
└── Project
    └── Task
```

Projects are owned by users, and tasks belong to projects. Task endpoints are nested to preserve this parent-child context.

## API Endpoints

| Method | Path | Auth |
|---|---|---|
| POST | `/api/register/` | No |
| POST | `/api/token/` | No |
| POST | `/api/login/` | No |
| POST | `/api/token/refresh/` | No |
| GET, POST | `/api/projects/` | Yes |
| GET, PUT, PATCH, DELETE | `/api/projects/{id}/` | Yes |
| GET, POST | `/api/projects/{project_id}/tasks/` | Yes |
| GET, PUT, PATCH, DELETE | `/api/projects/{project_id}/tasks/{id}/` | Yes |

## Authentication

Protected endpoints use Bearer JWT access tokens:

`Authorization: Bearer <access_token>`

Use `/api/token/` (or `/api/login/`) for access/refresh tokens, and `/api/token/refresh/` for access token renewal.

## Querying Tasks

Examples for `GET /api/projects/{project_id}/tasks/`:

- Filter: `?status=TODO`
- Filter: `?priority=HIGH`
- Search: `?search=report`
- Ordering: `?ordering=-due_date`
- Pagination: `?page=2`
- Combined: `?status=IN_PROGRESS&ordering=created_at&page=1`

## Project Structure

```text
.
├── manage.py
├── project/
│   ├── settings.py
│   └── urls.py
└── main/
    ├── models.py
    ├── serializers.py
    ├── views.py
    ├── urls.py
    └── migrations/
```

## Getting Started

```bash
git clone <repository-url>
cd task-tracker-api
python -m venv .venv
source .venv/bin/activate
pip install django djangorestframework djangorestframework-simplejwt django-filter drf-nested-routers
python manage.py migrate
python manage.py runserver
```

## Security

- JWT authentication is required for project/task endpoints.
- Project queries are scoped to the authenticated owner.
- Task query access is scoped by nested project and project owner.

## Future Improvements

- Add automated tests for auth, ownership, and nested-resource access
- Add OpenAPI/Swagger API documentation
- Move settings to environment-based configuration for deployment
- Add a dependency manifest (`requirements.txt` or `pyproject.toml`)
- Add CI checks (tests + lint) for pull requests
