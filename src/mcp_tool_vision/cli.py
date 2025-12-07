"""Command line entry point for preparing MCP image payloads."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .payload import PayloadError, build_payload
from .prompts import SYSTEM_PROMPTS


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
        help="Output the payload as machine-readable JSON.",
    )
    return parser.parse_args(argv)


def emit_text_payload(payload: dict[str, str]) -> None:
    print("# System prompt\n")
    print(payload["system"], end="\n\n")
    print("# User message\n")
    print(payload["user"], end="\n\n")
    print("# Notes\n")
    print(payload["summary"])


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        payload = build_payload(Path(args.image_path), args.command, args.prompt)
    except PayloadError as exc:  # pragma: no cover - user-facing paths
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        emit_text_payload(payload)

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
