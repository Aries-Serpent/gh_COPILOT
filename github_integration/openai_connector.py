import os
from typing import Any, Dict

import requests

OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


def get_api_key() -> str:
    """Return the OpenAI API key from the environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set")
    return api_key


def send_prompt(prompt: str, model: str = "gpt-3.5-turbo", **kwargs: Any) -> Dict[str, Any]:
    """Send a prompt to the OpenAI API and return the JSON response."""
    headers = {
        "Authorization": f"Bearer {get_api_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        **kwargs,
    }
    response = requests.post(OPENAI_API_URL, json=payload, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json()
