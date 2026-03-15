from __future__ import annotations

from typing import List, Optional

from app.database.repositories.action_items import ActionItemRepository
from app.database.repositories.notes import NoteRepository
from app.schemas.action_items import (
    ActionItemCreate,
    ActionItemResponse,
    ActionItemUpdate,
    ActionItemListResponse,
    ExtractRequest,
    ExtractResponse,
    MarkDoneRequest,
)
from app.schemas.notes import NoteCreate
from app.services.exceptions import (
    ActionItemNotFoundException,
    NoteNotFoundException,
    ValidationException,
    ExtractionException,
)
from app.services.extract import extract_action_items, extract_action_items_llm


class ActionItemService:
    """Service for action item business logic."""

    def __init__(
        self,
        action_item_repository: Optional[ActionItemRepository] = None,
        note_repository: Optional[NoteRepository] = None,
    ):
        self.action_item_repository = action_item_repository or ActionItemRepository()
        self.note_repository = note_repository or NoteRepository()

    def create_action_item(self, action_item_create: ActionItemCreate) -> ActionItemResponse:
        """Create a new action item."""
        # Validate note_id if provided
        if action_item_create.note_id is not None:
            if not self.note_repository.exists(action_item_create.note_id):
                raise NoteNotFoundException(action_item_create.note_id)

        # Validate content
        if not action_item_create.text.strip():
            raise ValidationException(
                message="Action item text cannot be empty", details={"field": "text"}
            )

        action_item_id = self.action_item_repository.create(action_item_create)
        action_item = self.action_item_repository.get_by_id(action_item_id)

        if action_item is None:
            raise ActionItemNotFoundException(action_item_id)

        return ActionItemResponse(
            id=action_item["id"],
            note_id=action_item["note_id"],
            text=action_item["text"],
            done=bool(action_item["done"]),
            created_at=action_item["created_at"],
        )

    def get_action_item(self, action_item_id: int) -> ActionItemResponse:
        """Get an action item by ID."""
        action_item = self.action_item_repository.get_by_id(action_item_id)

        if action_item is None:
            raise ActionItemNotFoundException(action_item_id)

        return ActionItemResponse(
            id=action_item["id"],
            note_id=action_item["note_id"],
            text=action_item["text"],
            done=bool(action_item["done"]),
            created_at=action_item["created_at"],
        )

    def get_all_action_items(
        self,
        note_id: Optional[int] = None,
        done: Optional[bool] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> ActionItemListResponse:
        """Get all action items with optional filtering."""
        # Validate note_id if provided
        if note_id is not None and not self.note_repository.exists(note_id):
            raise NoteNotFoundException(note_id)

        action_items_data = self.action_item_repository.get_all(
            note_id=note_id, done=done, limit=limit, offset=offset
        )

        total_count = self.action_item_repository.count(note_id=note_id, done=done)

        action_items = [
            ActionItemResponse(
                id=item["id"],
                note_id=item["note_id"],
                text=item["text"],
                done=bool(item["done"]),
                created_at=item["created_at"],
            )
            for item in action_items_data
        ]

        return ActionItemListResponse(
            action_items=action_items,
            count=total_count,
        )

    def update_action_item(
        self, action_item_id: int, action_item_update: ActionItemUpdate
    ) -> ActionItemResponse:
        """Update an action item."""
        # Check if action item exists
        if not self.action_item_repository.exists(action_item_id):
            raise ActionItemNotFoundException(action_item_id)

        # Validate update data
        if action_item_update.text is not None and not action_item_update.text.strip():
            raise ValidationException(
                message="Action item text cannot be empty", details={"field": "text"}
            )

        # Perform update
        updated = self.action_item_repository.update(action_item_id, action_item_update)

        if not updated:
            # No changes were made (both text and done were None)
            pass

        # Return updated action item
        return self.get_action_item(action_item_id)

    def mark_done(
        self, action_item_id: int, mark_done_request: MarkDoneRequest
    ) -> ActionItemResponse:
        """Mark an action item as done or not done."""
        # Check if action item exists
        if not self.action_item_repository.exists(action_item_id):
            raise ActionItemNotFoundException(action_item_id)

        updated = self.action_item_repository.mark_done(action_item_id, mark_done_request.done)

        if not updated:
            # This shouldn't happen since we checked existence, but handle it
            raise ActionItemNotFoundException(action_item_id)

        return self.get_action_item(action_item_id)

    def delete_action_item(self, action_item_id: int) -> None:
        """Delete an action item."""
        # Check if action item exists
        if not self.action_item_repository.exists(action_item_id):
            raise ActionItemNotFoundException(action_item_id)

        deleted = self.action_item_repository.delete(action_item_id)

        if not deleted:
            # This shouldn't happen since we checked existence, but handle it
            raise ActionItemNotFoundException(action_item_id)

    def extract_action_items(
        self, extract_request: ExtractRequest, use_llm: bool = False
    ) -> ExtractResponse:
        """Extract action items from text."""
        # Validate input text
        if not extract_request.text.strip():
            raise ValidationException(message="Text cannot be empty", details={"field": "text"})

        # Extract action items using appropriate method
        try:
            if use_llm:
                extracted_texts = extract_action_items_llm(extract_request.text)
            else:
                extracted_texts = extract_action_items(extract_request.text)
        except Exception as e:
            raise ExtractionException(
                message=f"Failed to extract action items: {str(e)}", details={"error": str(e)}
            )

        note_id = None
        if extract_request.save_note:
            # Save the input text as a note
            note_create = NoteCreate(content=extract_request.text)
            note_id = self.note_repository.create(note_create)

        # Create action items from extracted texts
        action_items = []
        for text in extracted_texts:
            action_item_create = ActionItemCreate(text=text, note_id=note_id)
            action_item_id = self.action_item_repository.create(action_item_create)
            action_item = self.action_item_repository.get_by_id(action_item_id)

            if action_item:
                action_items.append(
                    ActionItemResponse(
                        id=action_item["id"],
                        note_id=action_item["note_id"],
                        text=action_item["text"],
                        done=bool(action_item["done"]),
                        created_at=action_item["created_at"],
                    )
                )

        return ExtractResponse(
            note_id=note_id,
            items=action_items,
        )

    def get_pending_action_items(self, limit: Optional[int] = None) -> ActionItemListResponse:
        """Get pending (not done) action items."""
        action_items_data = self.action_item_repository.get_pending(limit=limit)
        count = len(action_items_data)

        action_items = [
            ActionItemResponse(
                id=item["id"],
                note_id=item["note_id"],
                text=item["text"],
                done=bool(item["done"]),
                created_at=item["created_at"],
            )
            for item in action_items_data
        ]

        return ActionItemListResponse(
            action_items=action_items,
            count=count,
        )

    def get_completed_action_items(self, limit: Optional[int] = None) -> ActionItemListResponse:
        """Get completed action items."""
        action_items_data = self.action_item_repository.get_completed(limit=limit)
        count = len(action_items_data)

        action_items = [
            ActionItemResponse(
                id=item["id"],
                note_id=item["note_id"],
                text=item["text"],
                done=bool(item["done"]),
                created_at=item["created_at"],
            )
            for item in action_items_data
        ]

        return ActionItemListResponse(
            action_items=action_items,
            count=count,
        )

    def search_action_items(
        self, query: str, limit: Optional[int] = None
    ) -> ActionItemListResponse:
        """Search action items by text."""
        if not query.strip():
            raise ValidationException(
                message="Search query cannot be empty", details={"field": "query"}
            )

        action_items_data = self.action_item_repository.search(query, limit=limit)
        count = len(action_items_data)

        action_items = [
            ActionItemResponse(
                id=item["id"],
                note_id=item["note_id"],
                text=item["text"],
                done=bool(item["done"]),
                created_at=item["created_at"],
            )
            for item in action_items_data
        ]

        return ActionItemListResponse(
            action_items=action_items,
            count=count,
        )
