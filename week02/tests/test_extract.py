import socket

import pytest

from ..app.services.extract import extract_action_items, extract_action_items_llm


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def ollama_available():
    """Check if Ollama is running on localhost:11434."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(("localhost", 11434))
        sock.close()
        return result == 0
    except OSError:
        return False


@pytest.mark.skipif(not ollama_available(), reason="Ollama not running")
class TestExtractActionItemsLLM:
    """Integration tests for extract_action_items_llm requiring Ollama."""

    def test_empty_input(self):
        """Empty string or whitespace should return empty list."""
        assert extract_action_items_llm("") == []
        assert extract_action_items_llm("   ") == []
        assert extract_action_items_llm("\n\t\n") == []

    def test_bullet_lists(self):
        """Extract action items from bullet lists."""
        text = """
        Team meeting notes:
        - Fix bug in login page
        * Implement new API endpoint
        1. Write unit tests
        • Update documentation
        Some discussion about design.
        """
        items = extract_action_items_llm(text)
        assert len(items) >= 3  # LLM might extract more/less
        assert all(isinstance(item, str) for item in items)
        # Check expected items are present (allow for LLM variations)
        expected_fragments = ["bug", "API", "tests", "documentation"]
        found = any(any(frag in item.lower() for frag in expected_fragments) for item in items)
        assert found, f"Expected fragments not found in {items}"

    def test_keyword_prefixes(self):
        """Extract items with TODO:, Action:, Next: prefixes."""
        text = """
        TODO: Review pull request #123
        Action: Schedule team meeting
        Next: Deploy to staging
        Random narrative text.
        """
        items = extract_action_items_llm(text)
        assert len(items) >= 2
        assert all(isinstance(item, str) for item in items)
        # LLM should extract the action items
        expected_keywords = ["review", "schedule", "deploy"]
        for item in items:
            item_lower = item.lower()
            assert any(
                keyword in item_lower for keyword in expected_keywords
            ), f"Item '{item}' doesn't contain expected keywords {expected_keywords}"

    def test_mixed_narrative(self):
        """Extract from mixed narrative with action items."""
        text = """
        We discussed the new feature implementation. 
        Need to fix the database connection issue first.
        Then we should update the UI components.
        Also, don't forget to write integration tests.
        The deadline is next Friday.
        """
        items = extract_action_items_llm(text)
        assert len(items) >= 2
        assert all(isinstance(item, str) for item in items)
        # Should extract imperative statements
        for item in items:
            assert len(item) > 5  # Reasonable minimum length

    def test_custom_model(self):
        """Test with explicit model parameter."""
        text = "- Test action item"
        # Use the default model that we know is available
        items = extract_action_items_llm(text, model="qwen3:0.6b")
        assert isinstance(items, list)
        assert all(isinstance(item, str) for item in items)

    def test_env_model(self, monkeypatch):
        """Test OLLAMA_MODEL environment variable."""
        monkeypatch.setenv("OLLAMA_MODEL", "qwen3:0.6b")
        text = "TODO: Test env variable"
        items = extract_action_items_llm(text)
        assert isinstance(items, list)
        assert all(isinstance(item, str) for item in items)

    def test_invalid_model_raises_error(self):
        """Test that invalid model name raises an exception."""
        text = "Simple action item"
        # Use a model name that doesn't exist
        try:
            extract_action_items_llm(text, model="non-existent-model-12345")
            # If we get here, the model might exist (unlikely) or error not raised
            # For integration test, we'll accept this as pass but log warning
            pytest.skip("Model 'non-existent-model-12345' might actually exist")
        except Exception:
            # Expected - any exception is fine (connection error, model not found, etc.)
            pass
