from datetime import datetime, date, time
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlmodel import Session as SQLModelSession, select, col

from database import get_session
from models import Order, OrderCreate, OrderStatus, OrderUpdateStatus, StatusLog

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    description="Create a new order",
    summary="Create a new order",
)
def create_order(
    order: OrderCreate, session: SQLModelSession = Depends(get_session)
):
    # SQLModel objects can be instantiated directly from schema data
    new_order = Order.model_validate(order)
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    return new_order


@router.get(
    "/list",
    response_model=List[Order],
    description="Get all orders",
    summary="Retrieve all orders",
)
def get_all_orders(session: SQLModelSession = Depends(get_session)):
    query = select(Order)
    orders = session.exec(query).all()
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No orders found"
        )
    return orders


@router.get(
    "/",
    response_model=List[Order],
    description="Get all orders based on status and created_at time",
    summary="Retrieve all orders on status and created_at",
)
def list_orders(
    status_filter: OrderStatus | None = Query(
        default=None, alias="status", description="Filter by order status"
    ),
    created_date: date | None = Query(
        default=None, description="Filter by created date (YYYY-MM-DD)"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=50),
    session: SQLModelSession = Depends(get_session),
):
    query = select(Order)

    if status_filter:
        query = query.where(Order.status == status_filter)

    if created_date:
        # Use a datetime range query to allow DB indexing on created_at
        start_datetime = datetime.combine(created_date, time.min)
        end_datetime = datetime.combine(created_date, time.max)
        query = query.where(
            col(Order.created_at) >= start_datetime,
            col(Order.created_at) <= end_datetime,
        )

    # Apply pagination directly to the SQL query statement
    query = query.offset(skip).limit(limit)
    orders = session.exec(query).all()

    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No orders found"
        )

    return orders