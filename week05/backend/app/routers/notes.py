from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Note
from ..schemas import NoteCreate, NoteRead, PaginatedNoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


def apply_sort(query, sort: str):
    match sort:
        case "created_desc":
            return query.order_by(Note.id.desc())
        case "created_asc":
            return query.order_by(Note.id.asc())
        case "title_asc":
            return query.order_by(Note.title.asc())
        case "title_desc":
            return query.order_by(Note.title.desc())
        case _:
            return query.order_by(Note.id.desc())


@router.get("/", response_model=PaginatedNoteResponse)
def list_notes(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort: str = Query(default="created_desc"),
    db: Session = Depends(get_db),
) -> Generator[PaginatedNoteResponse, None, None]:
    total = db.execute(select(func.count(Note.id))).scalar() or 0
    offset = (page - 1) * page_size
    rows = (
        db.execute(select(Note).order_by(Note.id.desc()).offset(offset).limit(page_size))
        .scalars()
        .all()
    )
    return PaginatedNoteResponse(
        items=[NoteRead.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=NoteRead, status_code=201)
def create_note(payload: NoteCreate, db: Session = Depends(get_db)) -> NoteRead:
    note = Note(title=payload.title, content=payload.content)
    db.add(note)
    db.flush()
    db.refresh(note)
    return NoteRead.model_validate(note)


@router.get("/search/", response_model=PaginatedNoteResponse)
def search_notes(
    q: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    sort: str = Query(default="created_desc"),
    db: Session = Depends(get_db),
) -> PaginatedNoteResponse:
    base_query = select(Note)
    if q:
        search_pattern = f"%{q}%"
        base_query = base_query.where(
            (func.lower(Note.title).like(func.lower(search_pattern)))
            | (func.lower(Note.content).like(func.lower(search_pattern)))
        )
    total = db.execute(select(func.count()).select_from(base_query.subquery())).scalar() or 0
    offset = (page - 1) * page_size
    query = apply_sort(base_query, sort).offset(offset).limit(page_size)
    rows = db.execute(query).scalars().all()
    return PaginatedNoteResponse(
        items=[NoteRead.model_validate(row) for row in rows],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: int, db: Session = Depends(get_db)) -> NoteRead:
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return NoteRead.model_validate(note)
