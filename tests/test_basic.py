"""Basic tests for girlfriend CLI helpers."""

from __future__ import annotations

import unittest

from girlfriend.ai_chat import categorize_message
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
