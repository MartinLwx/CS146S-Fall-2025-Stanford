# AGENTS.md - Agent Coding Guidelines for This Project

## Overview
This is a FastAPI-based notes and action items application with SQLite database. The codebase uses Python with SQLAlchemy ORM, Pydantic for schemas, and pytest for testing.

## Build/Lint/Test Commands

### Running the Application
```bash
make run
```
Runs the FastAPI server with uvicorn on `127.0.0.1:8000` by default. Use `HOST` and `PORT` environment variables to customize.

### Testing
```bash
# Run all tests
make test

# Run a single test file
PYTHONPATH=. uv run pytest -q backend/tests/test_notes.py

# Run a single test function
PYTHONPATH=. uv run pytest -q backend/tests/test_notes.py::test_create_and_list_notes

# Run with verbose output
PYTHONPATH=. uv run pytest -v backend/tests
```

### Code Formatting
```bash
# Format code with black and fix lint issues with ruff
make format
```

### Linting
```bash
# Run ruff linter
make lint
```

### Database Seeding
```bash
# Seed the database with initial data
make seed
```

### Pre-commit Hooks
```bash
# Install pre-commit hooks
uv tool run pre-commit install

# Run pre-commit manually
uv tool run pre-commit run --all-files
```

## Code Style Guidelines

### General
- Python 3.12+ with type hints required
- Use `PYTHONPATH=.` when running pytest or Python scripts
- Follow PEP 8 with Black formatting (line length 88)
- All code must pass `ruff check .` and `black .`

### Imports
- Use absolute imports: `from backend.app.db import get_db`
- Group imports in order: standard library, third-party, local
- Use `from collections.abc import Generator` instead of `from typing`

### Type Hints
- Always use type hints for function arguments and return types
- Use `Iterator[T]` from `collections.abc` for generator types
- Use `type: ignore` comments sparingly (e.g., `# noqa: BLE001` for intentional exception捕获)

### Naming Conventions
- **Files**: snake_case (e.g., `test_notes.py`, `action_items.py`)
- **Classes**: PascalCase (e.g., `Note`, `ActionItem`)
- **Functions/variables**: snake_case (e.g., `get_db`, `note_title`)
- **Constants**: UPPER_SNAKE_CASE (e.g., `DEFAULT_DB_PATH`)
- **Database tables**: snake_case (e.g., `notes`, `action_items`)

### Pydantic Schemas
- Use `BaseModel` from pydantic v2
- Create separate schemas for Create, Read, Update operations
- Use `from_attributes = True` in Config class for ORM compatibility
- Example:
  ```python
  class NoteCreate(BaseModel):
      title: str
      content: str

  class NoteRead(BaseModel):
      id: int
      title: str
      content: str

      class Config:
          from_attributes = True
  ```

### SQLAlchemy Models
- Use declarative base pattern
- Define `__tablename__` as snake_case plural
- Use appropriate column types: `String(200)`, `Text`, `Integer`, `Boolean`
- Always define primary key with `primary_key=True`

### Error Handling
- Use try/except with proper rollback in database operations
- Use context managers for session handling
- Let exceptions propagate appropriately for FastAPI to handle
- Example pattern from `db.py`:
  ```python
  def get_db() -> Iterator[Session]:
      session: Session = SessionLocal()
      try:
          yield session
          session.commit()
      except Exception:  # noqa: BLE001
          session.rollback()
          raise
      finally:
          session.close()
  ```

### FastAPI Routes
- Return appropriate HTTP status codes (200, 201, 404, etc.)
- Use dependency injection for database sessions
- Follow RESTful conventions for endpoints
- Document endpoints with docstrings

### Testing
- Use `pytest` with `fastapi.testclient.TestClient`
- Use the `client` fixture from `conftest.py` for API testing
- Create temporary databases for tests using `tempfile`
- Override database dependency for testing
- Use descriptive test names: `test_create_and_list_notes`

### Project Structure
```
week04/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app entry point
│   │   ├── db.py            # Database configuration
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   ├── routers/         # API route handlers
│   │   └── services/        # Business logic
│   └── tests/               # Test files with conftest.py
├── frontend/                # Static HTML/CSS/JS
├── data/                    # SQLite database
├── Makefile                 # Build commands
└── pre-commit-config.yaml   # Pre-commit hooks
```

### Environment Variables
- Use `.env` file with `python-dotenv`
- Default database path: `./data/app.db`
- Access via `os.getenv("VARIABLE_NAME", default_value)`

### Linters/Formatters Configuration
- **Black**: Line length 88 (default), Python 3.12+ target
- **Ruff**: Use `--fix` for auto-fixing, follows pyproject.toml settings
- **Pre-commit**: Runs black, ruff, end-of-file-fixer, trailing-whitespace
