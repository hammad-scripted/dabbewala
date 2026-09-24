from datetime import date, datetime, time
from database import get_session
from fastapi import APIRouter, Depends, Query
from models import Order, OrderStatus
from sqlmodel import Session, func, select

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/daily")
def daily_summary(
    summary_date: date | None = Query(
        default=None,
        alias="summary_date",
        description="Date for summary date (YYYY-MM-DD)",
    ),
    session: Session = Depends(get_session),
):
    # Use date.today() instead of datetime.today()
    target_date = summary_date or date.today()

    start_datetime = datetime.combine(target_date, time.min)
    end_datetime = datetime.combine(target_date, time.max)

    # Initialize all enum statuses with a count of 0
    status_counts = {status.value: 0 for status in OrderStatus}

    # Fetch counts grouped by status in a single query
    statement = (
        select(Order.status, func.count(Order.id))
        .where(
            Order.created_at >= start_datetime,
            Order.created_at <= end_datetime,
        )
        .group_by(Order.status)
    )

    results = session.exec(statement).all()

    total = 0
    for status, count in results:
        # Handle string or Enum status keying safely
        key = status.value if hasattr(status, "value") else status
        status_counts[key] = count
        total += count

    return {
        "date": target_date,
        "total": total,
        "summary": status_counts,
    }