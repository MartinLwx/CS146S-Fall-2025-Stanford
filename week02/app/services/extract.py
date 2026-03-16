from __future__ import annotations
import os

import re
from typing import Optional

from ollama import Client
from pydantic import BaseModel

from app.config import settings
from app.services.exceptions import (
    OllamaConnectionException,
    OllamaServiceException,
    ValidationException,
)


class ActionItems(BaseModel):
    action_items: list[str]


BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> list[str]:
    lines = text.splitlines()
    extracted: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def extract_action_items_llm(text: str, model: Optional[str] = None) -> list[str]:
    """
    Extract action items from text using Ollama LLM with structured outputs.

    Args:
        text: Input text to extract action items from
        model: Ollama model name. If None, uses settings.ollama.model

    Returns:
        List of extracted action items as strings

    Raises:
        OllamaConnectionException: For Ollama connection errors
        OllamaServiceException: For Ollama service errors or model not found
        ValidationException: If the LLM response cannot be parsed or doesn't match schema
    """
    # Use configured model if not specified
    if model is None:
        model = settings.ollama.model

    text = text.strip()
    if not text:
        return []

    prompt = f"""Extract action items from the following text. Return only a JSON object with an "action_items" field containing an array of strings, where each string is a clear, concise action item. Do not include any explanatory text.

Text: {text}"""

    try:
        response = Client(host=str(settings.ollama.base_url)).chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            format=ActionItems.model_json_schema(),
            stream=False,
            options={
                "temperature": settings.ollama.temperature,
                "timeout": settings.ollama.timeout,
            },
        )
    except ConnectionError as e:
        raise OllamaConnectionException(
            message=f"Failed to connect to Ollama at {settings.ollama.base_url}",
            details={"base_url": str(settings.ollama.base_url), "error": str(e)},
        ) from e
    except Exception as e:
        raise OllamaServiceException(
            message=f"Ollama service error: {str(e)}",
            details={"model": model, "error": str(e)},
        ) from e

    try:
        result = ActionItems.model_validate_json(response.message.content)
        return result.action_items
    except Exception as e:
        raise ValidationException(
            message="Failed to parse LLM response",
            details={"response": response.message.content, "error": str(e)},
        )


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
