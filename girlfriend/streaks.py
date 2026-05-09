"""Daily streak tracking."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date

from .config import get_streak_path


@dataclass
class StreakStats:
    current_streak: int
    longest_streak: int
    total_interactions: int
    last_seen: str


def _today() -> date:
    return date.today()


def load_streaks() -> dict[str, int | str]:
    streak_file = get_streak_path()
    if not streak_file.exists():
        return {"current_streak": 0, "longest_streak": 0, "total_interactions": 0, "last_seen": ""}
    try:
        return json.loads(streak_file.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {"current_streak": 0, "longest_streak": 0, "total_interactions": 0, "last_seen": ""}


def save_streaks(data: dict[str, int | str]) -> None:
    streak_file = get_streak_path()
    streak_file.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def update_streak() -> StreakStats:
    data = load_streaks()
    today = _today()
    today_str = today.isoformat()
    last_seen = str(data.get("last_seen", ""))

    if not last_seen:
        current_streak = 1
    else:
        last_date = date.fromisoformat(last_seen)
        delta_days = (today - last_date).days
        if delta_days == 0:
            current_streak = int(data.get("current_streak", 0))
        elif delta_days == 1:
            current_streak = int(data.get("current_streak", 0)) + 1
        else:
            current_streak = 1

    total_interactions = int(data.get("total_interactions", 0)) + 1
    longest_streak = max(int(data.get("longest_streak", 0)), current_streak)

    updated = {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_interactions": total_interactions,
        "last_seen": today_str,
    }
    save_streaks(updated)
    return StreakStats(**updated)


def get_streak_stats() -> StreakStats:
    data = load_streaks()
    return StreakStats(
        current_streak=int(data.get("current_streak", 0)),
        longest_streak=int(data.get("longest_streak", 0)),
        total_interactions=int(data.get("total_interactions", 0)),
        last_seen=str(data.get("last_seen", "")),
    )
