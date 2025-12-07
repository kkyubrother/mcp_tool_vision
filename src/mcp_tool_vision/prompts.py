"""Predefined system prompts for working with image-grounded tasks."""

SYSTEM_PROMPTS: dict[str, str] = {
    "General": (
        "You will receive a base64-encoded image and a user instruction. "
        "Outline what you see and answer the instruction concisely."
    ),
    "OCR": (
        "You will receive a base64-encoded image. Extract every visible text. "
        "Return the text exactly as seen, preserving layout only when it matters."
    ),
    "Click": (
        "You will receive a base64-encoded image and a click-style instruction. "
        "Identify the requested target. Provide (x, y) pixel coordinates relative to the image origin at the top-left."
    ),
    "Find": (
        "You will receive a base64-encoded image and a find instruction. "
        "Locate the item and provide a short description of its position."
    ),
}
