from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="The content of the note",
        examples=["Meeting notes: Need to fix login bug and update documentation."],
    )


class NoteCreate(NoteBase):
    """Schema for creating a new note."""


class NoteUpdate(BaseModel):
    """Schema for updating an existing note."""

    content: Optional[str] = Field(
        None,
        min_length=1,
        max_length=10000,
        description="Updated content of the note",
        examples=["Updated meeting notes: Login bug fixed, documentation pending."],
    )


class NoteResponse(NoteBase):
    """Schema for note response."""

    id: int = Field(
        ...,
        description="Unique identifier of the note",
        examples=[1],
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the note was created",
        examples=["2024-01-15T10:30:00Z"],
    )

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    """Schema for list of notes response."""

    notes: list[NoteResponse] = Field(
        ...,
        description="List of notes",
    )
    count: int = Field(
        ...,
        description="Total number of notes",
        examples=[5],
    )
