# Copilot Instructions for AI Coding Agents

## Project Overview
This is a FastAPI-based user management CRUD application with:
- Prometheus monitoring (metrics endpoint)
- OpenTelemetry distributed tracing (OTLP exporter, Jaeger backend)
- psutil-based system metrics (CPU, memory)
- Structured logging support (standard logging, ready for structlog)
The codebase is modular, supporting RESTful user operations, metrics, and tracing.

## Architecture & Key Components
- **app/**: Main application package.
  - `main.py`: FastAPI app entry point. Imports routers, sets up Prometheus metrics, and configures OpenTelemetry tracing (OTLP exporter to Jaeger).
  - `api/user_routes.py`: Defines user-related API endpoints (CRUD).
  - `database/connection.py`: SQLAlchemy database connection setup.
  - `models/user.py`: SQLAlchemy user model definition.
  - `schemas/user.py`: Pydantic schemas for request/response validation.
  - `services/user_service.py`: Business logic for user operations.
  - `monitoring/metrics.py`: Prometheus metrics integration, system metrics (CPU/memory) via psutil.
- **run.py**: App runner (often used with Uvicorn).
- **requirements.txt**: Python dependencies (FastAPI, SQLAlchemy, Prometheus, OpenTelemetry, Jaeger, psutil, etc.).

## Developer Workflows
- **Run the app**: Use `python run.py` or `uvicorn app.main:app --reload` (see `dev/bin/uvicorn`).
- **Database**: SQLAlchemy is used; connection details in `app/database/connection.py`.
- **Tracing**: OpenTelemetry is configured in `main.py` with OTLP exporter to Jaeger (default endpoint: `localhost:4317`).
- **Monitoring**: Prometheus metrics at `/metrics`, includes system stats via psutil.
- **Logging**: Uses Python standard logging, ready for structlog integration.
- **Environment**: Local venv in `dev/` (activate with `source dev/bin/activate`).

## Patterns & Conventions
- **API Routing**: All user endpoints are in `app/api/user_routes.py`, registered in `main.py`.
- **Models/Schemas Separation**: SQLAlchemy models in `models/`, Pydantic schemas in `schemas/`.
- **Service Layer**: Business logic is separated into `services/` for maintainability.
- **Monitoring**: Prometheus metrics are exposed via `/metrics` endpoint (see `monitoring/metrics.py`).
- **Tracing**: OpenTelemetry spans are created for HTTP requests and key service/database operations.
- **System Metrics**: CPU and memory usage are collected using psutil and exposed in Prometheus metrics.
- **Logging**: Standard logging is set up; codebase is ready for structured logging with structlog if needed.
- **Imports**: Use absolute imports from `app.` root.

## Integration Points
- **Prometheus**: Metrics collected via `prometheus_client` and exposed for scraping.
- **OpenTelemetry**: Tracing via OTLP exporter to Jaeger (see `main.py`).
- **Jaeger**: Run Jaeger backend (Docker recommended) to view traces at http://localhost:16686.
- **psutil**: Used for system metrics in Prometheus.
- **FastAPI**: All API logic is built on FastAPI; use dependency injection for DB/session.
- **SQLAlchemy**: ORM for database access; models and session management in `database/` and `models/`.

## Examples
- Register a new user: `POST /api/v1/users/`
- Get user list: `GET /api/v1/users/`
- Prometheus metrics: `GET /metrics`
- Jaeger UI: [http://localhost:16686](http://localhost:16686)

## Tips for AI Agents
- When adding new endpoints, follow the pattern in `api/user_routes.py` and register in `main.py`.
- For new models, create SQLAlchemy classes in `models/` and matching Pydantic schemas in `schemas/`.
- Use the service layer for business logic, not in routers.
- Update `requirements.txt` for new dependencies and install in `dev/` venv.
- For tracing, add custom OpenTelemetry spans in service or database layers as needed.
- For system metrics, update Prometheus metrics via `PrometheusMetrics.update_system_metrics()`.
- For logging, use the standard logging module or integrate structlog for structured logs.

---
For questions or missing conventions, ask for clarification or examples from maintainers.
