"""Desktop notification helpers."""

from __future__ import annotations

import shutil
import subprocess


def notification_supported() -> bool:
    return shutil.which("notify-send") is not None


def send_notification(title: str, body: str) -> bool:
    if not notification_supported():
        return False
    result = subprocess.run(
        ["notify-send", title, body],
        check=False,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0
