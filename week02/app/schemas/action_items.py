from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ActionItemBase(BaseModel):
    text: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="The action item text",
        examples=["Fix login bug", "Update documentation"],
    )
    note_id: Optional[int] = Field(
        None,
        description="ID of the associated note, if any",
        examples=[1],
    )


class ActionItemCreate(ActionItemBase):
    """Schema for creating a new action item."""


class ActionItemUpdate(BaseModel):
    """Schema for updating an existing action item."""

    text: Optional[str] = Field(
        None,
        min_length=1,
        max_length=1000,
        description="Updated action item text",
        examples=["Fixed login bug"],
    )
    done: Optional[bool] = Field(
        None,
        description="Whether the action item is completed",
        examples=[True],
    )


class ActionItemResponse(ActionItemBase):
    """Schema for action item response."""

    id: int = Field(
        ...,
        description="Unique identifier of the action item",
        examples=[1],
    )
    done: bool = Field(
        ...,
        description="Whether the action item is completed",
        examples=[False],
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the action item was created",
        examples=["2024-01-15T10:30:00Z"],
    )

    class Config:
        from_attributes = True


class ActionItemListResponse(BaseModel):
    """Schema for list of action items response."""

    action_items: list[ActionItemResponse] = Field(
        ...,
        description="List of action items",
    )
    count: int = Field(
        ...,
        description="Total number of action items",
        examples=[5],
    )


class ExtractRequest(BaseModel):
    """Schema for action item extraction request."""

    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text to extract action items from",
        examples=["Meeting notes: Need to fix login bug and update documentation."],
    )
    save_note: bool = Field(
        default=False,
        description="Whether to save the input text as a note",
        examples=[True],
    )


class ExtractResponse(BaseModel):
    """Schema for action item extraction response."""

    note_id: Optional[int] = Field(
        None,
        description="ID of the created note, if save_note was True",
        examples=[1],
    )
    items: list[ActionItemResponse] = Field(
        ...,
        description="Extracted action items",
    )


class MarkDoneRequest(BaseModel):
    """Schema for marking an action item as done/not done."""

    done: bool = Field(
        ...,
        description="Whether the action item is completed",
        examples=[True],
    )
