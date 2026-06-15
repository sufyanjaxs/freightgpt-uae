import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from core.database import Base
from core.db_compat import UUIDType, JSONType


class DocumentStatus:
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VERIFIED = "verified"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class DocumentType:
    POD = "pod"
    INVOICE = "invoice"
    BILL_OF_LADING = "bill_of_lading"
    CONTRACT = "contract"
    ID_PROOF = "id_proof"
    VEHICLE_DOC = "vehicle_doc"
    CUSTOMS = "customs"
    OTHER = "other"


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("tenants.id"), nullable=False)
    load_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("loads.id"), nullable=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("users.id"), nullable=True)
    document_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="uploaded")
    filename: Mapped[str] = mapped_column(String(512), nullable=False)
    original_filename: Mapped[str] = mapped_column(String(512), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=True)
    s3_key: Mapped[str] = mapped_column(String(1024), nullable=True)
    ocr_text: Mapped[str] = mapped_column(Text, nullable=True)
    extraction: Mapped[dict] = mapped_column(JSONType(), default=dict)
    verification_status: Mapped[str] = mapped_column(String(50), nullable=True)
    verified_by: Mapped[uuid.UUID] = mapped_column(UUIDType(), nullable=True)
    extra_data: Mapped[dict] = mapped_column(JSONType(), default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    load = relationship("Load", back_populates="documents")


class DocumentExtraction(Base):
    __tablename__ = "document_extractions"

    id: Mapped[uuid.UUID] = mapped_column(UUIDType(), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUIDType(), ForeignKey("documents.id"), nullable=False)
    extraction_type: Mapped[str] = mapped_column(String(100), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=True)
    structured_data: Mapped[dict] = mapped_column(JSONType(), default=dict)
    confidence_score: Mapped[int] = mapped_column(Integer, nullable=True)
    model_used: Mapped[str] = mapped_column(String(100), nullable=True)
    processing_time_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
