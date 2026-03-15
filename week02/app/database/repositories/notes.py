from __future__ import annotations

import sqlite3
from datetime import datetime
from typing import List, Optional

from app.database.connection import get_database_connection
from app.schemas.notes import NoteCreate, NoteUpdate


class NoteRepository:
    """Repository for note data access operations."""

    def __init__(self, connection=None):
        self.connection = connection or get_database_connection()

    def create(self, note: NoteCreate) -> int:
        """Create a new note and return its ID."""
        with self.connection.cursor() as cursor:
            cursor.execute("INSERT INTO notes (content) VALUES (?)", (note.content,))
            return int(cursor.lastrowid)

    def get_by_id(self, note_id: int) -> Optional[sqlite3.Row]:
        """Get a note by its ID."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT id, content, created_at FROM notes WHERE id = ?", (note_id,))
            return cursor.fetchone()

    def get_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[sqlite3.Row]:
        """Get all notes, optionally paginated."""
        query = "SELECT id, content, created_at FROM notes ORDER BY id DESC"
        params = []

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        if offset is not None and limit is not None:
            query += " OFFSET ?"
            params.append(offset)

        with self.connection.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return list(cursor.fetchall())

    def update(self, note_id: int, note: NoteUpdate) -> bool:
        """Update a note and return whether it was updated."""
        if note.content is None:
            return False

        with self.connection.cursor() as cursor:
            cursor.execute("UPDATE notes SET content = ? WHERE id = ?", (note.content, note_id))
            return cursor.rowcount > 0

    def delete(self, note_id: int) -> bool:
        """Delete a note and return whether it was deleted."""
        with self.connection.cursor() as cursor:
            # First, delete associated action items to maintain referential integrity
            cursor.execute("DELETE FROM action_items WHERE note_id = ?", (note_id,))
            # Then delete the note
            cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
            return cursor.rowcount > 0

    def exists(self, note_id: int) -> bool:
        """Check if a note exists."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM notes WHERE id = ?", (note_id,))
            return cursor.fetchone() is not None

    def count(self) -> int:
        """Count total number of notes."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM notes")
            result = cursor.fetchone()
            return result["count"] if result else 0

    def search(self, query: str, limit: Optional[int] = None) -> List[sqlite3.Row]:
        """Search notes by content."""
        search_query = f"%{query}%"
        sql = "SELECT id, content, created_at FROM notes WHERE content LIKE ? ORDER BY id DESC"
        params = [search_query]

        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)

        with self.connection.cursor() as cursor:
            cursor.execute(sql, tuple(params))
            return list(cursor.fetchall())

    def get_recent(self, days: int = 7) -> List[sqlite3.Row]:
        """Get notes created within the last N days."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, content, created_at FROM notes 
                WHERE date(created_at) >= date('now', ?) 
                ORDER BY id DESC
                """,
                (f"-{days} days",),
            )
            return list(cursor.fetchall())
