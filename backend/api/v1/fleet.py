from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import get_current_user
from db.models.user import User
from db.models.fleet import Truck, Driver, MaintenanceRecord
from schemas.fleet import TruckCreate, TruckResponse, DriverCreate, DriverResponse, MaintenanceCreate, MaintenanceResponse
from typing import List
from uuid import UUID

router = APIRouter()


@router.get("/trucks", response_model=List[TruckResponse])
async def list_trucks(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Truck).where(Truck.tenant_id == current_user.tenant_id)
    )
    trucks = result.scalars().all()
    return [TruckResponse.model_validate(t) for t in trucks]


@router.post("/trucks", response_model=TruckResponse, status_code=201)
async def create_truck(
    data: TruckCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    truck = Truck(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(truck)
    await db.flush()
    return TruckResponse.model_validate(truck)


@router.get("/trucks/{truck_id}", response_model=TruckResponse)
async def get_truck(
    truck_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Truck).where(Truck.id == truck_id, Truck.tenant_id == current_user.tenant_id)
    )
    truck = result.scalar_one_or_none()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    return TruckResponse.model_validate(truck)


@router.put("/trucks/{truck_id}/location")
async def update_truck_location(
    truck_id: UUID, lat: float, lng: float,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Truck).where(Truck.id == truck_id, Truck.tenant_id == current_user.tenant_id)
    )
    truck = result.scalar_one_or_none()
    if not truck:
        raise HTTPException(status_code=404, detail="Truck not found")
    truck.current_lat = lat
    truck.current_lng = lng
    return {"status": "updated"}


@router.get("/drivers", response_model=List[DriverResponse])
async def list_drivers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Driver).where(Driver.tenant_id == current_user.tenant_id)
    )
    drivers = result.scalars().all()
    return [DriverResponse.model_validate(d) for d in drivers]


@router.post("/drivers", response_model=DriverResponse, status_code=201)
async def create_driver(
    data: DriverCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    driver = Driver(tenant_id=current_user.tenant_id, **data.model_dump())
    db.add(driver)
    await db.flush()
    return DriverResponse.model_validate(driver)


@router.get("/maintenance", response_model=List[MaintenanceResponse])
async def list_maintenance(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(MaintenanceRecord)
        .join(Truck)
        .where(Truck.tenant_id == current_user.tenant_id)
    )
    records = result.scalars().all()
    return [MaintenanceResponse.model_validate(r) for r in records]


@router.post("/maintenance", response_model=MaintenanceResponse, status_code=201)
async def create_maintenance(
    data: MaintenanceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = MaintenanceRecord(**data.model_dump())
    db.add(record)
    await db.flush()
    return MaintenanceResponse.model_validate(record)
