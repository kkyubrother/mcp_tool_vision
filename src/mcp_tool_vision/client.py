"""Simple HTTP client for calling a /chat/completions-compatible endpoint."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class CompletionRequest:
    model: str
    system: str
    user: str


class CompletionError(Exception):
    """Raised when a completion request fails."""


DEFAULT_TIMEOUT = 30


def _build_request_body(req: CompletionRequest) -> dict[str, Any]:
    return {
        "model": req.model,
        "messages": [
            {"role": "system", "content": req.system},
            {"role": "user", "content": req.user},
        ],
    }


def request_completion(
    req: CompletionRequest,
    *,
    endpoint: str | None = None,
    api_key: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> dict[str, Any]:
    """Send a /chat/completions request and return the parsed JSON response."""

    if not endpoint:
        raise CompletionError("Missing endpoint URL for /chat/completions.")

    url = endpoint.rstrip("/") + "/chat/completions"
    body = json.dumps(_build_request_body(req)).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    http_req = urllib.request.Request(url=url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(http_req, timeout=timeout) as resp:  # type: ignore[arg-type]
            response_data = resp.read().decode("utf-8")
            return json.loads(response_data)
    except urllib.error.HTTPError as exc:  # pragma: no cover - network errors
        detail = exc.read().decode("utf-8", errors="replace")
        raise CompletionError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:  # pragma: no cover - network errors
        raise CompletionError(str(exc)) from exc


def env_default(key: str, fallback: str | None = None) -> str | None:
    """Return an environment variable value if set and non-empty."""

    value = os.environ.get(key)
    if value:
        return value
    return fallback
