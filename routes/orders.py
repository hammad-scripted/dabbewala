from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import select, func
from database import get_session
from models import Order, OrderCreate, OrderUpdateStatus, StatusLog, OrderStatus
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/",
    response_model=Order,
    status_code=status.HTTP_201_CREATED,
    description="Create a new order",
    summary="Create a new order",
)
async def create_order(order: OrderCreate, session: Session = Depends(get_session)):
    new_order = Order(**order.model_dump())
    # add, commit,refresh
    session.add(new_order)
    session.commit()
    session.refresh(new_order)
    return new_order


@router.get(
    "/list",
    response_model=List[Order],
    description="Get all orders",  # Description belongs in the decorator
    summary="Retrieve all orders",  # Optional short title for Swagger UI
)
async def get_all_orders(session: Session = Depends(get_session)):
    orders = session.query(Order).all()
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No orders found"
        )
    return orders


@router.get(
    "/",
    response_model=list[Order],
    description="Get all orders based on status and created_at time",  # Description belongs in the decorator,
    summary="Retrieve all orders",  # Optional short title for Swagger UI
)
def list_orders(
    status: OrderStatus | None = Query(
        default=None, description="Filter by order status"
    ),
    created_date: str | None = Query(
        default=None, description="Filter by created date in the format of YYYY-MM-DD"
    ),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=50),
    session: Session = Depends(get_session),
):
    query = select(Order)
    if status:
        query = query.where(Order.status == status)

    if created_date:
        try:
            created_date = datetime.strptime(created_date, "%Y-%m-%d").date()
            query = query.where(func.date(Order.created_at) == created_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD",
            )

    orders = session.exec(query).offset(skip).limit(limit).all()
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No orders found"
        )
    return orders
