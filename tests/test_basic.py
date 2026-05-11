"""Basic tests for girlfriend CLI helpers."""

from __future__ import annotations

import unittest

from girlfriend.ai_chat import categorize_message, chat_reply
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
