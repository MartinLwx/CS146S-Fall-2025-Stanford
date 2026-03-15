from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query

from app.schemas.action_items import (
    ActionItemCreate,
    ActionItemResponse,
    ActionItemUpdate,
    ActionItemListResponse,
    ExtractRequest,
    ExtractResponse,
    MarkDoneRequest,
)
from app.services import ActionItemService
from app.services.exceptions import AppException


router = APIRouter(prefix="/action-items", tags=["action-items"])


def get_action_item_service() -> ActionItemService:
    """Dependency injection for ActionItemService."""
    return ActionItemService()


@router.post(
    "/extract",
    response_model=ExtractResponse,
    summary="Extract action items from text",
    description="Extract action items from text using heuristic or LLM methods.",
    responses={
        400: {"description": "Validation error"},
        500: {"description": "Internal server error"},
        502: {"description": "External service error (Ollama)"},
    },
)
def extract_action_items(
    extract_request: ExtractRequest,
    use_llm: bool = Query(
        False,
        description="Whether to use LLM for extraction (default: heuristic)",
    ),
    action_item_service: ActionItemService = Depends(get_action_item_service),
) -> ExtractResponse:
    """Extract action items from text.

    - **text**: Text to extract action items from (required)
    - **save_note**: Whether to save the input text as a note (optional, default: false)
    - **use_llm**: Whether to use LLM for extraction (optional, default: false)
    """
    return action_item_service.extract_action_items(extract_request, use_llm=use_llm)


@router.get(
    "",
    response_model=ActionItemListResponse,
    summary="List action items",
    description="Retrieve action items with optional filtering.",
    responses={
        404: {"description": "Note not found (if note_id is provided)"},
        500: {"description": "Internal server error"},
    },
)
def list_action_items(
    note_id: Optional[int] = Query(
        None,
        description="Filter by note ID",
    ),
    done: Optional[bool] = Query(
        None,
        description="Filter by completion status",
    ),
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Maximum number of action items to return",
    ),
    offset: Optional[int] = Query(
        None,
        ge=0,
        description="Number of action items to skip",
    ),
    action_item_service: ActionItemService = Depends(get_action_item_service),
) -> ActionItemListResponse:
    """List action items with filtering and pagination.

    - **note_id**: Filter by note ID (optional)
    - **done**: Filter by completion status (optional)
    - **limit**: Maximum number of action items to return (optional)
    - **offset**: Number of action items to skip (optional)
    """
    return action_item_service.get_all_action_items(
        note_id=note_id,
        done=done,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/{action_item_id}",
    response_model=ActionItemResponse,
    summary="Get an action item by ID",
    description="Retrieve a specific action item by its ID.",
    responses={
        404: {"description": "Action item not found"},
        500: {"description": "Internal server error"},
    },
)
def get_action_item(
    action_item_id: int,
    action_item_service: ActionItemService = Depends(get_action_item_service),
) -> ActionItemResponse:
    """Get an action item by ID.

    - **action_item_id**: The ID of the action item to retrieve (required)
    """
    return action_item_service.get_action_item(action_item_id)


@router.post(
    "",
    response_model=ActionItemResponse,
    summary="Create a new action item",
    description="Create a new action item directly.",
    responses={
        400: {"description": "Validation error"},
        404: {"description": "Note not found (if note_id is provided)"},
        500: {"description": "Internal server error"},
    },
)
def create_action_item(
    action_item_create: ActionItemCreate,
    action_item_service: ActionItemService = Depends(get_action_item_service),
) -> ActionItemResponse:
    """Create a new action item.

    - **text**: The action item text (required)
    - **note_id**: ID of the associated note, if any (optional)
    """
    return action_item_service.create_action_item(action_item_create)


@router.put(
    "/{action_item_id}",
    response_model=ActionItemResponse,
    summary="Update an action item",
    description="Update an existing action item.",
    responses={
        404: {"description": "Action item not found"},
        400: {"description": "Validation error"},
        500: {"description": "Internal server error"},
    },
)
def update_action_item(
    action_item_id: int,
    action_item_update: ActionItemUpdate,
    action_item_service: ActionItemService = Depends(get_action_item_service),
) -> ActionItemResponse:
    """Update an action item.

    - **action_item_id**: The ID of the action item to update (required)
    - **text**: Updated action item text (optional)
    - **done**: Whether the action item is completed (optional)
    """
    return action_item_service.update_action_item(action_item_id, action_item_update)


@router.post(
    "/{action_item_id}/done",
    response_model=ActionItemResponse,
    summary="Mark action item as done/not done",
    description="Mark an action item as completed or not completed.",
    responses={
        404: {"description": "Action item not found"},
        500: {"description": "Internal server error"},
    },
)
def mark_action_item_done(
    action_item_id: int,
    mark_done_request: MarkDoneRequest,
    action_item_service: ActionItemService = Depends(get_action_item_service),
) -> ActionItemResponse:
    """Mark an action item as done or not done.

    - **action_item_id**: The ID of the action item to mark (required)
    - **done**: Whether the action item is completed (required)
    """
    return action_item_service.mark_done(action_item_id, mark_done_request)


@router.delete(
    "/{action_item_id}",
    status_code=204,
    response_model=None,
    summary="Delete an action item",
    description="Delete an action item by its ID.",
    responses={
        404: {"description": "Action item not found"},
        500: {"description": "Internal server error"},
    },
)
def delete_action_item(
    action_item_id: int,
    action_item_service: ActionItemService = Depends(get_action_item_service),
) -> None:
    """Delete an action item.

    - **action_item_id**: The ID of the action item to delete (required)
    """
    action_item_service.delete_action_item(action_item_id)


@router.get(
    "/pending",
    response_model=ActionItemListResponse,
    summary="Get pending action items",
    description="Retrieve action items that are not completed.",
    responses={
        500: {"description": "Internal server error"},
    },
)
def get_pending_action_items(
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Maximum number of action items to return",
    ),
    action_item_service: ActionItemService = Depends(get_action_item_service),
) -> ActionItemListResponse:
    """Get pending (not done) action items.

    - **limit**: Maximum number of action items to return (optional)
    """
    return action_item_service.get_pending_action_items(limit=limit)


@router.get(
    "/completed",
    response_model=ActionItemListResponse,
    summary="Get completed action items",
    description="Retrieve action items that are completed.",
    responses={
        500: {"description": "Internal server error"},
    },
)
def get_completed_action_items(
    limit: Optional[int] = Query(
        None,
        ge=1,
        le=100,
        description="Maximum number of action items to return",
    ),
    action_item_service: ActionItemService = Depends(get_action_item_service),
) -> ActionItemListResponse:
    """Get completed action items.

    - **limit**: Maximum number of action items to return (optional)
    """
    return action_item_service.get_completed_action_items(limit=limit)
