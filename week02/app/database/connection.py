from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Optional

from app.config import settings


class DatabaseConnection:
    """Manages SQLite database connections with thread-local storage."""

    _local = threading.local()

    def __init__(self, database_path: Optional[Path] = None):
        self.database_path = database_path or settings.database.path
        self._ensure_data_directory_exists()

    def _ensure_data_directory_exists(self) -> None:
        """Ensure the data directory exists."""
        if self.database_path != Path(":memory:"):
            self.database_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection (thread-local)."""
        if not hasattr(self._local, "connection") or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                str(self.database_path),
                timeout=settings.database.timeout,
                check_same_thread=settings.database.check_same_thread,
            )
            self._local.connection.row_factory = sqlite3.Row
        return self._local.connection

    def close_connection(self) -> None:
        """Close the current thread's database connection."""
        if hasattr(self._local, "connection") and self._local.connection is not None:
            self._local.connection.close()
            self._local.connection = None

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database transactions."""
        connection = self.get_connection()
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            self.close_connection()

    @contextmanager
    def cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager for database cursor."""
        with self.transaction() as connection:
            cursor = connection.cursor()
            try:
                yield cursor
            finally:
                cursor.close()

    def execute(self, query: str, parameters: tuple = ()) -> sqlite3.Cursor:
        """Execute a query and return the cursor."""
        with self.cursor() as cursor:
            cursor.execute(query, parameters)
            return cursor

    def initialize_database(self) -> None:
        """Initialize the database with required tables."""
        with self.transaction() as connection:
            cursor = connection.cursor()

            # Create notes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT (datetime('now'))
                )
            """)

            # Create action_items table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS action_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    note_id INTEGER,
                    text TEXT NOT NULL,
                    done INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT (datetime('now')),
                    FOREIGN KEY (note_id) REFERENCES notes(id)
                )
            """)

            # Create indexes for better performance
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_action_items_note_id ON action_items(note_id)"
            )
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_action_items_done ON action_items(done)")

            connection.commit()

    def drop_all_tables(self) -> None:
        """Drop all tables (for testing purposes)."""
        with self.transaction() as connection:
            cursor = connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS action_items")
            cursor.execute("DROP TABLE IF EXISTS notes")
            connection.commit()


# Global database connection instance
_db_connection: Optional[DatabaseConnection] = None


def get_database_connection() -> DatabaseConnection:
    """Get the global database connection instance."""
    global _db_connection
    if _db_connection is None:
        _db_connection = DatabaseConnection()
    return _db_connection


def initialize_database() -> None:
    """Initialize the database (call this at application startup)."""
    connection = get_database_connection()
    connection.initialize_database()


def close_all_connections() -> None:
    """Close all database connections (call this at application shutdown)."""
    global _db_connection
    if _db_connection is not None:
        _db_connection.close_connection()
        _db_connection = None


# Alias for backward compatibility
get_connection = get_database_connection
