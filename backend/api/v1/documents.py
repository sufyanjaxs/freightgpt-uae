from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import get_current_user
from db.models.user import User
from db.models.document import Document, DocumentStatus, DocumentType
from schemas.document import DocumentResponse, DocumentUploadResponse
from services.agent_orchestrator import orchestrator
from typing import List, Optional
from uuid import UUID
import uuid
import os

router = APIRouter()


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    load_id: Optional[UUID] = None,
    doc_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Document).where(Document.tenant_id == current_user.tenant_id)
    if load_id:
        query = query.where(Document.load_id == load_id)
    if doc_type:
        query = query.where(Document.document_type == doc_type)
    query = query.order_by(Document.created_at.desc())

    result = await db.execute(query)
    docs = result.scalars().all()
    return [DocumentResponse.model_validate(d) for d in docs]


@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: str = Form(...),
    load_id: Optional[UUID] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc_id = uuid.uuid4()
    file_ext = os.path.splitext(file.filename or "document.pdf")[1]
    s3_key = f"{current_user.tenant_id}/{doc_id}{file_ext}"

    document = Document(
        id=doc_id,
        tenant_id=current_user.tenant_id,
        load_id=load_id,
        user_id=current_user.id,
        document_type=document_type,
        filename=s3_key,
        original_filename=file.filename or "document",
        file_size_bytes=file.size,
        mime_type=file.content_type,
        status=DocumentStatus.UPLOADED,
    )
    db.add(document)
    await db.flush()

    return DocumentUploadResponse(
        id=doc_id,
        filename=file.filename or "document",
        status="uploaded",
    )


@router.post("/{document_id}/process")
async def process_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.tenant_id == current_user.tenant_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.status = DocumentStatus.PROCESSING

    agent_result = await orchestrator.run_agent("document_ai", {
        "action": "process_document",
        "document_type": document.document_type,
        "ocr_text": document.ocr_text or "",
        "file_metadata": {"filename": document.original_filename},
    })

    document.status = DocumentStatus.EXTRACTED
    document.extraction = agent_result.get("output", {})

    return {
        "status": "processed",
        "document_id": str(document_id),
        "extraction": agent_result,
    }


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(Document.id == document_id, Document.tenant_id == current_user.tenant_id)
    )
    document = result.scalar_one_or_none()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentResponse.model_validate(document)
