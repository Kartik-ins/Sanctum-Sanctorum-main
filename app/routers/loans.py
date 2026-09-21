from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.clock import get_now
from app.db import get_db
from app.schemas import LoanCreate, LoanOut
from app.services import loans as service

DbSession = Annotated[Session, Depends(get_db)]
CurrentTime = Annotated[datetime, Depends(get_now)]

router = APIRouter(prefix="/loans", tags=["loans"])


@router.post("", response_model=LoanOut, status_code=201)
def create_loan(data: LoanCreate, db: DbSession, now: CurrentTime):
    return service.create_loan(db, data, now)


@router.get("/{loan_id}", response_model=LoanOut)
def get_loan(loan_id: int, db: DbSession, now: CurrentTime):
    return service.get_loan(db, loan_id, now)


@router.post("/{loan_id}/return", response_model=LoanOut)
def return_loan(loan_id: int, db: DbSession, now: CurrentTime):
    return service.return_loan(db, loan_id, now)
