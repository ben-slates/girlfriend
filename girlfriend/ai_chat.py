"""Rule-based local chat with future online/local AI extensibility."""

from __future__ import annotations

from .messages import random_chat_reply


def categorize_message(message: str) -> str:
    lowered = message.lower()
    if any(word in lowered for word in ("hello", "hi", "hey")):
        return "hello"
    if any(word in lowered for word in ("help", "what can you do", "commands")):
        return "help"
    if any(word in lowered for word in ("sad", "bad", "down", "tired", "burned out")):
        return "sad"
    if any(word in lowered for word in ("love", "like you", "miss you")):
        return "love"
    if any(word in lowered for word in ("sleep", "nap", "bed", "eepy")):
        return "sleep"
    if any(word in lowered for word in ("bug", "error", "broken", "issue", "traceback")):
        return "bug"
    return "default"


def chat_reply(message: str) -> str:
    return random_chat_reply(categorize_message(message))
