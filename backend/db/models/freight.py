import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from core.db_compat import UUIDType, JSONType


class LoadStatus:
    PENDING = "pending"
    BOOKED = "booked"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class Load(Base):
    __tablename__ = "loads"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("tenants.id"), nullable=False)
    shipper_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("users.id"), nullable=True)
    external_id: Mapped[str] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    load_type: Mapped[str] = mapped_column(String(50), default="ftl")

    origin_city: Mapped[str] = mapped_column(String(255), nullable=False)
    origin_region: Mapped[str] = mapped_column(String(100), nullable=True)
    origin_lat: Mapped[float] = mapped_column(Numeric(10, 7), nullable=True)
    origin_lng: Mapped[float] = mapped_column(Numeric(10, 7), nullable=True)

    destination_city: Mapped[str] = mapped_column(String(255), nullable=False)
    destination_region: Mapped[str] = mapped_column(String(100), nullable=True)
    destination_lat: Mapped[float] = mapped_column(Numeric(10, 7), nullable=True)
    destination_lng: Mapped[float] = mapped_column(Numeric(10, 7), nullable=True)

    pickup_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    delivery_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    pickup_window_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    pickup_window_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    weight_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    volume_m3: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    pallets: Mapped[int] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    commodity: Mapped[str] = mapped_column(String(255), nullable=True)
    equipment_type: Mapped[str] = mapped_column(String(100), nullable=True)
    temperature_required: Mapped[bool] = mapped_column(Boolean, default=False)
    temperature_min_c: Mapped[float] = mapped_column(Numeric(5, 1), nullable=True)
    temperature_max_c: Mapped[float] = mapped_column(Numeric(5, 1), nullable=True)

    shipper_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    carrier_rate: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="AED")
    distance_km: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)

    special_instructions: Mapped[str] = mapped_column(Text, nullable=True)
    documents_required: Mapped[dict] = mapped_column(JSONType(), default=list)
    is_hazardous: Mapped[bool] = mapped_column(Boolean, default=False)

    assigned_truck_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("trucks.id"), nullable=True)
    assigned_driver_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("drivers.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="loads")
    bids = relationship("Bid", back_populates="load")
    tracking_events = relationship("TrackingEvent", back_populates="load")
    documents = relationship("Document", back_populates="load")


class Bid(Base):
    __tablename__ = "bids"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    load_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("loads.id"), nullable=False)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("tenants.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="AED")
    bid_type: Mapped[str] = mapped_column(String(50), nullable=True)
    is_winning: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(50), default="pending")
    profit_margin: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    responded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    load = relationship("Load", back_populates="bids")


class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    load_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("loads.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    latitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[float] = mapped_column(Numeric(10, 7), nullable=True)
    address: Mapped[str] = mapped_column(String(512), nullable=True)
    speed_kmh: Mapped[float] = mapped_column(Numeric(6, 2), nullable=True)
    heading: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    odometer_km: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    fuel_level_pct: Mapped[float] = mapped_column(Numeric(5, 2), nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSONType(), default=dict)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    load = relationship("Load", back_populates="tracking_events")
