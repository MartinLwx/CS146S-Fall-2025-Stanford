from __future__ import annotations

import datetime
import pytest
from pydantic import ValidationError

from app.schemas.notes import NoteCreate, NoteResponse, NoteUpdate
from app.schemas.action_items import (
    ActionItemCreate,
    ActionItemResponse,
    ActionItemUpdate,
    ExtractRequest,
    MarkDoneRequest,
)
from app.schemas.errors import ErrorResponse, ValidationErrorResponse


class TestNoteSchemas:
    """Test note-related schemas."""

    def test_note_create_valid(self):
        """Test valid NoteCreate schema."""
        data = {"content": "Test note content"}
        note = NoteCreate(**data)
        assert note.content == data["content"]

    def test_note_create_invalid_empty(self):
        """Test NoteCreate with empty content."""
        with pytest.raises(ValidationError):
            NoteCreate(content="")

    def test_note_create_invalid_too_long(self):
        """Test NoteCreate with content exceeding max length."""
        with pytest.raises(ValidationError):
            NoteCreate(content="x" * 10001)

    def test_note_response_valid(self):
        """Test valid NoteResponse schema."""
        data = {
            "id": 1,
            "content": "Test note content",
            "created_at": "2024-01-15T10:30:00Z",
        }
        note = NoteResponse(**data)
        assert note.id == data["id"]
        assert note.content == data["content"]
        expected_date = datetime.datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        assert note.created_at == expected_date

    def test_note_update_valid(self):
        """Test valid NoteUpdate schema."""
        data = {"content": "Updated content"}
        note = NoteUpdate(**data)
        assert note.content == data["content"]

    def test_note_update_empty(self):
        """Test NoteUpdate with empty content."""
        with pytest.raises(ValidationError):
            NoteUpdate(content="")


class TestActionItemSchemas:
    """Test action item-related schemas."""

    def test_action_item_create_valid(self):
        """Test valid ActionItemCreate schema."""
        data = {"text": "Test action item", "note_id": 1}
        action_item = ActionItemCreate(**data)
        assert action_item.text == data["text"]
        assert action_item.note_id == data["note_id"]

    def test_action_item_create_invalid_empty_text(self):
        """Test ActionItemCreate with empty text."""
        with pytest.raises(ValidationError):
            ActionItemCreate(text="")

    def test_action_item_create_invalid_too_long_text(self):
        """Test ActionItemCreate with text exceeding max length."""
        with pytest.raises(ValidationError):
            ActionItemCreate(text="x" * 1001)

    def test_action_item_response_valid(self):
        """Test valid ActionItemResponse schema."""
        data = {
            "id": 1,
            "note_id": 1,
            "text": "Test action item",
            "done": False,
            "created_at": "2024-01-15T10:30:00Z",
        }
        action_item = ActionItemResponse(**data)
        assert action_item.id == data["id"]
        assert action_item.note_id == data["note_id"]
        assert action_item.text == data["text"]
        assert action_item.done == data["done"]
        expected_date = datetime.datetime.fromisoformat(data["created_at"].replace("Z", "+00:00"))
        assert action_item.created_at == expected_date

    def test_action_item_update_valid(self):
        """Test valid ActionItemUpdate schema."""
        data = {"text": "Updated text", "done": True}
        action_item = ActionItemUpdate(**data)
        assert action_item.text == data["text"]
        assert action_item.done == data["done"]

    def test_action_item_update_partial(self):
        """Test ActionItemUpdate with partial data."""
        data = {"done": True}
        action_item = ActionItemUpdate(**data)
        assert action_item.done == data["done"]
        assert action_item.text is None

    def test_extract_request_valid(self):
        """Test valid ExtractRequest schema."""
        data = {"text": "Test text", "save_note": True}
        request = ExtractRequest(**data)
        assert request.text == data["text"]
        assert request.save_note == data["save_note"]

    def test_extract_request_default_save_note(self):
        """Test ExtractRequest with default save_note."""
        data = {"text": "Test text"}
        request = ExtractRequest(**data)
        assert request.text == data["text"]
        assert request.save_note is False

    def test_mark_done_request_valid(self):
        """Test valid MarkDoneRequest schema."""
        data = {"done": True}
        request = MarkDoneRequest(**data)
        assert request.done == data["done"]


class TestErrorSchemas:
    """Test error response schemas."""

    def test_error_response_valid(self):
        """Test valid ErrorResponse schema."""
        data = {
            "error_code": "NOTE_NOT_FOUND",
            "message": "Note not found",
            "details": {"note_id": 1},
        }
        error = ErrorResponse(**data)
        assert error.error_code == data["error_code"]
        assert error.message == data["message"]
        assert error.details == data["details"]

    def test_error_response_no_details(self):
        """Test ErrorResponse without details."""
        data = {
            "error_code": "INTERNAL_ERROR",
            "message": "Internal server error",
        }
        error = ErrorResponse(**data)
        assert error.error_code == data["error_code"]
        assert error.message == data["message"]
        assert error.details is None

    def test_validation_error_response_valid(self):
        """Test valid ValidationErrorResponse schema."""
        from app.schemas.errors import ValidationErrorDetail

        details = [
            ValidationErrorDetail(
                field="content",
                message="field required",
                type="missing",
            )
        ]

        error = ValidationErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Validation failed",
            details=details,
        )

        assert error.error_code == "VALIDATION_ERROR"
        assert error.message == "Validation failed"
        assert len(error.details) == 1
        assert error.details[0].field == "content"
