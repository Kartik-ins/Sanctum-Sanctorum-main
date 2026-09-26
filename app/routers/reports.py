from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import TopBook
from app.services import reports as service

DbSession = Annotated[Session, Depends(get_db)]
LimitQuery = Annotated[int, Query(ge=1, le=50)]

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/top-books", response_model=list[TopBook])
def top_books(db: DbSession, limit: LimitQuery = 5):
    return service.top_books(db, limit)
