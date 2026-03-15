from __future__ import annotations

import pytest

from app.schemas.notes import NoteCreate, NoteUpdate
from app.schemas.action_items import ActionItemCreate, ActionItemUpdate


class TestNoteRepository:
    """Test NoteRepository."""

    def test_create_note(self, note_repository):
        """Test creating a note."""
        note_create = NoteCreate(content="Test note content")
        note_id = note_repository.create(note_create)

        assert note_id > 0

        # Retrieve the note
        note = note_repository.get_by_id(note_id)
        assert note is not None
        assert note["id"] == note_id
        assert note["content"] == note_create.content

    def test_get_by_id_not_found(self, note_repository):
        """Test getting a non-existent note."""
        note = note_repository.get_by_id(99999)
        assert note is None

    def test_get_all_notes(self, note_repository):
        """Test getting all notes."""
        # Create multiple notes
        note_ids = []
        for i in range(3):
            note_create = NoteCreate(content=f"Test note {i}")
            note_id = note_repository.create(note_create)
            note_ids.append(note_id)

        # Get all notes
        notes = note_repository.get_all()
        assert len(notes) >= 3

        # Check that our notes are in the results
        retrieved_ids = {note["id"] for note in notes}
        for note_id in note_ids:
            assert note_id in retrieved_ids

    def test_get_all_notes_with_pagination(self, note_repository):
        """Test getting notes with pagination."""
        # Create multiple notes
        for i in range(5):
            note_create = NoteCreate(content=f"Test note {i}")
            note_repository.create(note_create)

        # Get with limit
        notes = note_repository.get_all(limit=2)
        assert len(notes) == 2

        # Get with limit and offset
        notes = note_repository.get_all(limit=2, offset=2)
        assert len(notes) == 2

    def test_update_note(self, note_repository):
        """Test updating a note."""
        # Create a note
        note_create = NoteCreate(content="Original content")
        note_id = note_repository.create(note_create)

        # Update the note
        note_update = NoteUpdate(content="Updated content")
        updated = note_repository.update(note_id, note_update)

        assert updated is True

        # Retrieve and verify
        note = note_repository.get_by_id(note_id)
        assert note["content"] == "Updated content"

    def test_update_note_no_changes(self, note_repository):
        """Test updating a note with no changes."""
        # Create a note
        note_create = NoteCreate(content="Original content")
        note_id = note_repository.create(note_create)

        # Update with None content (no changes)
        note_update = NoteUpdate(content=None)
        updated = note_repository.update(note_id, note_update)

        assert updated is False

    def test_delete_note(self, note_repository):
        """Test deleting a note."""
        # Create a note
        note_create = NoteCreate(content="Test note to delete")
        note_id = note_repository.create(note_create)

        # Delete the note
        deleted = note_repository.delete(note_id)

        assert deleted is True

        # Verify note is deleted
        note = note_repository.get_by_id(note_id)
        assert note is None

    def test_exists_note(self, note_repository):
        """Test checking if a note exists."""
        # Create a note
        note_create = NoteCreate(content="Test note")
        note_id = note_repository.create(note_create)

        assert note_repository.exists(note_id) is True
        assert note_repository.exists(99999) is False

    def test_count_notes(self, note_repository):
        """Test counting notes."""
        initial_count = note_repository.count()

        # Create a note
        note_create = NoteCreate(content="Test note")
        note_repository.create(note_create)

        new_count = note_repository.count()
        assert new_count == initial_count + 1

    def test_search_notes(self, note_repository):
        """Test searching notes."""
        # Create notes with specific content
        note_repository.create(NoteCreate(content="Meeting about project Alpha"))
        note_repository.create(NoteCreate(content="Project Beta status update"))
        note_repository.create(NoteCreate(content="Alpha team meeting notes"))

        # Search for "alpha"
        results = note_repository.search("alpha")
        assert len(results) == 2

        # Search for "beta"
        results = note_repository.search("beta")
        assert len(results) == 1

        # Search with limit
        results = note_repository.search("meeting", limit=1)
        assert len(results) == 1

    def test_get_recent_notes(self, note_repository):
        """Test getting recent notes."""
        # Create a note
        note_create = NoteCreate(content="Recent note")
        note_repository.create(note_create)

        # Get recent notes (last 7 days)
        recent = note_repository.get_recent(days=7)
        assert len(recent) >= 1


class TestActionItemRepository:
    """Test ActionItemRepository."""

    def test_create_action_item(self, action_item_repository):
        """Test creating an action item."""
        action_item_create = ActionItemCreate(text="Test action item")
        action_item_id = action_item_repository.create(action_item_create)

        assert action_item_id > 0

        # Retrieve the action item
        action_item = action_item_repository.get_by_id(action_item_id)
        assert action_item is not None
        assert action_item["id"] == action_item_id
        assert action_item["text"] == action_item_create.text
        assert action_item["done"] == 0  # Default is False (0 in SQLite)

    def test_create_action_item_with_note_id(self, action_item_repository, note_repository):
        """Test creating an action item with note_id."""
        # Create a note first
        note_create = NoteCreate(content="Test note")
        note_id = note_repository.create(note_create)

        # Create action item with note_id
        action_item_create = ActionItemCreate(text="Test action item", note_id=note_id)
        action_item_id = action_item_repository.create(action_item_create)

        action_item = action_item_repository.get_by_id(action_item_id)
        assert action_item["note_id"] == note_id

    def test_create_many_action_items(self, action_item_repository):
        """Test creating multiple action items."""
        action_items = [ActionItemCreate(text=f"Action item {i}") for i in range(3)]

        ids = action_item_repository.create_many(action_items)
        assert len(ids) == 3

        for action_item_id in ids:
            action_item = action_item_repository.get_by_id(action_item_id)
            assert action_item is not None

    def test_get_all_action_items(self, action_item_repository):
        """Test getting all action items."""
        # Create multiple action items
        for i in range(3):
            action_item_create = ActionItemCreate(text=f"Action item {i}")
            action_item_repository.create(action_item_create)

        action_items = action_item_repository.get_all()
        assert len(action_items) >= 3

    def test_get_all_with_filters(self, action_item_repository, note_repository):
        """Test getting action items with filters."""
        # Create a note
        note_create = NoteCreate(content="Test note")
        note_id = note_repository.create(note_create)

        # Create action items with different statuses and note_id
        action_item_repository.create(ActionItemCreate(text="Pending 1", note_id=note_id))
        action_item_repository.create(ActionItemCreate(text="Pending 2", note_id=note_id))
        completed_id = action_item_repository.create(
            ActionItemCreate(text="Completed", note_id=note_id)
        )
        action_item_repository.mark_done(completed_id, True)

        # Filter by note_id
        action_items = action_item_repository.get_all(note_id=note_id)
        assert len(action_items) == 3

        # Filter by done=False
        action_items = action_item_repository.get_all(done=False)
        assert len(action_items) >= 2

        # Filter by done=True
        action_items = action_item_repository.get_all(done=True)
        assert len(action_items) >= 1

        # Filter by both note_id and done
        action_items = action_item_repository.get_all(note_id=note_id, done=False)
        assert len(action_items) == 2

    def test_update_action_item(self, action_item_repository):
        """Test updating an action item."""
        # Create an action item
        action_item_create = ActionItemCreate(text="Original text")
        action_item_id = action_item_repository.create(action_item_create)

        # Update text and done status
        action_item_update = ActionItemUpdate(text="Updated text", done=True)
        updated = action_item_repository.update(action_item_id, action_item_update)

        assert updated is True

        # Retrieve and verify
        action_item = action_item_repository.get_by_id(action_item_id)
        assert action_item["text"] == "Updated text"
        assert action_item["done"] == 1

    def test_mark_done(self, action_item_repository):
        """Test marking an action item as done/not done."""
        # Create an action item
        action_item_create = ActionItemCreate(text="Test action item")
        action_item_id = action_item_repository.create(action_item_create)

        # Mark as done
        updated = action_item_repository.mark_done(action_item_id, True)
        assert updated is True

        action_item = action_item_repository.get_by_id(action_item_id)
        assert action_item["done"] == 1

        # Mark as not done
        updated = action_item_repository.mark_done(action_item_id, False)
        assert updated is True

        action_item = action_item_repository.get_by_id(action_item_id)
        assert action_item["done"] == 0

    def test_delete_action_item(self, action_item_repository):
        """Test deleting an action item."""
        # Create an action item
        action_item_create = ActionItemCreate(text="Test action item")
        action_item_id = action_item_repository.create(action_item_create)

        # Delete the action item
        deleted = action_item_repository.delete(action_item_id)

        assert deleted is True

        # Verify action item is deleted
        action_item = action_item_repository.get_by_id(action_item_id)
        assert action_item is None

    def test_delete_by_note_id(self, action_item_repository, note_repository):
        """Test deleting action items by note_id."""
        # Create a note
        note_create = NoteCreate(content="Test note")
        note_id = note_repository.create(note_create)

        # Create action items for the note
        for i in range(3):
            action_item_create = ActionItemCreate(text=f"Action item {i}", note_id=note_id)
            action_item_repository.create(action_item_create)

        # Delete all action items for the note
        deleted_count = action_item_repository.delete_by_note_id(note_id)
        assert deleted_count == 3

        # Verify no action items left for this note
        action_items = action_item_repository.get_all(note_id=note_id)
        assert len(action_items) == 0

    def test_count_action_items(self, action_item_repository):
        """Test counting action items."""
        initial_count = action_item_repository.count()

        # Create an action item
        action_item_create = ActionItemCreate(text="Test action item")
        action_item_repository.create(action_item_create)

        new_count = action_item_repository.count()
        assert new_count == initial_count + 1

    def test_get_pending_action_items(self, action_item_repository):
        """Test getting pending action items."""
        # Create pending and completed action items
        pending_id = action_item_repository.create(ActionItemCreate(text="Pending"))
        completed_id = action_item_repository.create(ActionItemCreate(text="Completed"))
        action_item_repository.mark_done(completed_id, True)

        pending_items = action_item_repository.get_pending()
        assert len(pending_items) >= 1

        # Verify the pending item is in the results
        pending_ids = {item["id"] for item in pending_items}
        assert pending_id in pending_ids
        assert completed_id not in pending_ids

    def test_search_action_items(self, action_item_repository):
        """Test searching action items."""
        # Create action items with specific text
        action_item_repository.create(ActionItemCreate(text="Fix login bug"))
        action_item_repository.create(ActionItemCreate(text="Update documentation"))
        action_item_repository.create(ActionItemCreate(text="Bug report for login issue"))

        # Search for "login"
        results = action_item_repository.search("login")
        assert len(results) == 2

        # Search for "documentation"
        results = action_item_repository.search("documentation")
        assert len(results) == 1
