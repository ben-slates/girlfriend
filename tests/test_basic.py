"""Basic tests for girlfriend CLI helpers."""

from __future__ import annotations

import unittest

from girlfriend.ai_chat import categorize_message, chat_reply
from girlfriend.ascii_art import MOOD_REACTIONS, random_reaction
from girlfriend.config import DEFAULT_CONFIG
from girlfriend.messages import COMPLIMENTS, LOVE_QUOTES, RANDOM_MESSAGES
from girlfriend.moods import get_mood, list_moods
from girlfriend.system_monitor import detect_distro
from girlfriend.voice import get_voice_profile, list_voice_profiles


class TestBasic(unittest.TestCase):
    def test_mood_lookup(self) -> None:
        self.assertEqual(get_mood("hacker").name, "hacker")
        self.assertIn("caring", list_moods())

    def test_chat_categories(self) -> None:
        self.assertEqual(categorize_message("hello there"), "hello")
        self.assertEqual(categorize_message("I found a bug"), "bug")

    def test_chat_reply_uses_local_for_basic_greeting(self) -> None:
        result = chat_reply("hey babe", DEFAULT_CONFIG.copy())
        self.assertEqual(result.source, "local")
        self.assertTrue(result.text)

    def test_chat_reply_uses_local_for_command_help(self) -> None:
        result = chat_reply("how do i use streak", DEFAULT_CONFIG.copy())
        self.assertEqual(result.source, "local")
        self.assertIn("girlfriend streak", result.text)

    def test_default_config_includes_chat_settings(self) -> None:
        self.assertIn("gemini_api_key", DEFAULT_CONFIG)
        self.assertIn("chat_mood", DEFAULT_CONFIG)
        self.assertIn("chat_theme", DEFAULT_CONFIG)
        self.assertIn("chat_response_style", DEFAULT_CONFIG)

    def test_chat_reply_reports_missing_api_key(self) -> None:
        config = DEFAULT_CONFIG.copy()
        config["gemini_api_key"] = ""
        result = chat_reply("Explain Linux cgroups and namespaces in detail", config)
        self.assertEqual(result.source, "error")
        self.assertIn("Gemini API key", result.text)
        self.assertIn("chat --config", result.text)

    def test_ascii_art_supports_mood_specific_reactions(self) -> None:
        self.assertIn("caring", MOOD_REACTIONS)
        self.assertIn("hacker", MOOD_REACTIONS)
        self.assertTrue(MOOD_REACTIONS["sleepy"])

    def test_random_reaction_accepts_unknown_mood(self) -> None:
        reaction = random_reaction("unknown")
        self.assertTrue(reaction.strip())

    def test_message_catalog_sizes(self) -> None:
        self.assertGreaterEqual(len(COMPLIMENTS), 10)
        self.assertGreaterEqual(len(LOVE_QUOTES), 50)
        for items in RANDOM_MESSAGES.values():
            self.assertGreaterEqual(len(items), 10)

    def test_detect_distro(self) -> None:
        self.assertTrue(detect_distro())

    def test_voice_profiles(self) -> None:
        self.assertIn("cute", list_voice_profiles())
        self.assertEqual(get_voice_profile("anime").voice, "en+f4")


if __name__ == "__main__":
    unittest.main()
