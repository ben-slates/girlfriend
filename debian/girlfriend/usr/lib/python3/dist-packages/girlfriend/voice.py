"""Voice output using espeak or espeak-ng with softer presets."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceProfile:
    name: str
    voice: str
    rate: int
    pitch: int
    amplitude: int
    note: str


VOICE_PROFILES: dict[str, VoiceProfile] = {
    "cute": VoiceProfile("cute", "en+f3", 150, 68, 125, "soft feminine default"),
    "soft": VoiceProfile("soft", "en+f2", 145, 62, 120, "gentle and calmer"),
    "anime": VoiceProfile("anime", "en+f4", 165, 78, 120, "lighter and more playful"),
    "goth": VoiceProfile("goth", "en+f2", 135, 45, 118, "lower and moodier"),
    "narrator": VoiceProfile("narrator", "en+f1", 155, 52, 122, "clear and balanced"),
}

DEFAULT_VOICE_PROFILE = "cute"


def list_voice_profiles() -> list[str]:
    """Return sorted voice profile names."""

    return sorted(VOICE_PROFILES.keys())


def get_voice_profile(name: str | None) -> VoiceProfile:
    """Return a configured voice profile."""

    if not name:
        return VOICE_PROFILES[DEFAULT_VOICE_PROFILE]
    return VOICE_PROFILES.get(name.lower(), VOICE_PROFILES[DEFAULT_VOICE_PROFILE])


def get_voice_binary() -> str | None:
    """Return the preferred speech binary."""

    for candidate in ("espeak-ng", "espeak"):
        if shutil.which(candidate):
            return candidate
    return None


def voice_supported() -> bool:
    return get_voice_binary() is not None


def build_speak_command(
    text: str,
    profile_name: str | None = None,
    rate: int | None = None,
    pitch: int | None = None,
) -> list[str]:
    """Build the speech command for the configured profile."""

    binary = get_voice_binary()
    if not binary:
        return []

    profile = get_voice_profile(profile_name)
    effective_rate = rate if rate is not None else profile.rate
    effective_pitch = pitch if pitch is not None else profile.pitch
    return [
        binary,
        "-v",
        profile.voice,
        "-s",
        str(effective_rate),
        "-p",
        str(effective_pitch),
        "-a",
        str(profile.amplitude),
        text,
    ]


def speak_text(
    text: str,
    profile_name: str | None = None,
    rate: int | None = None,
    pitch: int | None = None,
) -> bool:
    command = build_speak_command(text, profile_name=profile_name, rate=rate, pitch=pitch)
    if not command:
        return False
    result = subprocess.run(command, check=False, capture_output=True, text=True)
    return result.returncode == 0
