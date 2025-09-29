import os
from typing import Any, Dict

from third_party.openai_client import OpenAIClient


def get_api_key() -> str:
    """Return the OpenAI API key from the environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENAI_API_KEY not set")
    return api_key


def send_prompt(prompt: str, model: str = "gpt-3.5-turbo", **kwargs: Any) -> Dict[str, Any]:
    """Send a prompt to the OpenAI API and return the JSON response."""
    client = OpenAIClient(api_key=get_api_key())
    messages = [{"role": "user", "content": prompt}]
    return client.chat_completion(messages, model=model, **kwargs)
