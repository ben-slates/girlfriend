"""Hybrid chat with local replies first and Gemini fallback second."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from difflib import SequenceMatcher
from typing import Any

from .config import save_config
from .messages import random_chat_reply

try:
    from google import genai
except ImportError:  # pragma: no cover - depends on optional runtime install
    genai = None


GEMINI_API_KEY = "AIzaSyAHVb-xvWrde9DBJKEPEgHyVKMbfHlzY9k"
DEFAULT_MODELS = [
    "gemini-2.5-flash",
    "gemini-3-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
]

_GEMINI_CLIENT = genai.Client(api_key=GEMINI_API_KEY) if genai is not None else None
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


def _today_string() -> str:
    return date.today().isoformat()


def _gemini_usage_snapshot(config: dict[str, Any]) -> tuple[str, int]:
    usage = config.get("gemini_usage", {})
    if not isinstance(usage, dict):
        usage = {}
    usage_date = str(usage.get("date", ""))
    usage_count = int(usage.get("count", 0))
    if usage_date != _today_string():
        return _today_string(), 0
    return usage_date, usage_count


def _can_use_gemini(config: dict[str, Any]) -> bool:
    _, usage_count = _gemini_usage_snapshot(config)
    limit = int(config.get("gemini_daily_limit", 50))
    return usage_count < limit


def _consume_gemini_request(config: dict[str, Any]) -> int:
    usage_date, usage_count = _gemini_usage_snapshot(config)
    updated_count = usage_count + 1
    config["gemini_usage"] = {"date": usage_date, "count": updated_count}
    save_config(config)
    return updated_count


def _ask_gemini(message: str) -> tuple[str, str]:
    if _GEMINI_CLIENT is None:
        raise RuntimeError("Gemini SDK is not installed.")

    prompt = (
        "You are a virtual girlfriend replying inside a Linux terminal chat app. "
        "Answer in a warm, cute, supportive girlfriend style. Keep it short, natural, "
        "and in one compact paragraph. Help with spelling mistakes and unclear phrasing "
        "without calling them out harshly. If the user asks about this app's commands, "
        "briefly mention the relevant command. User message: "
        f"{message}"
    )

    errors: list[str] = []
    for model_name in _get_model_list():
        try:
            response = _GEMINI_CLIENT.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            answer = _normalize_answer(getattr(response, "text", "") or "")
            if answer:
                return answer, model_name
            errors.append(f"{model_name}: empty response")
        except Exception as error:
            errors.append(f"{model_name}: {error}")
            if not _is_retryable_model_error(error):
                continue
    joined_errors = " | ".join(errors) if errors else "No Gemini models configured"
    raise RuntimeError(f"All Gemini models failed. {joined_errors}")


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

    if not _can_use_gemini(config):
        return ChatResult(
            "I used all 50 smart replies for today, so stay with me in local mode for now, okay? Try again tomorrow and I will be extra helpful.",
            "limit",
        )

    try:
        answer, model_name = _ask_gemini(stripped)
    except Exception:
        return ChatResult(
            "My online brain is being shy right now, so stay with me a little simpler for a bit and try again soon.",
            "error",
        )

    _consume_gemini_request(config)
    return ChatResult(answer, "gemini", model_name)
