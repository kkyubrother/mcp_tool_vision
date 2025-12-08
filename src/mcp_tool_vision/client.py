"""HTTP client built on top of FastMCP dependencies."""

from __future__ import annotations

import os
from typing import Any

import httpx
from fastmcp.exceptions import FastMCPError
from pydantic import BaseModel


class CompletionMessage(BaseModel):
    role: str
    content: str


class CompletionRequest(BaseModel):
    model: str
    system: str
    user: str

    def as_messages(self) -> list[CompletionMessage]:
        return [
            CompletionMessage(role="system", content=self.system),
            CompletionMessage(role="user", content=self.user),
        ]


class CompletionError(FastMCPError):
    """Raised when a completion request fails."""


DEFAULT_TIMEOUT = 30.0


def _build_request_body(req: CompletionRequest) -> dict[str, Any]:
    return {
        "model": req.model,
        "messages": [message.model_dump() for message in req.as_messages()],
    }


def request_completion(
    req: CompletionRequest,
    *,
    endpoint: str | None = None,
    api_key: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Send a /chat/completions request using httpx."""

    if not endpoint:
        raise CompletionError("Missing endpoint URL for /chat/completions.")

    url = endpoint.rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(url, headers=headers, json=_build_request_body(req))
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:  # pragma: no cover - network errors
        detail = exc.response.text
        raise CompletionError(f"HTTP {exc.response.status_code}: {detail}") from exc
    except httpx.HTTPError as exc:  # pragma: no cover - network errors
        raise CompletionError(str(exc)) from exc


def env_default(key: str, fallback: str | None = None) -> str | None:
    """Return an environment variable value if set and non-empty."""

    value = os.environ.get(key)
    if value:
        return value
    return fallback
