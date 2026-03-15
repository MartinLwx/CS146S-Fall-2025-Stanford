from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.schemas.notes import NoteCreate, NoteResponse, NoteUpdate, NoteListResponse
from app.services import NoteService
from app.services.exceptions import AppException, NoteNotFoundException


router = APIRouter(prefix="/notes", tags=["notes"])


def get_note_service() -> NoteService:
    """Dependency injection for NoteService."""
    return NoteService()


@router.post(
    "",
    response_model=NoteResponse,
    summary="Create a new note",
    description="Create a new note with the provided content.",
    responses={
        400: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
def create_note(
    note_create: NoteCreate,
    note_service: NoteService = Depends(get_note_service),
) -> NoteResponse:
    """Create a new note.

    - **content**: The content of the note (required)
    """
    return note_service.create_note(note_create)


@router.get(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Get a note by ID",
    description="Retrieve a specific note by its ID.",
    responses={
        404: {"description": "Note not found"},
        500: {"description": "Internal server error"},
    },
)
def get_note(
    note_id: int,
    note_service: NoteService = Depends(get_note_service),
) -> NoteResponse:
    """Get a note by ID.

    - **note_id**: The ID of the note to retrieve (required)
    """
    return note_service.get_note(note_id)


@router.get(
    "",
    response_model=NoteListResponse,
    summary="List all notes",
    description="Retrieve all notes with optional pagination.",
    responses={
        500: {"description": "Internal server error"},
    },
)
def list_notes(
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Maximum number of notes to return",
    ),
    offset: Optional[int] = Query(
        None,
        ge=0,
        description="Number of notes to skip",
    ),
    note_service: NoteService = Depends(get_note_service),
) -> NoteListResponse:
    """List all notes with pagination.

    - **limit**: Maximum number of notes to return (optional)
    - **offset**: Number of notes to skip (optional)
    """
    return note_service.get_all_notes(limit=limit, offset=offset)


@router.put(
    "/{note_id}",
    response_model=NoteResponse,
    summary="Update a note",
    description="Update an existing note with new content.",
    responses={
        404: {"description": "Note not found"},
        400: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
def update_note(
    note_id: int,
    note_update: NoteUpdate,
    note_service: NoteService = Depends(get_note_service),
) -> NoteResponse:
    """Update a note.

    - **note_id**: The ID of the note to update (required)
    - **content**: The updated content of the note (optional)
    """
    return note_service.update_note(note_id, note_update)


@router.delete(
    "/{note_id}",
    status_code=204,
    response_model=None,
    summary="Delete a note",
    description="Delete a note by its ID.",
    responses={
        404: {"description": "Note not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_note(
    note_id: int,
    note_service: NoteService = Depends(get_note_service),
) -> None:
    """Delete a note.

    - **note_id**: The ID of the note to delete (required)
    """
    note_service.delete_note(note_id)
