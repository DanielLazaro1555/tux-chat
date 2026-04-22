"""Async client for Ollama text generation API."""

import httpx

from bot.config import DEFAULT_MODEL, OLLAMA_URL, TIMEOUT


class OllamaTextClient:
    """Async client for Ollama text generation."""

    def __init__(
        self,
        base_url: str = OLLAMA_URL,
        default_model: str = DEFAULT_MODEL,
        timeout: int = TIMEOUT,
    ):
        self.base_url = base_url
        self.default_model = default_model
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def generate(
        self,
        prompt: str,
        model: str = None,
        context: list = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
    ) -> tuple[str, list | None]:
        """
        Generate a response from Ollama.

        Args:
            prompt: User input text
            model: Model name (uses default if None)
            context: Previous conversation context from Ollama
            temperature: Randomness (0.0 to 1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Tuple of (response_text, new_context)
        """
        model = model or self.default_model

        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        if context:
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
        """Close the HTTP client."""
        await self.client.aclose()
