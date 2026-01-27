"""
Claude API wrapper for Terminal RPG.
Handles API calls with model configuration and error handling.
"""

import os
from enum import Enum

from anthropic import Anthropic
from anthropic.types import Message


class ClaudeModel(Enum):
    """Available Claude models"""

    SONNET_4_5 = "claude-sonnet-4-5-20250929"
    OPUS_4_5 = "claude-opus-4-5-20251101"
    HAIKU_4_5 = "claude-haiku-4-5-20251001"


def create_message(
    messages: list[dict],
    model: ClaudeModel = ClaudeModel.SONNET_4_5,
    system: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 1.0,
    tools: list[dict] | None = None,
    thinking: dict | None = None,
) -> Message:
    """
    Send a message to Claude API and return the response.

    Args:
        messages: List of message dicts in Anthropic format
        model: Claude model to use
        system: Optional system prompt
        max_tokens: Maximum tokens in response
        temperature: Randomness (0-1)
        tools: Optional tool definitions (sets tool_choice="auto")
        thinking: Optional extended thinking config

    Returns:
        Anthropic Message object

    Raises:
        anthropic.APIError: On API failures
    """
    client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    kwargs = {
        "model": model.value,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": messages,
    }

    if system:
        kwargs["system"] = system

    if tools:
        kwargs["tools"] = tools
        kwargs["tool_choice"] = {"type": "auto"}

    if thinking:
        kwargs["thinking"] = thinking

    return client.messages.create(**kwargs)
