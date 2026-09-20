from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import BookCreate, BookOut, BookPage, BookQueryParams, BookUpdate
from app.services import books as service

router = APIRouter(prefix="/books", tags=["books"])

DbSession = Annotated[Session, Depends(get_db)]


@router.post("", response_model=BookOut, status_code=201)
def create_book(data: BookCreate, db: DbSession):
    return service.create_book(db, data)


@router.get("", response_model=BookPage)
def list_books(
    db: DbSession,
    params: Annotated[BookQueryParams, Query()],
):
    return service.list_books(db, params)


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: DbSession):
    return service.get_book(db, book_id)


@router.patch("/{book_id}", response_model=BookOut)
def update_book(book_id: int, data: BookUpdate, db: DbSession):
    return service.update_book(db, book_id, data)
