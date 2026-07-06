"""AI provider using any OpenAI-compatible Chat Completions API.

Defaults to Google Gemini's OpenAI-compatible endpoint. Uses only stdlib
(urllib) — no extra dependency required.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from collections.abc import Sequence

from app.config import settings
from app.domain.ports.ai_provider import AIProvider, ChatMessage

log = logging.getLogger(__name__)

_MAX_HISTORY = 10
_MAX_TOKENS = 600
_TIMEOUT_S = 30

_SYSTEM_PROMPT = (
    "You are a basic cat care assistant called Rescute AI. "
    "Reply in English, in a warm and concise manner. "
    "Only answer questions about cat care, health, and well-being. "
    "For urgent symptoms, recommend a veterinarian. "
    "Politely decline questions outside the topic of feline care."
)


class OpenAICompatibleProvider(AIProvider):

    def is_configured(self) -> bool:
        return settings.ai_enabled

    def _call_api(self, messages: list[dict], max_tokens: int) -> dict:
        payload = {
            "model": settings.AI_MODEL,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": max_tokens,
        }
        url = f"{settings.AI_BASE_URL.rstrip('/')}/chat/completions"
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.AI_PROVIDER_KEY}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=_TIMEOUT_S) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:500]
            log.error("AI API HTTP error %d: %s", e.code, detail)
            raise RuntimeError("AI service unavailable") from e
        except urllib.error.URLError as e:
            log.error("AI API connection error: %s", e.reason)
            raise RuntimeError("AI service unavailable") from e
        return data

    async def reply(self, system_prompt: str, messages: Sequence[ChatMessage]) -> str:
        history = [{"role": m.role, "content": m.content} for m in messages[-_MAX_HISTORY:]]
        api_messages = [{"role": "system", "content": system_prompt}, *history]
        data = self._call_api(api_messages, _MAX_TOKENS)
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, AttributeError) as e:
            log.error("Unexpected AI reply structure: %s", data)
            raise RuntimeError("Unexpected response from AI service.") from e

    async def generate_response(self, prompt: str, context: str | None = None) -> str:
        messages = [ChatMessage(role="user", content=f"{context or ''}\n{prompt}".strip())]
        return await self.reply(_SYSTEM_PROMPT, messages)
