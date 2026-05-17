# School AI Assistant

A modular FastAPI-based assistant for school workflows: messaging (Twilio/WhatsApp), STT, AI intent resolution, and administrative services.

## Features

- FastAPI HTTP API and route modules
- SQLAlchemy models and Alembic migrations
- Async task workers (Celery) for STT and notifications
- Pluggable AI services (OpenAI / Claude) and media handling

## Requirements

- Python 3.10+
- PostgreSQL (or configure another DB via `DATABASE_URL`)
- Redis (for Celery broker) — optional when running workers

## Quickstart (local)

1. Copy environment file and edit values:

```bash
cp .env.example .env
# edit .env to set DATABASE_URL, SECRET_KEY, TWILIO_* etc
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply database migrations:

```bash
alembic upgrade head
```

4. Run the app (development):

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker

Build and run with docker-compose:

```bash
docker-compose up --build
```

## Celery workers

Start a Celery worker for background tasks (requires Redis broker configured):

```bash
celery -A src.workers.celery_app worker -l info
```

## Testing

Run tests with pytest. A `tests/conftest.py` fixture will attempt to use the project's DB engine; consider configuring an ephemeral test DB or using SQLite for CI:

```bash
pytest -q
```

## Migrations

Alembic migration scripts live at the repo root `alembic/`. To create a new migration:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Project layout (high level)

- `src/` — application package
  - `db/` — SQLAlchemy engine, base, and models
  - `schemas/` — Pydantic schemas
  - `routes/` — FastAPI routes
  - `services/` — business logic and AI integrations
  - `core/` — config, dependencies, security
  - `workers/` — Celery app and tasks
- `tests/` — unit and integration tests

## Environment variables (common)

- `DATABASE_URL` — SQLAlchemy DB URL
- `SECRET_KEY` — app secret for JWTs
- `TWILIO_AUTH_TOKEN`, `TWILIO_ACCOUNT_SID`, `TWILIO_WHATSAPP_FROM`
- `REDIS_URL` — broker for Celery

## Contributing

Open issues or PRs for bugs and improvements. Add tests for new behavior.

## License

Specify your license here.
