# Copilot Instructions for AI Coding Agents

## Project Overview
This is a FastAPI-based user management CRUD application with Prometheus monitoring. The codebase is organized for modularity and clarity, supporting RESTful user operations and metrics collection.

## Architecture & Key Components
- **app/**: Main application package.
  - `main.py`: FastAPI app entry point. Imports routers and sets up Prometheus metrics.
  - `api/user_routes.py`: Defines user-related API endpoints (CRUD).
  - `database/connection.py`: SQLAlchemy database connection setup.
  - `models/user.py`: SQLAlchemy user model definition.
  - `schemas/user.py`: Pydantic schemas for request/response validation.
  - `services/user_service.py`: Business logic for user operations.
  - `monitoring/metrics.py`: Prometheus metrics integration.
- **run.py**: App runner (often used with Uvicorn).
- **requirements.txt**: Python dependencies (FastAPI, SQLAlchemy, Prometheus, etc.).

## Developer Workflows
- **Run the app**: Use `python run.py` or `uvicorn app.main:app --reload` (see `dev/bin/uvicorn`).
- **Database**: SQLAlchemy is used; connection details in `app/database/connection.py`.
- **Testing**: No explicit test suite found; add tests in `tests/` if needed.
- **Environment**: Local venv in `dev/` (activate with `source dev/bin/activate`).

## Patterns & Conventions
- **API Routing**: All user endpoints are in `app/api/user_routes.py`, registered in `main.py`.
- **Models/Schemas Separation**: SQLAlchemy models in `models/`, Pydantic schemas in `schemas/`.
- **Service Layer**: Business logic is separated into `services/` for maintainability.
- **Monitoring**: Prometheus metrics are exposed via `/metrics` endpoint (see `monitoring/metrics.py`).
- **Imports**: Use absolute imports from `app.` root.

## Integration Points
- **Prometheus**: Metrics collected via `prometheus_client` and exposed for scraping.
- **FastAPI**: All API logic is built on FastAPI; use dependency injection for DB/session.
- **SQLAlchemy**: ORM for database access; models and session management in `database/` and `models/`.

## Examples
- Register a new user: `POST /users/`
- Get user list: `GET /users/`
- Prometheus metrics: `GET /metrics`

## Tips for AI Agents
- When adding new endpoints, follow the pattern in `api/user_routes.py` and register in `main.py`.
- For new models, create SQLAlchemy classes in `models/` and matching Pydantic schemas in `schemas/`.
- Use the service layer for business logic, not in routers.
- Update `requirements.txt` for new dependencies and install in `dev/` venv.

---
For questions or missing conventions, ask for clarification or examples from maintainers.
