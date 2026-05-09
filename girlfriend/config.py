"""Config and data persistence helpers."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

def _resolve_app_dir() -> Path:
    override = os.environ.get("GIRLFRIEND_HOME")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".girlfriend"


APP_DIR = _resolve_app_dir()
CONFIG_FILE = APP_DIR / "config.json"
STREAK_FILE = APP_DIR / "streak.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "preferred_mood": "caring",
    "notification_frequency_minutes": 180,
    "username": "",
    "enable_voice": False,
    "voice_profile": "cute",
    "voice_rate": 150,
    "voice_pitch": 68,
    "theme": "wholesome",
    "typing_animation": True,
    "bedtime_hour": 23,
}


def ensure_app_dir() -> Path:
    preferred = APP_DIR
    try:
        preferred.mkdir(parents=True, exist_ok=True)
        probe = preferred / ".write_test"
        probe.write_text("ok\n", encoding="utf-8")
        probe.unlink()
        return preferred
    except OSError:
        fallback = Path(tempfile.gettempdir()) / "girlfriend"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def get_config_path() -> Path:
    return ensure_app_dir() / "config.json"


def get_streak_path() -> Path:
    return ensure_app_dir() / "streak.json"


def load_config() -> dict[str, Any]:
    config_file = get_config_path()
    if not config_file.exists():
        save_config(DEFAULT_CONFIG.copy())
        return DEFAULT_CONFIG.copy()

    try:
        content = json.loads(config_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        content = {}

    merged = DEFAULT_CONFIG.copy()
    merged.update(content)
    return merged


def save_config(config: dict[str, Any]) -> None:
    config_file = get_config_path()
    config_file.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n", encoding="utf-8")
