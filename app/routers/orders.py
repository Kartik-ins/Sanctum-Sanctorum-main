from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.clock import get_now
from app.db import get_db
from app.schemas import OrderCreate, OrderOut
from app.services import orders as service

DbSession = Annotated[Session, Depends(get_db)]
CurrentTime = Annotated[datetime, Depends(get_now)]

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
def create_order(data: OrderCreate, db: DbSession, now: CurrentTime):
    return service.create_order(db, data, now)


@router.get("/{order_id}", response_model=OrderOut)
def get_order(order_id: int, db: DbSession):
    return service.get_order(db, order_id)


@router.post("/{order_id}/pay", response_model=OrderOut)
def pay_order(order_id: int, db: DbSession):
    return service.pay_order(db, order_id)


@router.post("/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: int, db: DbSession):
    return service.cancel_order(db, order_id)
