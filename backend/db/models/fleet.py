import uuid
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from core.db_compat import UUIDType, JSONType


class TruckStatus:
    AVAILABLE = "available"
    IN_TRANSIT = "in_transit"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"
    RESERVED = "reserved"


class Truck(Base):
    __tablename__ = "trucks"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("tenants.id"), nullable=False)
    plate_number: Mapped[str] = mapped_column(String(50), nullable=False)
    truck_type: Mapped[str] = mapped_column(String(50), nullable=False)
    make: Mapped[str] = mapped_column(String(100), nullable=True)
    model: Mapped[str] = mapped_column(String(100), nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=True)
    vin: Mapped[str] = mapped_column(String(50), nullable=True)
    capacity_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    capacity_m3: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    fuel_type: Mapped[str] = mapped_column(String(50), nullable=True)
    fuel_consumption_per_km: Mapped[float] = mapped_column(Numeric(6, 3), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="available")
    gps_device_id: Mapped[str] = mapped_column(String(100), nullable=True)
    gps_provider: Mapped[str] = mapped_column(String(100), nullable=True)
    insurance_policy: Mapped[str] = mapped_column(String(255), nullable=True)
    insurance_expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    registration_expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    current_lat: Mapped[float] = mapped_column(Numeric(10, 7), nullable=True)
    current_lng: Mapped[float] = mapped_column(Numeric(10, 7), nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSONType(), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="trucks")
    drivers = relationship("Driver", back_populates="truck")
    maintenance_records = relationship("MaintenanceRecord", back_populates="truck")


class Driver(Base):
    __tablename__ = "drivers"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("tenants.id"), nullable=False)
    truck_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("trucks.id"), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("users.id"), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    license_number: Mapped[str] = mapped_column(String(100), nullable=False)
    license_expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    visa_expiry: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    passport_number: Mapped[str] = mapped_column(String(50), nullable=True)
    nationality: Mapped[str] = mapped_column(String(100), nullable=True)
    languages: Mapped[dict] = mapped_column(JSONType(), default=list)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(50), default="available")
    rating: Mapped[float] = mapped_column(Numeric(3, 2), default=5.0)
    total_trips: Mapped[int] = mapped_column(Integer, default=0)
    extra_data: Mapped[dict] = mapped_column(JSONType(), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tenant = relationship("Tenant", back_populates="drivers")
    truck = relationship("Truck", back_populates="drivers")


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    load_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("loads.id"), nullable=False)
    estimated_distance_km: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    estimated_duration_hours: Mapped[float] = mapped_column(Numeric(6, 2), nullable=True)
    estimated_fuel_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    estimated_toll_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    route_polyline: Mapped[str] = mapped_column(Text, nullable=True)
    waypoints: Mapped[dict] = mapped_column(JSONType(), default=list)
    optimal_departure_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    truck_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("trucks.id"), nullable=False)
    maintenance_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    odometer_at_service: Mapped[float] = mapped_column(Numeric(10, 2), nullable=True)
    vendor: Mapped[str] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="scheduled")
    scheduled_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    truck = relationship("Truck", back_populates="maintenance_records")
