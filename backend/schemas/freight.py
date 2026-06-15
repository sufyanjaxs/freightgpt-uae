from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class LoadCreate(BaseModel):
    origin_city: str = Field(..., min_length=1)
    origin_region: Optional[str] = None
    destination_city: str = Field(..., min_length=1)
    destination_region: Optional[str] = None
    pickup_date: datetime
    delivery_date: Optional[datetime] = None
    weight_kg: Optional[float] = None
    volume_m3: Optional[float] = None
    pallets: Optional[int] = None
    description: Optional[str] = None
    commodity: Optional[str] = None
    equipment_type: Optional[str] = None
    load_type: str = "ftl"
    temperature_required: bool = False
    temperature_min_c: Optional[float] = None
    temperature_max_c: Optional[float] = None


class LoadResponse(LoadCreate):
    id: UUID
    tenant_id: UUID
    status: str
    source: Optional[str]
    shipper_rate: Optional[Decimal]
    carrier_rate: Optional[Decimal]
    currency: str
    distance_km: Optional[float]
    assigned_truck_id: Optional[UUID]
    assigned_driver_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class LoadListResponse(BaseModel):
    items: List[LoadResponse]
    total: int
    page: int
    page_size: int


class BidCreate(BaseModel):
    load_id: UUID
    amount: Decimal = Field(..., gt=0)
    bid_type: Optional[str] = None
    profit_margin: Optional[float] = None
    notes: Optional[str] = None


class BidResponse(BidCreate):
    id: UUID
    tenant_id: UUID
    currency: str
    is_winning: bool
    status: str
    confidence_score: Optional[float]
    submitted_at: datetime

    model_config = {"from_attributes": True}


class TrackingEventResponse(BaseModel):
    id: UUID
    event_type: str
    status: str
    latitude: Optional[float]
    longitude: Optional[float]
    address: Optional[str]
    speed_kmh: Optional[float]
    fuel_level_pct: Optional[float]
    recorded_at: datetime

    model_config = {"from_attributes": True}
