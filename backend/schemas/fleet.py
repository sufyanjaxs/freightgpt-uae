from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class TruckCreate(BaseModel):
    plate_number: str = Field(..., min_length=1)
    truck_type: str
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    capacity_kg: Optional[float] = None
    capacity_m3: Optional[float] = None
    fuel_type: Optional[str] = None


class TruckResponse(TruckCreate):
    id: UUID
    tenant_id: UUID
    status: str
    vin: Optional[str]
    current_lat: Optional[float]
    current_lng: Optional[float]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DriverCreate(BaseModel):
    full_name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    email: Optional[str] = None
    license_number: str = Field(..., min_length=1)
    nationality: Optional[str] = None
    languages: Optional[List[str]] = None


class DriverResponse(DriverCreate):
    id: UUID
    tenant_id: UUID
    truck_id: Optional[UUID]
    user_id: Optional[UUID]
    is_active: bool
    status: str
    rating: float
    total_trips: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MaintenanceCreate(BaseModel):
    truck_id: UUID
    maintenance_type: str
    description: Optional[str] = None
    cost: Optional[Decimal] = None
    vendor: Optional[str] = None
    scheduled_date: Optional[datetime] = None


class MaintenanceResponse(MaintenanceCreate):
    id: UUID
    status: str
    completed_date: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}
