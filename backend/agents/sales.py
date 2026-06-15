import logging
from typing import Dict, Any, Optional
from agents.base import BaseAgent

logger = logging.getLogger(__name__)

SALES_SYSTEM_PROMPT = """You are the AI Sales Agent for FreightGPT UAE, an autonomous logistics OS in the GCC.
Capabilities: Voice calls, Email, WhatsApp, Arabic, English, Urdu.
Can answer: Rates, Capacity, Availability, ETA.
You are professional, knowledgeable, and persuasive. Adapt to the customer's language and communication style.
Understand GCC logistics market deeply including UAE, Saudi Arabia, Qatar, Oman, Bahrain.
Always aim to book meetings, close deals, and provide exceptional customer experience."""


class SalesAgent(BaseAgent):
    def __init__(self, model: str = "gpt-4"):
        super().__init__("sales", model)

    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        action = input_data.get("action", "handle_inquiry")
        channel = input_data.get("channel", "email")
        message = input_data.get("message", "")
        customer = input_data.get("customer", {})
        language = input_data.get("language", "en")
        context = input_data.get("context", {})

        if action == "handle_inquiry":
            return await self._handle_inquiry(channel, message, customer, language, context)
        elif action == "send_quote":
            return await self._send_quote(customer, input_data.get("quote_details", {}), language)
        elif action == "follow_up":
            return await self._follow_up(customer, input_data.get("history", []), language)
        elif action == "book_meeting":
            return await self._book_meeting(customer, input_data.get("preferred_times", []), language)
        elif action == "voice_call_script":
            return await self._generate_call_script(customer, context, language)
        elif action == "whatsapp_message":
            return await self._generate_whatsapp(customer, message, language)
        else:
            return await self._handle_inquiry(channel, message, customer, language, context)

    async def _handle_inquiry(self, channel: str, message: str, customer: Dict[str, Any],
                              language: str, context: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"""Handle a sales inquiry received via {channel}:

Customer: {customer}
Message: {message}
Response Language: {language}
Additional Context: {context}

Generate an appropriate response that:
1. Addresses the customer's specific query
2. Highlights FreightGPT UAE's AI-powered logistics advantages
3. Provides relevant information about rates, capacity, or services
4. Includes a clear call-to-action
5. Is culturally appropriate for GCC business environment

Also classify: inquiry_type, urgency, sentiment (positive/neutral/negative), recommended_next_action."""
        result = await self.think(prompt, SALES_SYSTEM_PROMPT)
        return {"response": result, "channel": channel, "language": language}

    async def _send_quote(self, customer: Dict[str, Any], quote_details: Dict[str, Any],
                          language: str) -> Dict[str, Any]:
        prompt = f"""Generate a professional freight quote for:
Customer: {customer}
Quote Details: {quote_details}
Language: {language}

Include: pricing breakdown, service terms, validity period, payment terms, FreightGPT UAE differentiators.
Format professionally for email/WhatsApp in GCC business context."""
        result = await self.think(prompt, SALES_SYSTEM_PROMPT)
        return {"quote": result, "customer": customer}

    async def _follow_up(self, customer: Dict[str, Any], history: list, language: str) -> Dict[str, Any]:
        prompt = f"""Generate a sales follow-up communication:
Customer: {customer}
Previous Interactions: {history}
Language: {language}

Determine: follow-up type (email/call/whatsapp), tone, key messages, timing recommendation.
Handle objections professionally. Move towards next step in sales cycle."""
        result = await self.think(prompt, SALES_SYSTEM_PROMPT)
        return {"follow_up": result}

    async def _book_meeting(self, customer: Dict[str, Any], preferred_times: list,
                            language: str) -> Dict[str, Any]:
        prompt = f"""Generate a meeting booking request:
Customer: {customer}
Preferred Times: {preferred_times}
Language: {language}

Create a professional meeting invitation that: proposes specific times, sets clear agenda, 
provides video call link instructions, confirms timezone (GST/AST), and requests confirmation."""
        result = await self.think(prompt, SALES_SYSTEM_PROMPT)
        return {"meeting_request": result}

    async def _generate_call_script(self, customer: Dict[str, Any], context: Dict[str, Any],
                                    language: str) -> Dict[str, Any]:
        prompt = f"""Generate a voice call script for sales call:
Customer: {customer}
Call Context: {context}
Language: {language}

Script needs: opening, value proposition, discovery questions, objection handling,
closing statement, call duration recommendation, key talking points."""
        result = await self.think(prompt, SALES_SYSTEM_PROMPT)
        return {"call_script": result}

    async def _generate_whatsapp(self, customer: Dict[str, Any], message: str,
                                 language: str) -> Dict[str, Any]:
        prompt = f"""Generate a WhatsApp business message:
Customer: {customer}
Context: {message}
Language: {language}

WhatsApp best practices: concise, professional, includes call-to-action, uses appropriate formatting,
respects business hours, culturally appropriate for GCC."""
        result = await self.think(prompt, SALES_SYSTEM_PROMPT)
        return {"whatsapp_message": result}
