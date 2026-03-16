# Action Item Extractor

A FastAPI-based web application that extracts actionable items from text notes. Supports both heuristic-based and LLM-powered extraction using Ollama.

## Overview

This application provides a RESTful API for creating notes and extracting action items from their content. It features:

- **Note Management**: Create, read, update, and delete notes
- **Action Item Extraction**: Extract actionable items using:
  - Heuristic-based extraction (pattern matching)
  - LLM-powered extraction (Ollama)
- **Action Item Tracking**: Mark items as done/pending, filter by status
- **Simple Frontend**: Minimal HTML interface for quick testing
- **SQLite Database**: Persistent storage with repository pattern

## Project Structure

```
week02/
├── app/
│   ├── config.py              # Configuration management (Pydantic Settings)
│   ├── factory.py             # FastAPI application factory
│   ├── main.py                # App entry point
│   ├── database/
│   │   ├── connection.py      # Database connection management
│   │   └── repositories/      # Repository pattern implementations
│   │       ├── notes.py
│   │       └── action_items.py
│   ├── schemas/               # Pydantic models for API contracts
│   │   ├── notes.py
│   │   ├── action_items.py
│   │   └── errors.py
│   ├── services/              # Business logic layer
│   │   ├── notes.py
│   │   ├── action_items.py
│   │   ├── extract.py         # Extraction logic
│   │   └── exceptions.py      # Custom exception hierarchy
│   └── routers/               # FastAPI route handlers
│       ├── notes.py
│       └── action_items.py
├── frontend/
│   └── index.html             # Simple HTML frontend
├── tests/
│   ├── conftest.py            # Pytest fixtures
│   ├── test_schemas.py
│   ├── test_repositories.py
│   └── test_extract.py
├── data/                      # Database files
├── .env.example              # Environment configuration template
└── requirements.txt           # Python dependencies
```

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Ollama (optional, for LLM-based extraction)

### Installation

1. **Install dependencies**:

   ```bash
   # Using uv (recommended)
   uv sync

   # Or using pip
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:

   ```bash
   cp .env.example .env.dev
   # Edit .env.dev as needed
   ```

3. **Start Ollama** (optional, for LLM extraction):

   ```bash
   # Pull a model
   ollama pull llama3.1:8b

   # Start Ollama server
   ollama serve
   ```

### Running the Application

```bash
# Development server with auto-reload
uvicorn app.main:app --reload

# Or specify host and port
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application will be available at:
- **Frontend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Check application health status |

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/notes` | Create a new note |
| GET | `/notes` | List all notes (supports `limit` and `offset` query params) |
| GET | `/notes/{note_id}` | Get a specific note |
| PUT | `/notes/{note_id}` | Update a note |
| DELETE | `/notes/{note_id}` | Delete a note |

**Request/Response Models**:

```python
# POST /notes
NoteCreate:
  content: str  # Note content

NoteResponse:
  id: int
  content: str
  created_at: datetime
  updated_at: datetime

NoteListResponse:
  notes: List[NoteResponse]
  total: int
```

### Action Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/action-items/extract` | Extract action items from text (heuristic or LLM) |
| POST | `/action-items/extract-llm` | Extract action items using LLM |
| GET | `/action-items` | List action items (supports filtering) |
| GET | `/action-items/{action_item_id}` | Get a specific action item |
| POST | `/action-items` | Create a new action item directly |
| PUT | `/action-items/{action_item_id}` | Update an action item |
| POST | `/action-items/{action_item_id}/done` | Mark action item as done/pending |
| DELETE | `/action-items/{action_item_id}` | Delete an action item |
| GET | `/action-items/pending` | Get pending (not done) action items |
| GET | `/action-items/completed` | Get completed action items |

**Query Parameters for List Endpoints**:
- `note_id`: Filter by associated note
- `done`: Filter by completion status (true/false)
- `limit`: Max items to return (1-100)
- `offset`: Number of items to skip

**Request/Response Models**:

```python
# POST /action-items/extract or /action-items/extract-llm
ExtractRequest:
  text: str              # Text to extract from
  save_note: bool        # Whether to save text as a note

ExtractResponse:
  items: List[ActionItemResponse]
  note_id: Optional[int]  # ID of saved note (if save_note=true)

ActionItemResponse:
  id: int
  text: str
  done: bool
  note_id: Optional[int]
  created_at: datetime
  updated_at: datetime
```

**Example Usage**:

```bash
# Extract action items using heuristic
curl -X POST http://localhost:8000/action-items/extract \
  -H "Content-Type: application/json" \
  -d '{"text": "Meeting notes: Need to fix bug in login and update docs", "save_note": true}'

# Extract using LLM
curl -X POST http://localhost:8000/action-items/extract-llm \
  -H "Content-Type: application/json" \
  -d '{"text": "Schedule meeting with team, review PR, deploy to prod"}'

# List all action items
curl http://localhost:8000/action-items

# Mark item as done
curl -X POST http://localhost:8000/action-items/1/done \
  -H "Content-Type: application/json" \
  -d '{"done": true}'
```

## Testing

### Running Tests

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_extract.py -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

### Test Structure

- `tests/conftest.py` - Pytest fixtures and configuration
- `tests/test_schemas.py` - Pydantic schema validation tests
- `tests/test_repositories.py` - Database repository tests
- `tests/test_extract.py` - Extraction service tests

### Environment Variables for Testing

Create a `.env.test` file or the tests will use the default test environment settings defined in `conftest.py`.

## Configuration

Configuration is managed via environment variables using Pydantic Settings.

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment: dev, test, prod | dev |
| `DEBUG` | Enable debug mode | false |
| `APP_NAME` | Application name | Action Item Extractor |
| `APP_VERSION` | Application version | 1.0.0 |
| `DATABASE__PATH` | SQLite database path | data/app.db |
| `OLLAMA__MODEL` | Ollama model for LLM extraction | llama3.1:8b |
| `OLLAMA__BASE_URL` | Ollama server URL | http://localhost:11434 |
| `CORS_ORIGins` | Allowed CORS origins | ["*"] |

## Technology Stack

- **Framework**: FastAPI
- **Server**: Uvicorn
- **Database**: SQLite with SQLAlchemy
- **Validation**: Pydantic + Pydantic Settings
- **LLM**: Ollama (optional)
- **Testing**: pytest + pytest-asyncio

## License

MIT
