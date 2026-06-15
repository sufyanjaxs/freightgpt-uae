from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import get_current_user
from db.models.user import User
from db.models.communication import Communication, CommunicationChannel, CommunicationStatus, Conversation
from integrations.email import email_service
from integrations.whatsapp import whatsapp_service
from integrations.voice import voice_service
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel

router = APIRouter()


class SendEmailRequest(BaseModel):
    to_email: str
    subject: str
    body: str
    cc: Optional[List[str]] = None


class SendWhatsAppRequest(BaseModel):
    to: str
    message: str


class MakeCallRequest(BaseModel):
    to: str
    script: str
    language: str = "en"


@router.post("/email")
async def send_email(
    data: SendEmailRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = await email_service.send_email(
        to_email=data.to_email,
        subject=data.subject,
        body=data.body,
        cc=data.cc,
    )
    comm = Communication(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        channel=CommunicationChannel.EMAIL,
        subject=data.subject,
        body=data.body,
        sender="system@freightgpt.ae",
        recipient=data.to_email,
        status=CommunicationStatus.SENT if success else CommunicationStatus.FAILED,
    )
    db.add(comm)

    return {"status": "sent" if success else "failed"}


@router.post("/whatsapp")
async def send_whatsapp(
    data: SendWhatsAppRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    success = await whatsapp_service.send_message(data.to, data.message)
    comm = Communication(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        channel=CommunicationChannel.WHATSAPP,
        body=data.message,
        sender="system@freightgpt.ae",
        recipient=data.to,
        status=CommunicationStatus.SENT if success else CommunicationStatus.FAILED,
    )
    db.add(comm)

    return {"status": "sent" if success else "failed"}


@router.post("/voice/call")
async def make_call(
    data: MakeCallRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    call_sid = await voice_service.make_ai_call(data.to, data.script, data.language)
    if call_sid:
        comm = Communication(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            channel=CommunicationChannel.VOICE,
            body=data.script,
            sender="system@freightgpt.ae",
            recipient=data.to,
            external_id=call_sid,
            status=CommunicationStatus.SENT,
        )
        db.add(comm)
        return {"status": "call_initiated", "call_sid": call_sid}
    return {"status": "failed"}


@router.get("/history")
async def get_communication_history(
    limit: int = 50,
    channel: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Communication).where(Communication.tenant_id == current_user.tenant_id)
    if channel:
        query = query.where(Communication.channel == channel)
    query = query.order_by(Communication.created_at.desc()).limit(limit)

    result = await db.execute(query)
    communications = result.scalars().all()
    return [
        {
            "id": str(c.id),
            "channel": c.channel.value,
            "direction": c.direction.value,
            "status": c.status.value,
            "subject": c.subject,
            "recipient": c.recipient,
            "created_at": c.created_at.isoformat(),
        }
        for c in communications
    ]
