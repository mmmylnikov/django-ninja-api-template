# Django Ninja API Template

[![CI](https://github.com/mmmylnikov/django-ninja-api-template/actions/workflows/ci.yml/badge.svg)](https://github.com/mmmylnikov/django-ninja-api-template/actions/workflows/ci.yml)
![Django](https://img.shields.io/badge/Django-092E20?logo=django&logoColor=white)
![Django Ninja](https://img.shields.io/badge/Django_Ninja-F55247?logo=ninja&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)
![gRPC](https://img.shields.io/badge/gRPC-244C5A?logo=grpc&logoColor=white)
![Celery](https://img.shields.io/badge/Celery-37814A?logo=celery&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-2088FF?logo=github-actions&logoColor=white)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)


A flexible project template for building modern Django Ninja API services with
JWT authentication, gRPC integration, and vector (full-text) search support in
PostgreSQL. This template is ideal for rapid prototyping or as a foundation
for scalable backend systems.

---

## Features

- **Django Ninja** framework with fast OpenAPI support
- **JWT authentication** (login, refresh)
- **gRPC integration** (sample notification server included)
- **Vector and full-text search** in PostgreSQL
- **Docker Compose** setup for development (database, valkey, notify server, 
    backend, celery worker/beat/flower)
- **Celery integration** (background tasks, scheduling, monitoring)
- **Custom management commands** (e.g., sample user data)
- **Clean project structure** with `api.py`, `schemas.py`, `services.py`
    in each app
- **Ready-to-use user roles** and event-related entities

---

## Stack & Services

This project uses Docker Compose for easy local development. The following
services are available:

- **database**: PostgreSQL 14 (with vector and full-text search enabled)
- **valkey**: Lightning-fast in-memory key-value store (Valkey)
- **backend**: Django app running on port `8080`
- **celery_worker**: Celery worker for async/background tasks
- **celery_beat**: Celery Beat for scheduled tasks
- **celery_flower**: Flower monitoring UI (available at port `5555`)
- **notification-server**: Test gRPC notification server

---

## Quickstart

1. **Clone the repository and start services:**
    ```sh
    docker compose up --build
    ```

2. **Perform the necessary migrations:**
    ```sh
    docker compose exec backend python manage.py migrate
    ```

3. **Optional: initialize test data (admin, organizer, visitor):**
    ```sh
    docker compose exec backend python manage.py initdata
    ```

4. **Access API documentation (OpenAPI/Swagger):**
    - http://localhost:8080/api/docs

5. **Access Flower UI:**
    - http://localhost:5555

---

## Authentication

- JWT is used for authentication.
- Register a user and get a token for further requests.
- Use the "Authorization: Bearer <token>" header.

---

## Example Endpoints

| Method | URL                            | Description            |
|--------|--------------------------------|------------------------|
| POST   | /api/users/register            | Register User          |
| POST   | /api/auth/login                | Login (JWT)            |
| POST   | /api/auth/token/refresh        | Token Refresh          |
| GET    | /api/events/                   | List Events            |
| POST   | /api/events/                   | Create Event           |
| GET    | /api/events/upcoming/          | User Upcoming Events   |
| GET    | /api/events/{event_id}/        | Get Event Details      |
| DELETE | /api/events/{event_id}/        | Delete Event           |
| PATCH  | /api/events/{event_id}/status/ | Update Event Status    |
| POST   | /api/events/{event_id}/book/   | Book Event             |
| DELETE | /api/events/{event_id}/book/   | Cancel Booking         |

---

## Notifications

- A sample gRPC notification server is included and receives notification
  messages.
- Easily integrate real notification services by changing the gRPC server logic.

---

## Management Commands

- `python manage.py initdata` — creates test users: **admin**, **organizer**, **visitor**.

---

## Configuration

The project uses environment variables for configuration. Create a `.env` file 
in the project root with the following variables:

```txt
DEBUG=True
DEBUG_HOST=127.0.0.1
DEBUG_PORT=8080

LANGUAGE_CODE=ru-RU
TIME_ZONE=Asia/Yekaterinburg

SECRET_KEY=your-secret-key
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=django.db.backends.postgresql
DB_NAME=django_db
DB_USER=django_user
DB_PASSWORD=django_password
DB_PASSWORD_ROOT=django_password_root
DB_HOST=database
DB_PORT=5432

CELERY_BROKER_URL=redis://valkey:6379/0
CELERY_RESULT_BACKEND=django-db

GRPC_SERVER_HOST=notification-server
GRPC_SERVER_PORT=50051
```

## Development Setup

### Prerequisites

- Docker and Docker Compose
- uv
- Python 3.13+
- Make (optional, for running Makefile commands)

### Local Development

1. **Clone the repository:**
```sh
git clone https://github.com/mmmylnikov/django-ninja-api-template.git
cd django-ninja-api-template
```

2. Create a virtual environment:

```sh
uv sync
```

### Makefile Commands

The project includes a Makefile with various commands to streamline development:

#### Code Quality
```sh
# Check WPS coding style issues
uv run make style_wps

# Run Ruff linter
uv run make style_ruff

# Format code with Ruff
uv run make format_ruff

# Run all style checks and formatting
uv run make style

# Run type checking with mypy
uv run make types

# Run all checks (style + type checking)
uv run make check
```

#### Project Management

```sh
# Run Django development server
uv run make debug

# Run migrations
uv run make migrate

# Initialize test data
uv run make initdata
```

#### Celery Management

```sh
# Run Celery worker
uv run make celery

# Run Celery Beat scheduler
uv run make celery_beat

# Run Celery Flower monitoring
uv run make celery_flower
```

#### gRPC

```sh
# Generate Python code from Protocol Buffer definition
uv run make notify_build_proto
```

#### CI/CD

```sh
# Run locally CI Workflow
uv run make actci
```
