"""System monitoring helpers for Linux."""

from __future__ import annotations

import os
import shutil
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SystemStats:
    cpu_percent: float
    ram_percent: float
    disk_percent: float
    battery_percent: int | None
    distro: str


def _read_cpu_times() -> tuple[int, int]:
    with open("/proc/stat", "r", encoding="utf-8") as handle:
        line = handle.readline()
    parts = [int(item) for item in line.split()[1:]]
    idle = parts[3] + parts[4]
    total = sum(parts)
    return idle, total


def get_cpu_percent(interval: float = 0.1) -> float:
    idle_1, total_1 = _read_cpu_times()
    time.sleep(interval)
    idle_2, total_2 = _read_cpu_times()
    idle_delta = idle_2 - idle_1
    total_delta = total_2 - total_1
    if total_delta <= 0:
        return 0.0
    return round((1 - (idle_delta / total_delta)) * 100, 1)


def get_ram_percent() -> float:
    values: dict[str, int] = {}
    with open("/proc/meminfo", "r", encoding="utf-8") as handle:
        for line in handle:
            key, value = line.split(":", 1)
            values[key] = int(value.strip().split()[0])
    total = values.get("MemTotal", 1)
    available = values.get("MemAvailable", 0)
    used_ratio = (total - available) / total
    return round(used_ratio * 100, 1)


def get_disk_percent() -> float:
    usage = shutil.disk_usage(Path.home())
    return round((usage.used / usage.total) * 100, 1)


def get_battery_percent() -> int | None:
    base_path = Path("/sys/class/power_supply")
    if not base_path.exists():
        return None
    for entry in base_path.iterdir():
        capacity = entry / "capacity"
        if capacity.exists():
            try:
                return int(capacity.read_text(encoding="utf-8").strip())
            except ValueError:
                return None
    return None


def detect_distro() -> str:
    os_release = Path("/etc/os-release")
    if not os_release.exists():
        return os.uname().sysname
    data: dict[str, str] = {}
    for line in os_release.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        data[key] = value.strip('"')
    return data.get("PRETTY_NAME", data.get("NAME", os.uname().sysname))


def collect_stats() -> SystemStats:
    return SystemStats(
        cpu_percent=get_cpu_percent(),
        ram_percent=get_ram_percent(),
        disk_percent=get_disk_percent(),
        battery_percent=get_battery_percent(),
        distro=detect_distro(),
    )


def reaction_for_stats(stats: SystemStats) -> str:
    if stats.cpu_percent >= 85:
        return "Babe your CPU is hotter than our relationship. Maybe close twelve browser tabs."
    if stats.ram_percent >= 90:
        return "Your RAM is clinging harder than I do. Please release some tabs."
    if stats.disk_percent >= 90:
        return "Disk space is running out and so is my patience with your downloads folder."
    if stats.battery_percent is not None and stats.battery_percent <= 20:
        return "Low battery detected. Plug in before your laptop becomes a dramatic tragedy."
    return "System looks stable. You may continue being adorable and computationally dangerous."
