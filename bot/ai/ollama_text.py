# bot/ai/ollama_text.py - Async client for Ollama text generation API.

from typing import List, Optional, Tuple

import httpx

from bot.config import (
    DEFAULT_MODEL,
    MAX_TOKENS,
    OLLAMA_URL,
    SYSTEM_PROMPT_TEXT,
    TIMEOUT,
)


class OllamaTextClient:
    """Async client for Ollama text generation."""

    def __init__(
        self,
        base_url: str = OLLAMA_URL,
        default_model: str = DEFAULT_MODEL,
        timeout: int = TIMEOUT,
        default_max_tokens: int = MAX_TOKENS,
        default_system_prompt: str = SYSTEM_PROMPT_TEXT,
    ):
        self.base_url = base_url
        self.default_model = default_model
        self.timeout = timeout
        self.default_max_tokens = default_max_tokens
        self.default_system_prompt = default_system_prompt
        self.client = httpx.AsyncClient(timeout=timeout)

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[List[int]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> Tuple[str, Optional[List[int]]]:
        model = model or self.default_model
        max_tokens = max_tokens or self.default_max_tokens
        system_prompt = system_prompt or self.default_system_prompt

        payload = {
            "model": model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        if context is not None:
            payload["context"] = context

        try:
            response = await self.client.post(self.base_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data.get("response", ""), data.get("context")
        except httpx.TimeoutException:
            raise TimeoutError(f"Ollama request timed out after {self.timeout} seconds")
        except httpx.HTTPStatusError as e:
            raise RuntimeError(
                f"Ollama API error: {e.response.status_code} - {e.response.text}"
            )
        except Exception as e:
            raise RuntimeError(f"Unexpected error: {str(e)}")

    async def close(self):
        await self.client.aclose()
