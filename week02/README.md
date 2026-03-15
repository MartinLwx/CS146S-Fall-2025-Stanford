# Week 02: Action Item Extractor (Refactored)

Refactored backend application with improved architecture, error handling, and testing.

## Architecture Overview

- **Configuration**: Multi-environment settings using Pydantic Settings
- **Database Layer**: Repository pattern with connection pooling
- **Service Layer**: Business logic with custom exception hierarchy
- **API Layer**: FastAPI routers with Pydantic schemas and dependency injection
- **Error Handling**: Structured error responses with error codes
- **Testing**: Comprehensive unit tests with pytest fixtures

## Key Improvements

1. **Well-defined API contracts** using Pydantic models
2. **Repository pattern** separating database operations from business logic
3. **Environment-specific configuration** (dev, test, prod)
4. **Structured error handling** with consistent error response format
5. **Application factory** with lifespan management and middleware
6. **Comprehensive unit tests** for schemas, repositories, and services

## Project Structure

```
app/
├── config.py              # Configuration management
├── database/              # Database layer (connection, repositories)
├── schemas/               # Pydantic models for API contracts
├── services/              # Business logic and custom exceptions
├── routers/               # FastAPI route handlers
├── factory.py             # Application factory with lifespan
└── main.py               # App entry point

tests/
├── conftest.py           # Test fixtures
├── test_schemas.py       # Schema validation tests
├── test_repositories.py  # Repository unit tests
└── test_extract.py       # Extraction service tests
```

## Setup

1. Install dependencies using uv (recommended) or pip:
   ```bash
   uv sync  # from parent directory
   ```

2. Configure environment variables:
   ```bash
   cp .env.example .env.dev
   # Edit .env.dev as needed
   ```

3. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## API Documentation

Once running, interactive OpenAPI documentation is available at:
- `/docs` - Swagger UI
- `/redoc` - ReDoc

## Testing

Run tests with:
```bash
pytest tests/ -v
```

## Environment Variables

See `.env.example` for available configuration options.

## Dependencies

- FastAPI + Uvicorn
- Pydantic + Pydantic Settings
- Ollama (for LLM-based extraction)
- SQLite (built-in)
- pytest (testing)

All dependencies are managed via uv/pyproject.toml in the parent directory.