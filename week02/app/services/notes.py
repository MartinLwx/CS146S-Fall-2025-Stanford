from __future__ import annotations

from typing import List, Optional

from app.database.repositories.notes import NoteRepository
from app.schemas.notes import NoteCreate, NoteResponse, NoteUpdate, NoteListResponse
from app.services.exceptions import NoteNotFoundException, ValidationException


class NoteService:
    """Service for note business logic."""

    def __init__(self, note_repository: Optional[NoteRepository] = None):
        self.note_repository = note_repository or NoteRepository()

    def create_note(self, note_create: NoteCreate) -> NoteResponse:
        """Create a new note."""
        # Additional validation can be added here
        if not note_create.content.strip():
            raise ValidationException(
                message="Note content cannot be empty", details={"field": "content"}
            )

        note_id = self.note_repository.create(note_create)
        note = self.note_repository.get_by_id(note_id)

        if note is None:
            raise NoteNotFoundException(note_id)

        return NoteResponse(
            id=note["id"],
            content=note["content"],
            created_at=note["created_at"],
        )

    def get_note(self, note_id: int) -> NoteResponse:
        """Get a note by ID."""
        note = self.note_repository.get_by_id(note_id)

        if note is None:
            raise NoteNotFoundException(note_id)

        return NoteResponse(
            id=note["id"],
            content=note["content"],
            created_at=note["created_at"],
        )

    def get_all_notes(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> NoteListResponse:
        """Get all notes with pagination."""
        notes_data = self.note_repository.get_all(limit=limit, offset=offset)
        total_count = self.note_repository.count()

        notes = [
            NoteResponse(
                id=note["id"],
                content=note["content"],
                created_at=note["created_at"],
            )
            for note in notes_data
        ]

        return NoteListResponse(
            notes=notes,
            count=total_count,
        )

    def update_note(self, note_id: int, note_update: NoteUpdate) -> NoteResponse:
        """Update a note."""
        # Check if note exists
        if not self.note_repository.exists(note_id):
            raise NoteNotFoundException(note_id)

        # Validate update data
        if note_update.content is not None and not note_update.content.strip():
            raise ValidationException(
                message="Note content cannot be empty", details={"field": "content"}
            )

        # Perform update
        updated = self.note_repository.update(note_id, note_update)

        if not updated:
            # No changes were made (content was None)
            pass

        # Return updated note
        return self.get_note(note_id)

    def delete_note(self, note_id: int) -> None:
        """Delete a note."""
        # Check if note exists
        if not self.note_repository.exists(note_id):
            raise NoteNotFoundException(note_id)

        deleted = self.note_repository.delete(note_id)

        if not deleted:
            # This shouldn't happen since we checked existence, but handle it
            raise NoteNotFoundException(note_id)

    def search_notes(self, query: str, limit: Optional[int] = None) -> NoteListResponse:
        """Search notes by content."""
        if not query.strip():
            raise ValidationException(
                message="Search query cannot be empty", details={"field": "query"}
            )

        notes_data = self.note_repository.search(query, limit=limit)
        # Note: search doesn't provide total count for performance reasons
        # We'll just return the count of results we found
        count = len(notes_data)

        notes = [
            NoteResponse(
                id=note["id"],
                content=note["content"],
                created_at=note["created_at"],
            )
            for note in notes_data
        ]

        return NoteListResponse(
            notes=notes,
            count=count,
        )

    def get_recent_notes(self, days: int = 7) -> NoteListResponse:
        """Get notes created within the last N days."""
        if days <= 0:
            raise ValidationException(
                message="Days must be positive", details={"field": "days", "value": days}
            )

        notes_data = self.note_repository.get_recent(days)
        count = len(notes_data)

        notes = [
            NoteResponse(
                id=note["id"],
                content=note["content"],
                created_at=note["created_at"],
            )
            for note in notes_data
        ]

        return NoteListResponse(
            notes=notes,
            count=count,
        )
