from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


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


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
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
    unique: List[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def extract_action_items_llm(text: str, model: str | None = None) -> List[str]:
    """
    Extract action items from text using Ollama LLM with structured outputs.

    Args:
        text: Input text to extract action items from
        model: Ollama model name. If None, uses OLLAMA_MODEL env var or "llama3.1:8b"

    Returns:
        List of extracted action items as strings

    Raises:
        ValueError: If the LLM response cannot be parsed or doesn't match schema
        Exception: For Ollama connection errors or model not found
    """
    if model is None:
        model = os.getenv("OLLAMA_MODEL", "llama3.1:8b")

    text = text.strip()
    if not text:
        return []

    prompt = f"""Extract action items from the following text. Return only a JSON object with an "action_items" field containing an array of strings, where each string is a clear, concise action item. Do not include any explanatory text.

Text: {text}"""

    response = chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        format=ActionItems.model_json_schema(),
        stream=False,
        options={"temperature": 0},
    )

    result = ActionItems.model_validate_json(response.message.content)
    return result.action_items


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
