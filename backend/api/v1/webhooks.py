from fastapi import APIRouter, Request, HTTPException
from core.config import settings
import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if settings.STRIPE_WEBHOOK_SECRET:
        try:
            from stripe import Webhook
            event = Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid payload")
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid signature")

        event_type = event.get("type")
        event_data = event.get("data", {}).get("object", {})

        logger.info(f"Stripe webhook received: {event_type} - {event_data.get('id')}")

        return {"status": "received", "event_type": event_type}

    return {"status": "received"}


@router.post("/twilio/voice")
async def twilio_voice_webhook(request: Request):
    form = await request.form()
    call_sid = form.get("CallSid")
    caller = form.get("From")
    logger.info(f"Twilio voice webhook: {call_sid} from {caller}")
    return {"status": "received"}


@router.post("/twilio/status")
async def twilio_status_webhook(request: Request):
    form = await request.form()
    message_sid = form.get("MessageSid")
    status = form.get("MessageStatus")
    logger.info(f"Twilio status webhook: {message_sid} -> {status}")
    return {"status": "received"}


@router.post("/gps")
async def gps_webhook(data: dict):
    device_id = data.get("device_id")
    lat = data.get("latitude")
    lng = data.get("longitude")
    logger.info(f"GPS update: {device_id} -> ({lat}, {lng})")
    return {"status": "received"}
