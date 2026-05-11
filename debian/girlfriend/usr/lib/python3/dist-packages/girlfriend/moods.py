"""Mood definitions and output styling."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MoodProfile:
    name: str
    color: str
    emoji: str
    intro: str
    outro: str
    typing_delay: float


MOODS: dict[str, MoodProfile] = {
    "caring": MoodProfile("caring", "magenta", "💕", "gentle mode engaged", "please be nice to yourself", 0.006),
    "jealous": MoodProfile("jealous", "red", "😤", "jealous girlfriend kernel loaded", "who is this 'tmux' and why do you spend nights together", 0.007),
    "hacker": MoodProfile("hacker", "green", "💻", "romance in monochrome", "I parsed your heart with zero warnings", 0.004),
    "clingy": MoodProfile("clingy", "bright_magenta", "🥺", "attention daemon started", "please do not background me", 0.008),
    "sleepy": MoodProfile("sleepy", "cyan", "😴", "power save cuddles enabled", "close five tabs and go eepy", 0.009),
    "gamer": MoodProfile("gamer", "yellow", "🎮", "co-op affection initialized", "our duo queue has elite chemistry", 0.005),
    "motivational": MoodProfile("motivational", "bright_blue", "🚀", "pep-talk subsystem online", "you have survived worse build logs than this", 0.005),
}

DEFAULT_MOOD = "caring"


def get_mood(name: str | None) -> MoodProfile:
    """Return a mood profile, falling back to the default mood."""

    if not name:
        return MOODS[DEFAULT_MOOD]
    return MOODS.get(name.lower(), MOODS[DEFAULT_MOOD])


def list_moods() -> list[str]:
    """Return supported mood names."""

    return sorted(MOODS.keys())
