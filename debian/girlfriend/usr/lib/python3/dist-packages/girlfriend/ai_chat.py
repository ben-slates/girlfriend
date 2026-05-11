"""Hybrid chat with local replies first and Gemini fallback second."""

from __future__ import annotations

import socket
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any

from .messages import random_chat_reply

try:
    from google import genai
except ImportError:  # pragma: no cover - depends on optional runtime install
    genai = None


DEFAULT_MODELS = [
    "gemini-2.5-flash",
    "gemini-3-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
]
_LOCAL_KEYWORDS = (
    "hello",
    "hi",
    "hey",
    "help",
    "commands",
    "sad",
    "bad",
    "down",
    "tired",
    "burned out",
    "love",
    "like you",
    "miss you",
    "sleep",
    "nap",
    "bed",
    "eepy",
    "bug",
    "error",
    "broken",
    "issue",
    "traceback",
    "compliment",
    "roast",
    "monitor",
    "streak",
    "stats",
    "config",
    "speak",
)


@dataclass
class ChatResult:
    text: str
    source: str
    model: str = ""


class GeminiError(RuntimeError):
    def __init__(self, user_message: str, *, reason: str) -> None:
        super().__init__(user_message)
        self.user_message = user_message
        self.reason = reason


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


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def _looks_like_local_message(message: str) -> bool:
    lowered = " ".join(message.lower().split())
    if not lowered:
        return True
    if len(lowered.split()) <= 5 and any(keyword in lowered for keyword in _LOCAL_KEYWORDS):
        return True
    return any(_similarity(lowered, keyword) >= 0.84 for keyword in _LOCAL_KEYWORDS)


def _command_reply(message: str) -> str | None:
    lowered = message.lower()
    command_map = {
        "compliment": "Use `girlfriend compliment` if you want me extra sweet and nerdy for a second.",
        "roast": "Use `girlfriend roast` if you want playful damage with affection attached.",
        "monitor": "Use `girlfriend monitor` and I will read your CPU, RAM, disk, and battery with attitude.",
        "streak": "Use `girlfriend streak` to see your current streak, or `girlfriend stats` for the full little romance report.",
        "stats": "Use `girlfriend stats` when you want streak numbers, total interactions, and the config path too.",
        "config": "Use `girlfriend config` to view settings, then the `--set-*` options if you want to change your name, mood, theme, or voice.",
        "speak": "Use `girlfriend speak` and I will say something out loud if `espeak` is installed.",
        "chat": "Use `girlfriend chat` and stay with me here in the terminal for a proper conversation.",
    }
    for command_name, reply in command_map.items():
        if command_name in lowered:
            return reply
    return None


def _get_model_list() -> list[str]:
    return list(DEFAULT_MODELS)


def _is_retryable_model_error(error: Exception) -> bool:
    message = str(error).lower()
    retryable_markers = (
        "429",
        "500",
        "503",
        "rate limit",
        "quota",
        "resource exhausted",
        "overload",
        "overloaded",
        "unavailable",
        "timed out",
        "timeout",
        "deadline exceeded",
    )
    return any(marker in message for marker in retryable_markers)


def _normalize_answer(text: str, max_chars: int = 420) -> str:
    cleaned = " ".join((text or "").split())
    if len(cleaned) <= max_chars:
        return cleaned
    trimmed = cleaned[:max_chars].rsplit(" ", 1)[0].rstrip(" ,;:")
    return f"{trimmed}..."


def _api_key_from_config(config: dict[str, Any]) -> str:
    return str(config.get("gemini_api_key", "") or "").strip()


def _has_internet_connection(timeout: float = 2.0) -> bool:
    try:
        with socket.create_connection(("8.8.8.8", 53), timeout=timeout):
            return True
    except OSError:
        return False


def _build_gemini_client(config: dict[str, Any]) -> Any:
    if genai is None:
        raise GeminiError(
            "Gemini support is not installed right now. Reinstall the app with its Python dependencies and try again.",
            reason="sdk-missing",
        )

    api_key = _api_key_from_config(config)
    if not api_key:
        raise GeminiError(
            "I need a Gemini API key before I can use my online brain. Run `girlfriend chat --config` and save it there first.",
            reason="missing-key",
        )

    try:
        return genai.Client(api_key=api_key)
    except Exception as error:  # pragma: no cover - SDK behavior varies by version
        raise GeminiError(
            "I could not initialize Gemini with that API key. Please double-check it in `girlfriend chat --config`.",
            reason=f"client-init:{error}",
        ) from error


def _classify_gemini_error(error: Exception) -> GeminiError:
    message = str(error).lower()

    if any(marker in message for marker in ("api key not valid", "invalid api key", "invalid argument", "unauthenticated", "authentication", "permission denied", "403")):
        return GeminiError(
            "That Gemini API key looks invalid. Open `girlfriend chat --config`, paste a fresh key, and try again.",
            reason=f"invalid-key:{error}",
        )
    if any(marker in message for marker in ("quota", "rate limit", "resource exhausted", "429", "billing")):
        return GeminiError(
            "Your Gemini free quota looks used up right now. Please wait a bit or use a fresh quota window and try again.",
            reason=f"quota:{error}",
        )
    if any(marker in message for marker in ("timeout", "timed out", "deadline exceeded")):
        return GeminiError(
            "Gemini took too long to answer just now. Please try that question again in a moment.",
            reason=f"timeout:{error}",
        )
    if any(marker in message for marker in ("503", "500", "502", "overload", "overloaded", "unavailable", "internal")):
        return GeminiError(
            "Gemini is having a rough moment on Google's side right now. Please try again soon.",
            reason=f"service:{error}",
        )
    if any(marker in message for marker in ("connection", "dns", "network", "name resolution", "temporary failure", "unreachable", "refused")):
        return GeminiError(
            "I cannot reach Gemini right now because the network looks down. Please check your internet connection and try again.",
            reason=f"network:{error}",
        )
    return GeminiError(
        "Gemini had an unexpected API problem just now. Please try again in a moment.",
        reason=f"unknown:{error}",
    )


def _ask_gemini(message: str, config: dict[str, Any]) -> tuple[str, str]:
    client = _build_gemini_client(config)
    if not _has_internet_connection():
        raise GeminiError(
            "I cannot reach Gemini right now because there is no internet connection. I can still stay in local mode with you.",
            reason="offline",
        )

    prompt = (
        "You are a virtual girlfriend replying inside a Linux terminal chat app. "
        "Answer in a warm, cute, supportive girlfriend style. Keep it short, natural, "
        "and in one compact paragraph. Help with spelling mistakes and unclear phrasing "
        "without calling them out harshly. If the user asks about this app's commands, "
        "briefly mention the relevant command. "
        f"Response style: {config.get('chat_response_style', 'compact')}. "
        f"Current chat mood: {config.get('chat_mood') or config.get('preferred_mood', 'caring')}. "
        "User message: "
        f"{message}"
    )

    errors: list[str] = []
    for model_name in _get_model_list():
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            answer = _normalize_answer(getattr(response, "text", "") or "")
            if answer:
                return answer, model_name
            errors.append(f"{model_name}: empty response")
        except Exception as error:
            classified = _classify_gemini_error(error)
            errors.append(f"{model_name}: {classified.reason}")
            if not _is_retryable_model_error(error):
                raise classified from error
    if errors:
        raise GeminiError(
            "Gemini did not return a usable answer right now. Please try again in a moment.",
            reason="all-models-failed: " + " | ".join(errors),
        )
    raise GeminiError("No Gemini models are configured for chat fallback.", reason="no-models")


def chat_reply(message: str, config: dict[str, Any]) -> ChatResult:
    stripped = message.strip()
    if not stripped:
        return ChatResult("Say anything, baby. I am listening.", "local")

    command_help = _command_reply(stripped)
    if command_help:
        return ChatResult(command_help, "local")

    category = categorize_message(stripped)
    if category != "default" or _looks_like_local_message(stripped):
        return ChatResult(random_chat_reply(category), "local")

    try:
        answer, model_name = _ask_gemini(stripped, config)
    except GeminiError as error:
        return ChatResult(
            error.user_message,
            "error",
        )

    return ChatResult(answer, "gemini", model_name)
