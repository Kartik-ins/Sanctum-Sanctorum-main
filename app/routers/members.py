from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.clock import get_now
from app.db import get_db
from app.schemas import (
    LoanOut,
    LoanStatus,
    MemberCreate,
    MemberOut,
    MemberPage,
    MemberQueryParams,
    MemberStats,
    OrderOut,
)
from app.services import loans as loan_service
from app.services import members as service

DbSession = Annotated[Session, Depends(get_db)]
CurrentTime = Annotated[datetime, Depends(get_now)]

router = APIRouter(prefix="/members", tags=["members"])


@router.post("", response_model=MemberOut, status_code=201)
def create_member(data: MemberCreate, db: DbSession, now: CurrentTime):
    return service.create_member(db, data, now)


@router.get("", response_model=MemberPage)
def list_members(
    db: DbSession,
    params: Annotated[MemberQueryParams, Query()],
):
    return service.list_members(db, params)


@router.get("/{member_id}", response_model=MemberOut)
def get_member(member_id: int, db: DbSession):
    return service.get_member(db, member_id)


@router.get("/{member_id}/orders", response_model=list[OrderOut])
def list_member_orders(member_id: int, db: DbSession):
    return service.list_member_orders(db, member_id)


@router.get("/{member_id}/stats", response_model=MemberStats)
def get_member_stats(member_id: int, db: DbSession, now: CurrentTime):
    return service.get_member_stats(db, member_id, now)


@router.get("/{member_id}/loans", response_model=list[LoanOut])
def list_member_loans(
    member_id: int,
    db: DbSession,
    now: CurrentTime,
    status: LoanStatus | None = None,
):
    return loan_service.list_member_loans(db, member_id, now, status)
