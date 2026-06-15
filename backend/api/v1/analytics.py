from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from core.database import get_db
from core.security import get_current_user
from db.models.user import User
from db.models.freight import Load, LoadStatus
from db.models.finance import Invoice
from db.models.fleet import Truck, TruckStatus
from typing import Dict, Any
from datetime import datetime, timezone, timedelta

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = current_user.tenant_id

    active_loads = await db.scalar(
        select(func.count())
        .select_from(Load)
        .where(
            and_(
                Load.tenant_id == tenant_id,
                Load.status.in_([LoadStatus.BOOKED, LoadStatus.IN_TRANSIT]),
            )
        )
    )

    available_trucks = await db.scalar(
        select(func.count())
        .select_from(Truck)
        .where(
            and_(
                Truck.tenant_id == tenant_id,
                Truck.status == TruckStatus.AVAILABLE,
                Truck.is_active == True,
            )
        )
    )

    total_trucks = await db.scalar(
        select(func.count())
        .select_from(Truck)
        .where(Truck.tenant_id == tenant_id, Truck.is_active == True)
    )

    total_loads = await db.scalar(
        select(func.count())
        .select_from(Load)
        .where(Load.tenant_id == tenant_id)
    )

    recent_invoices = await db.execute(
        select(func.coalesce(func.sum(Invoice.total_amount), 0))
        .where(
            and_(
                Invoice.tenant_id == tenant_id,
                Invoice.created_at >= datetime.now(timezone.utc) - timedelta(days=30),
            )
        )
    )
    revenue_30d = recent_invoices.scalar() or 0

    return {
        "active_loads": active_loads or 0,
        "available_trucks": available_trucks or 0,
        "total_trucks": total_trucks or 0,
        "total_loads": total_loads or 0,
        "revenue_last_30_days": float(revenue_30d),
        "fleet_utilization": round(((total_trucks or 0) - (available_trucks or 0)) / max(total_trucks or 1, 1) * 100, 1),
    }


@router.get("/loads/timeline")
async def get_load_timeline(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(Load.created_at).label("date"),
            func.count().label("count"),
        )
        .where(
            and_(
                Load.tenant_id == current_user.tenant_id,
                Load.created_at >= since,
            )
        )
        .group_by(func.date(Load.created_at))
        .order_by(func.date(Load.created_at))
    )
    rows = result.all()
    return [{"date": str(row.date), "count": row.count} for row in rows]


@router.get("/revenue/timeline")
async def get_revenue_timeline(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await db.execute(
        select(
            func.date(Invoice.created_at).label("date"),
            func.coalesce(func.sum(Invoice.total_amount), 0).label("revenue"),
        )
        .where(
            and_(
                Invoice.tenant_id == current_user.tenant_id,
                Invoice.created_at >= since,
                Invoice.status == "paid",
            )
        )
        .group_by(func.date(Invoice.created_at))
        .order_by(func.date(Invoice.created_at))
    )
    rows = result.all()
    return [{"date": str(row.date), "revenue": float(row.revenue)} for row in rows]


@router.get("/fleet/status")
async def get_fleet_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Truck.status, func.count().label("count"))
        .where(Truck.tenant_id == current_user.tenant_id, Truck.is_active == True)
        .group_by(Truck.status)
    )
    rows = result.all()
    return {row.status.value if hasattr(row.status, 'value') else row.status: row.count for row in rows}
