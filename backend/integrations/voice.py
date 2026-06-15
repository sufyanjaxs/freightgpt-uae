import logging
from core.config import settings

logger = logging.getLogger(__name__)


class VoiceService:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.phone_number = settings.TWILIO_PHONE_NUMBER

    async def make_call(self, to: str, twiml: str) -> bool:
        """Make voice call.
        FREE OPTIONS:
        1. Twilio free trial credits (sign up free)
        2. Logs to console in dev mode (no setup needed)
        """
        if all([self.account_sid, self.auth_token, self.phone_number]):
            try:
                from twilio.rest import Client
                client = Client(self.account_sid, self.auth_token)
                call = client.calls.create(twiml=twiml, to=to, from_=self.phone_number)
                logger.info(f"Call initiated: SID {call.sid}")
                return True
            except Exception as e:
                logger.error(f"Call failed: {e}")
                return False
        else:
            # FREE dev mode
            logger.info(f"[VOICE CALL MOCK] To: {to}")
            logger.info(f"[VOICE CALL MOCK] Script: {twiml[:200]}")
            return True

    async def make_ai_call(self, to: str, script: str, language: str = "en") -> bool:
        twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say language="{language}">{script}</Say>
</Response>"""
        return await self.make_call(to, twiml)

    async def send_sms(self, to: str, message: str) -> bool:
        if all([self.account_sid, self.auth_token, self.phone_number]):
            try:
                from twilio.rest import Client
                client = Client(self.account_sid, self.auth_token)
                client.messages.create(body=message, from_=self.phone_number, to=to)
                return True
            except Exception as e:
                logger.error(f"SMS failed: {e}")
                return False
        else:
            logger.info(f"[SMS MOCK] To: {to}, Message: {message[:200]}")
            return True


voice_service = VoiceService()
