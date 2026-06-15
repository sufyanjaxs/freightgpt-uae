from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class DocumentResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    load_id: Optional[UUID]
    document_type: str
    status: str
    filename: str
    original_filename: str
    file_size_bytes: Optional[int]
    mime_type: Optional[str]
    ocr_text: Optional[str]
    extraction: dict
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentUploadResponse(BaseModel):
    id: UUID
    filename: str
    status: str
    upload_url: Optional[str]


class ExtractionResponse(BaseModel):
    id: UUID
    extraction_type: str
    structured_data: dict
    confidence_score: Optional[float]
    model_used: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
