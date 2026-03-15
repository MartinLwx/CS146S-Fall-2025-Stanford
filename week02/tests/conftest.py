from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.database.connection import DatabaseConnection, get_database_connection
from app.database.repositories.action_items import ActionItemRepository
from app.database.repositories.notes import NoteRepository
from app.factory import create_app
from app.services import ActionItemService, NoteService


# Set test environment
os.environ["ENVIRONMENT"] = "test"


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Test settings fixture."""
    # Override settings for testing
    settings = Settings(_env_file=".env.test")
    return settings


@pytest.fixture(scope="function")
def test_db_connection(test_settings: Settings) -> Generator[DatabaseConnection, None, None]:
    """Test database connection fixture (function scope)."""
    # Create a temporary database file for testing
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)

    # Override database path
    test_settings.database.path = db_path

    # Create connection with test settings
    connection = DatabaseConnection(database_path=db_path)
    connection.initialize_database()

    yield connection

    # Cleanup
    connection.close_connection()
    if db_path.exists():
        db_path.unlink()


@pytest.fixture(scope="function")
def note_repository(test_db_connection: DatabaseConnection) -> NoteRepository:
    """Note repository fixture."""
    return NoteRepository(connection=test_db_connection)


@pytest.fixture(scope="function")
def action_item_repository(test_db_connection: DatabaseConnection) -> ActionItemRepository:
    """Action item repository fixture."""
    return ActionItemRepository(connection=test_db_connection)


@pytest.fixture(scope="function")
def note_service(note_repository: NoteRepository) -> NoteService:
    """Note service fixture."""
    return NoteService(note_repository=note_repository)


@pytest.fixture(scope="function")
def action_item_service(
    action_item_repository: ActionItemRepository,
    note_repository: NoteRepository,
) -> ActionItemService:
    """Action item service fixture."""
    return ActionItemService(
        action_item_repository=action_item_repository,
        note_repository=note_repository,
    )


@pytest.fixture(scope="function")
def test_client() -> Generator[TestClient, None, None]:
    """Test client fixture."""
    # Create app with test settings
    app = create_app()

    with TestClient(app) as client:
        yield client


# Sample test data
@pytest.fixture
def sample_note_data() -> dict:
    """Sample note data for testing."""
    return {
        "content": "Test note content for unit testing.",
    }


@pytest.fixture
def sample_action_item_data() -> dict:
    """Sample action item data for testing."""
    return {
        "text": "Test action item for unit testing.",
        "note_id": None,
    }


@pytest.fixture
def sample_extract_request_data() -> dict:
    """Sample extract request data for testing."""
    return {
        "text": "Meeting notes: Need to fix bug and update documentation.",
        "save_note": False,
    }
