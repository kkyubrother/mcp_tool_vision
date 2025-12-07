"""Functions to convert images into a text-friendly payload."""

from __future__ import annotations

import base64
import json
import mimetypes
from pathlib import Path

from .prompts import SYSTEM_PROMPTS


class PayloadError(Exception):
    """Raised when a payload cannot be produced."""


def _guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(path.name)
    return mime or "application/octet-stream"


def encode_image(path: Path) -> str:
    data = path.read_bytes()
    return base64.b64encode(data).decode("ascii")


def build_payload(image_path: Path, command: str, prompt_key: str = "General") -> dict[str, str]:
    """Return a text-friendly payload for a text-only model.

    The payload includes:
    * ``system``: the selected system prompt
    * ``user``: a JSON string combining the command and base64 image

    Parameters
    ----------
    image_path:
        Path to the image file to embed.
    command:
        User instruction describing what to do with the image.
    prompt_key:
        Name of the predefined system prompt. Defaults to ``"General"``.
    """

    if prompt_key not in SYSTEM_PROMPTS:
        options = ", ".join(sorted(SYSTEM_PROMPTS))
        raise PayloadError(f"Unknown system prompt '{prompt_key}'. Choose from: {options}.")

    if not image_path.exists() or not image_path.is_file():
        raise PayloadError(f"Image path does not exist or is not a file: {image_path}")

    system_prompt = SYSTEM_PROMPTS[prompt_key]
    image_b64 = encode_image(image_path)
    mime_type = _guess_mime(image_path)

    user_payload = {
        "command": command.strip(),
        "image_base64": image_b64,
        "filename": image_path.name,
        "mime_type": mime_type,
    }

    return {
        "system": system_prompt,
        "user": json.dumps(user_payload, ensure_ascii=False),
        "summary": (
            "Base64 image content is included in the user JSON under the key "
            "'image_base64'. Send both the system and user fields to the model."
        ),
    }
