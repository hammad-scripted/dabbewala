from fastapi import APIRouter, Depends, HTTPException, status, Query

from database import get_session
from models import Order, OrderCreate, OrderUpdateStatus, StatusLog, OrderStatus
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["orders", "order"])


@router.post("/", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, session: Session = Depends(get_session)):
    new_order = Order(**order.model_dump())
    # add, commit,refresh
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    return new_order


@router.get("/", response_model=List[Order])
async def get_orders(session: Session = Depends(get_session)):
    return session.query(Order).all()
