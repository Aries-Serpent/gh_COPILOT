from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Any, Dict, List

import requests


@dataclass
class OpenAIClient:
    """Simple OpenAI API client with retry and rate limiting."""

    api_key: str | None = None
    base_url: str | None = None
    rate_limit: float = 1.0
    max_retries: int = 3

    def __post_init__(self) -> None:
        self.api_key = self.api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = self.base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        self._last_request = 0.0

    def _wait_rate_limit(self) -> None:
        elapsed = time.time() - self._last_request
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def request(self, method: str, endpoint: str, payload: Dict[str, Any]) -> requests.Response:
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        for attempt in range(1, self.max_retries + 1):
            self._wait_rate_limit()
            self._last_request = time.time()
            try:
                resp = self.session.request(method, url, headers=self._headers(), json=payload, timeout=30)
            except requests.RequestException as exc:  # pragma: no cover - network failure
                self.logger.warning("Request error on attempt %s: %s", attempt, exc)
                if attempt == self.max_retries:
                    raise
                time.sleep(attempt)
                continue
            if resp.status_code >= 500 and attempt < self.max_retries:
                time.sleep(attempt)
                continue
            return resp
        return resp  # type: ignore

    def chat_completion(
        self, messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo", **params: Any
    ) -> Dict[str, Any]:
        payload = {"model": model, "messages": messages}
        payload.update(params)
        resp = self.request("POST", "chat/completions", payload)
        resp.raise_for_status()
        return resp.json()


__all__ = ["OpenAIClient"]
