"""Thin wrapper around the Anthropic API used by the rest of the CLI."""
from __future__ import annotations

import json
import os

import anthropic

DEFAULT_MODEL = os.environ.get("ARCH_COMPLIANCE_MODEL", "claude-sonnet-4-5-20250929")

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic()
    return _client


def _strip_fences(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else ""
        if text.endswith("```"):
            text = text.rsplit("```", 1)[0]
    return text.strip()


def call_json(
    model: str,
    system: str,
    user_text: str,
    max_tokens: int = 4000,
    image_blocks: list[dict] | None = None,
):
    """Call the model and parse a JSON response. Raises if the response isn't valid JSON."""
    content: list[dict] = []
    if image_blocks:
        content.extend(image_blocks)
    content.append({"type": "text", "text": user_text})

    response = get_client().messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": content}],
    )
    text = "".join(block.text for block in response.content if block.type == "text")
    text = _strip_fences(text)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Model did not return valid JSON: {e}\n---\n{text[:2000]}") from e
