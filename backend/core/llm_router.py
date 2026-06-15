import logging
import json
from typing import Optional, Dict, Any
from core.config import settings

logger = logging.getLogger(__name__)


class LLMRouter:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self._init_clients()

    def _init_clients(self):
        if settings.OPENAI_API_KEY:
            try:
                from openai import AsyncOpenAI
                self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            except Exception as e:
                logger.warning(f"OpenAI init failed (non-critical): {e}")
        if settings.ANTHROPIC_API_KEY:
            try:
                from anthropic import AsyncAnthropic
                self.anthropic_client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
            except Exception as e:
                logger.warning(f"Anthropic init failed (non-critical): {e}")

    async def route(
        self,
        prompt: str,
        model: str = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        model = model or settings.LLM_ROUTER_MODEL

        if model.startswith("ollama/"):
            return await self._call_ollama(prompt, model.replace("ollama/", ""), system_prompt, temperature)
        elif model.startswith("gpt") or model.startswith("o1"):
            return await self._call_openai(prompt, model, system_prompt, temperature, max_tokens)
        elif model.startswith("claude"):
            return await self._call_anthropic(prompt, model, system_prompt, temperature, max_tokens)
        else:
            # Default to Ollama with fallback
            try:
                return await self._call_ollama(prompt, model, system_prompt, temperature)
            except Exception as e:
                logger.warning(f"Model {model} failed: {e}, trying fallback")
                return await self._call_ollama(prompt, settings.FALLBACK_LLM.replace("ollama/", ""), system_prompt, temperature)

    async def _call_ollama(self, prompt: str, model: str, system_prompt: Optional[str], temperature: float) -> str:
        import httpx
        payload = {
            "model": model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{settings.OLLAMA_BASE_URL}/api/generate", json=payload)
                resp.raise_for_status()
                return resp.json()["response"]
        except Exception as e:
            logger.warning(f"Ollama call failed: {e}")
            # Return a graceful fallback response when LLM is not available
            return self._fallback_response(prompt, system_prompt)

    async def _call_openai(self, prompt: str, model: str, system_prompt: Optional[str],
                           temperature: float, max_tokens: int) -> str:
        if not self.openai_client:
            raise ValueError("OpenAI not configured (free Ollama is default)")
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = await self.openai_client.chat.completions.create(
            model=model, messages=messages, temperature=temperature, max_tokens=max_tokens
        )
        return response.choices[0].message.content

    async def _call_anthropic(self, prompt: str, model: str, system_prompt: Optional[str],
                              temperature: float, max_tokens: int) -> str:
        if not self.anthropic_client:
            raise ValueError("Anthropic not configured (free Ollama is default)")
        kwargs = dict(model=model, max_tokens=max_tokens, temperature=temperature)
        messages = [{"role": "user", "content": prompt}]
        if system_prompt:
            kwargs["system"] = system_prompt
        kwargs["messages"] = messages
        response = await self.anthropic_client.messages.create(**kwargs)
        return response.content[0].text

    def _fallback_response(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Return a reasonable fallback when no LLM is available."""
        return json.dumps({
            "message": "AI agent running in offline mode",
            "analysis": "Install Ollama (ollama.ai) for full AI capabilities, or set OPENAI_API_KEY. "
                       "The system works in rule-based mode without LLM.",
            "fallback": True,
            "suggestion": "Run: ollama pull mistral && ollama pull phi",
        })

    async def generate_structured(self, prompt: str, output_model: type, model: str = None,
                                  system_prompt: Optional[str] = None) -> Any:
        response = await self.route(
            prompt=prompt + "\n\nReturn ONLY valid JSON. No markdown, no explanation.",
            model=model,
            system_prompt=system_prompt or "You are a precise data extraction system. Return only valid JSON.",
        )
        try:
            data = json.loads(response)
            return output_model(**data)
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse structured output: {e}")
            return output_model()


llm_router = LLMRouter()
