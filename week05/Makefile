.PHONY: run test format lint seed

run:
	uv run uvicorn backend.app.main:app --reload --host $${HOST:-127.0.0.1} --port $${PORT:-8000}

test:
	PYTHONPATH=. uv run pytest -q backend/tests

format:
	uv tool run black .
	uv tool run ruff check . --fix

lint:
	uv tool run ruff check .

seed:
	uv run -c "from backend.app.db import apply_seed_if_needed; apply_seed_if_needed()"
