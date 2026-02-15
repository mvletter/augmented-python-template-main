# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python microservice template using Copier for generating new services at Holodeck/Voys. The template creates FastAPI-based services with a clean architecture pattern including adapters, core domain logic, and infrastructure layers.

## Key Development Commands

### Template Management
- **Generate new service from template**: `copier copy git@gitlab.wearespindle.com:holodeck/templates/python-template.git {PROJECT_NAME}`
- **Update existing project**: `copier update --conflict inline`

### Code Quality
- **Lint code**: `ruff check .`
- **Format code**: `ruff format .`
- **Type checking**: `mypy .`
- **Run all checks**: `pre-commit run --all-files`

### Testing
- **Run tests**: `pytest`
- **Run tests with coverage**: `pytest --cov`
- **Run specific test**: `pytest path/to/test_file.py::test_function`

### Service Management (Generated Services)
- **Run service**: `python manage.py runserver` (or use generated runserver script)
- **List commands**: `python manage.py` (shows available CLI commands)
- **Database migration**: `alembic upgrade head` (if database enabled)
- **Development setup**: `./scripts/verify_project.sh` (creates override files)

## Architecture Overview

The template follows Clean Architecture with three main layers:

### Core Layer (`service/core/`)
- **Entities**: Domain models and business objects
- **Use Cases**: Business logic and orchestration
- **Interfaces**: Abstract definitions for external dependencies

### Adapters Layer (`service/adapters/`)
- **HTTP**: FastAPI endpoints, request/response schemas, and HTTP-specific logic
- **NATS**: Event handling and messaging (optional)
- **Resgate**: Real-time API gateway integration (optional)

### Infrastructure Layer (`service/data/`)
- **Models**: SQLAlchemy database models
- **Repositories**: Data access implementations
- **Connectors**: Database, Redis, and NATS connection management

### Shared Components (`holo/`)
- Reusable code across services including:
  - Configuration management
  - Database/Redis connection handling
  - OpenTelemetry instrumentation
  - Common utilities and middleware

## Template Configuration

The template supports several configuration options via `copier.yml`:
- **include_database**: Adds PostgreSQL support with SQLAlchemy and Alembic
- **include_redis**: Adds Redis support for caching
- **use_nats**: Enables NATS messaging integration
- **use_resgate**: Adds Resgate real-time API support

## Dependency Injection

Services use a custom dependency injection system in `service/injector.py` that provides:
- Database sessions with transaction support
- Redis connections
- NATS connections
- Clean resource management

## Testing Framework

- Uses pytest with async support
- Polyfactory for test data generation
- Test fixtures in `service/testing/fixtures.py`
- Database test utilities and assertion helpers

## Monitoring and Observability

Generated services include:
- **Health endpoints**: `/ping`, `/health`, `/metrics`
- **OpenTelemetry**: Distributed tracing support
- **Prometheus**: Metrics collection
- **Sentry**: Error reporting
- **Segment**: Analytics tracking

## Key Files to Understand

- `service/server.py`: FastAPI application setup and configuration
- `service/injector.py`: Dependency injection and resource management
- `manage.py`: CLI command runner for service management
- `pyproject.toml`: Project dependencies and tool configuration
- `copier.yml`: Template configuration and questions
