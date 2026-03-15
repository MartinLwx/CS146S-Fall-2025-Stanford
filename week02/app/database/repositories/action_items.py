from __future__ import annotations

import sqlite3
from typing import List, Optional

from app.database.connection import get_database_connection
from app.schemas.action_items import ActionItemCreate, ActionItemUpdate


class ActionItemRepository:
    """Repository for action item data access operations."""

    def __init__(self, connection=None):
        self.connection = connection or get_database_connection()

    def create(self, action_item: ActionItemCreate) -> int:
        """Create a new action item and return its ID."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                (action_item.note_id, action_item.text),
            )
            return int(cursor.lastrowid)

    def create_many(self, action_items: List[ActionItemCreate]) -> List[int]:
        """Create multiple action items and return their IDs."""
        ids = []
        with self.connection.cursor() as cursor:
            for action_item in action_items:
                cursor.execute(
                    "INSERT INTO action_items (note_id, text) VALUES (?, ?)",
                    (action_item.note_id, action_item.text),
                )
                ids.append(int(cursor.lastrowid))
        return ids

    def get_by_id(self, action_item_id: int) -> Optional[sqlite3.Row]:
        """Get an action item by its ID."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, note_id, text, done, created_at 
                FROM action_items WHERE id = ?
                """,
                (action_item_id,),
            )
            return cursor.fetchone()

    def get_all(
        self,
        note_id: Optional[int] = None,
        done: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[sqlite3.Row]:
        """Get all action items, optionally filtered by note_id and done status."""
        query = """
            SELECT id, note_id, text, done, created_at 
            FROM action_items 
            WHERE 1=1
        """
        params = []

        if note_id is not None:
            query += " AND note_id = ?"
            params.append(note_id)

        if done is not None:
            query += " AND done = ?"
            params.append(1 if done else 0)

        query += " ORDER BY id DESC"

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)

        if offset is not None and limit is not None:
            query += " OFFSET ?"
            params.append(offset)

        with self.connection.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return list(cursor.fetchall())

    def update(self, action_item_id: int, action_item: ActionItemUpdate) -> bool:
        """Update an action item and return whether it was updated."""
        updates = []
        params = []

        if action_item.text is not None:
            updates.append("text = ?")
            params.append(action_item.text)

        if action_item.done is not None:
            updates.append("done = ?")
            params.append(1 if action_item.done else 0)

        if not updates:
            return False

        params.append(action_item_id)
        set_clause = ", ".join(updates)
        query = f"UPDATE action_items SET {set_clause} WHERE id = ?"

        with self.connection.cursor() as cursor:
            cursor.execute(query, tuple(params))
            return cursor.rowcount > 0

    def mark_done(self, action_item_id: int, done: bool) -> bool:
        """Mark an action item as done or not done."""
        with self.connection.cursor() as cursor:
            cursor.execute(
                "UPDATE action_items SET done = ? WHERE id = ?", (1 if done else 0, action_item_id)
            )
            return cursor.rowcount > 0

    def delete(self, action_item_id: int) -> bool:
        """Delete an action item and return whether it was deleted."""
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM action_items WHERE id = ?", (action_item_id,))
            return cursor.rowcount > 0

    def delete_by_note_id(self, note_id: int) -> int:
        """Delete all action items for a note and return the count deleted."""
        with self.connection.cursor() as cursor:
            cursor.execute("DELETE FROM action_items WHERE note_id = ?", (note_id,))
            return cursor.rowcount

    def exists(self, action_item_id: int) -> bool:
        """Check if an action item exists."""
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT 1 FROM action_items WHERE id = ?", (action_item_id,))
            return cursor.fetchone() is not None

    def count(self, note_id: Optional[int] = None, done: Optional[bool] = None) -> int:
        """Count action items, optionally filtered by note_id and done status."""
        query = "SELECT COUNT(*) as count FROM action_items WHERE 1=1"
        params = []

        if note_id is not None:
            query += " AND note_id = ?"
            params.append(note_id)

        if done is not None:
            query += " AND done = ?"
            params.append(1 if done else 0)

        with self.connection.cursor() as cursor:
            cursor.execute(query, tuple(params))
            result = cursor.fetchone()
            return result["count"] if result else 0

    def get_pending(self, limit: Optional[int] = None) -> List[sqlite3.Row]:
        """Get pending (not done) action items."""
        return self.get_all(done=False, limit=limit)

    def get_completed(self, limit: Optional[int] = None) -> List[sqlite3.Row]:
        """Get completed action items."""
        return self.get_all(done=True, limit=limit)

    def get_by_note_id(self, note_id: int) -> List[sqlite3.Row]:
        """Get all action items for a specific note."""
        return self.get_all(note_id=note_id)

    def search(self, query: str, limit: Optional[int] = None) -> List[sqlite3.Row]:
        """Search action items by text."""
        search_query = f"%{query}%"
        sql = """
            SELECT id, note_id, text, done, created_at 
            FROM action_items 
            WHERE text LIKE ? 
            ORDER BY id DESC
        """
        params = [search_query]

        if limit is not None:
            sql += " LIMIT ?"
            params.append(limit)

        with self.connection.cursor() as cursor:
            cursor.execute(sql, tuple(params))
            return list(cursor.fetchall())
