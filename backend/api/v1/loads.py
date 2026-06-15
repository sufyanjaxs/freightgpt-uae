from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from core.database import get_db
from core.security import get_current_user
from db.models.user import User
from db.models.freight import Load, LoadStatus, Bid
from schemas.freight import LoadCreate, LoadResponse, LoadListResponse, BidCreate, BidResponse
from typing import Optional
from uuid import UUID

router = APIRouter()


@router.get("/", response_model=LoadListResponse)
async def list_loads(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Load).where(Load.tenant_id == current_user.tenant_id)
    if status:
        query = query.where(Load.status == status)
    query = query.order_by(Load.created_at.desc())

    total_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(total_query)

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    loads = result.scalars().all()

    return LoadListResponse(
        items=[LoadResponse.model_validate(l) for l in loads],
        total=total or 0,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=LoadResponse, status_code=201)
async def create_load(
    data: LoadCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    load = Load(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(load)
    await db.flush()
    return LoadResponse.model_validate(load)


@router.get("/{load_id}", response_model=LoadResponse)
async def get_load(
    load_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Load).where(Load.id == load_id, Load.tenant_id == current_user.tenant_id)
    )
    load = result.scalar_one_or_none()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    return LoadResponse.model_validate(load)


@router.patch("/{load_id}/status")
async def update_load_status(
    load_id: UUID, status: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Load).where(Load.id == load_id, Load.tenant_id == current_user.tenant_id)
    )
    load = result.scalar_one_or_none()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    load.status = status
    return {"status": "updated", "new_status": status}


@router.post("/{load_id}/bids", response_model=BidResponse)
async def place_bid(
    load_id: UUID, data: BidCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    load_result = await db.execute(
        select(Load).where(Load.id == load_id, Load.tenant_id == current_user.tenant_id)
    )
    load = load_result.scalar_one_or_none()
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")

    bid = Bid(load_id=load_id, tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(bid)
    await db.flush()
    return BidResponse.model_validate(bid)
