import logging
from core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self):
        self.api_key = settings.WHATSAPP_API_KEY if hasattr(settings, 'WHATSAPP_API_KEY') else None

    async def send_message(self, to: str, message: str) -> bool:
        """Send WhatsApp message.
        FREE OPTIONS:
        1. WhatsApp Cloud API (free tier) - set WHATSAPP_API_KEY
        2. Logs to console in dev mode (no API needed)
        """
        if self.api_key:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://graph.facebook.com/v17.0/WHATSAPP_PHONE_ID/messages",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json={
                            "messaging_product": "whatsapp",
                            "to": to,
                            "type": "text",
                            "text": {"body": message},
                        },
                    )
                    response.raise_for_status()
                    return True
            except Exception as e:
                logger.error(f"WhatsApp send failed: {e}")
                return False
        else:
            # FREE dev mode: log to console
            logger.info(f"[WHATSAPP MOCK] To: {to}, Message: {message[:200]}")
            return True

    async def send_template(self, to: str, template_name: str, parameters: dict) -> bool:
        logger.info(f"[WHATSAPP TEMPLATE MOCK] To: {to}, Template: {template_name}")
        return True


whatsapp_service = WhatsAppService()
