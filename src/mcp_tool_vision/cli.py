"""Command line entry point for preparing MCP image payloads."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from .client import CompletionError, CompletionRequest, env_default, request_completion
from .payload import PayloadError, build_payload
from .prompts import SYSTEM_PROMPTS

ENV_ENDPOINT = "MCP_VISION_API_URL"
ENV_MODEL = "MCP_VISION_MODEL"
ENV_API_KEY = "MCP_VISION_API_KEY"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Prepare a system + user payload so text-only models can process base64 images."
        )
    )
    parser.add_argument(
        "image_path",
        metavar="IMAGE",
        help="Path to the image file that will be base64-encoded.",
    )
    parser.add_argument(
        "command",
        metavar="COMMAND",
        help="Instruction describing how to read the image.",
    )
    parser.add_argument(
        "--prompt",
        default="General",
        choices=sorted(SYSTEM_PROMPTS),
        help="Predefined system prompt to use (default: General).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output the payload or response as machine-readable JSON.",
    )
    parser.add_argument(
        "--call",
        action="store_true",
        help="Immediately call the /chat/completions endpoint with the payload.",
    )
    parser.add_argument(
        "--endpoint",
        default=env_default(ENV_ENDPOINT),
        help=f"Base URL for the API (default: ${ENV_ENDPOINT}).",
    )
    parser.add_argument(
        "--model",
        default=env_default(ENV_MODEL),
        help=f"Model name to send (default: ${ENV_MODEL}).",
    )
    parser.add_argument(
        "--api-key",
        default=env_default(ENV_API_KEY),
        help=f"Optional API key for Authorization header (default: ${ENV_API_KEY}).",
    )
    return parser.parse_args(argv)


def emit_text_payload(payload: dict[str, str]) -> None:
    print("# System prompt\n")
    print(payload["system"], end="\n\n")
    print("# User message\n")
    print(payload["user"], end="\n\n")
    print("# Notes\n")
    print(payload["summary"])


def emit_text_response(payload: dict[str, str], response: dict) -> None:
    emit_text_payload(payload)
    print("\n# Model response\n")
    choices = response.get("choices")
    if choices:
        content = choices[0].get("message", {}).get("content")
        if content is not None:
            print(content)
            return
    print(json.dumps(response, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        payload = build_payload(Path(args.image_path), args.command, args.prompt)
    except PayloadError as exc:  # pragma: no cover - user-facing paths
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.call:
        if not args.model:
            print("Error: --model is required when using --call.", file=sys.stderr)
            return 1
        if not args.endpoint:
            print("Error: --endpoint is required when using --call.", file=sys.stderr)
            return 1

        req = CompletionRequest(
            model=args.model,
            system=payload["system"],
            user=payload["user"],
        )

        try:
            response = request_completion(
                req, endpoint=args.endpoint, api_key=args.api_key
            )
        except CompletionError as exc:  # pragma: no cover - network errors
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        if args.json:
            output = {
                "request": {
                    "endpoint": args.endpoint,
                    "model": args.model,
                    "messages": [
                        {"role": "system", "content": payload["system"]},
                        {"role": "user", "content": payload["user"]},
                    ],
                },
                "response": response,
            }
            json.dump(output, sys.stdout, ensure_ascii=False, indent=2)
            print()
        else:
            emit_text_response(payload, response)
    else:
        if args.json:
            json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
            print()
        else:
            emit_text_payload(payload)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
