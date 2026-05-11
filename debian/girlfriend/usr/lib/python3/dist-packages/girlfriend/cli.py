"""CLI entrypoint for girlfriend."""

from __future__ import annotations

import argparse
import random
import sys
import time

from rich.align import Align
from rich.console import Console
from rich.console import Group
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from . import __version__
from .ai_chat import chat_reply
from .ascii_art import LOGO, random_reaction
from .config import get_config_path, load_config, save_config
from .messages import (
    random_compliment,
    random_message,
    random_package_joke,
    random_quote,
    random_roast,
    random_tmux_vim_joke,
)
from .moods import get_mood, list_moods
from .notification import notification_supported, send_notification
from .streaks import get_streak_stats, update_streak
from .system_monitor import collect_stats, reaction_for_stats
from .voice import list_voice_profiles, speak_text, voice_supported

console = Console()

THEMES = ["anime", "wholesome", "hacker", "goth", "gamer", "yandere", "cozy"]
RESPONSE_STYLES = ["compact", "playful", "supportive", "technical", "flirty"]


def typing_print(message: str, color: str, enabled: bool) -> None:
    if not enabled:
        console.print(f"[{color}]{message}[/{color}]")
        return
    for character in message:
        console.print(f"[{color}]{character}[/{color}]", end="")
        time.sleep(0.006)
    console.print()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="girlfriend",
        description="Funny romantic virtual girlfriend assistant for Linux terminal users.",
        epilog="Example: girlfriend --mood hacker | girlfriend monitor | girlfriend chat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--mood", choices=list_moods(), help="Select a personality mood.")
    parser.add_argument("--quote", action="store_true", help="Show a random love quote.")
    parser.add_argument("--theme", choices=THEMES, help="Temporarily override the theme.")
    parser.add_argument("--notify", action="store_true", help="Send the selected message as a desktop notification.")
    parser.add_argument("--no-typing", action="store_true", help="Disable typing animation for this run.")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("compliment", help="Generate a nerdy compliment.")
    subparsers.add_parser("roast", help="Generate a harmless Linux-user roast.")
    subparsers.add_parser("streak", help="Show your daily interaction streak.")
    subparsers.add_parser("stats", help="Show detailed interaction stats.")
    subparsers.add_parser("monitor", help="Inspect CPU, RAM, disk, and battery with commentary.")
    subparsers.add_parser("speak", help="Speak a fresh message aloud using espeak.")
    chat_parser = subparsers.add_parser("chat", help="Start local-first chat mode with Gemini fallback.")
    chat_parser.add_argument("--config", action="store_true", help="Configure AI chat settings interactively.")

    config_parser = subparsers.add_parser("config", help="View or update config.")
    config_parser.add_argument("--set-name", help="Set preferred display name.")
    config_parser.add_argument("--set-mood", choices=list_moods(), help="Set preferred mood.")
    config_parser.add_argument("--set-theme", choices=THEMES, help="Set preferred theme.")
    config_parser.add_argument("--enable-voice", action="store_true", help="Enable voice by default.")
    config_parser.add_argument("--disable-voice", action="store_true", help="Disable voice by default.")
    config_parser.add_argument("--set-voice-profile", choices=list_voice_profiles(), help="Set the offline voice profile.")
    config_parser.add_argument("--set-voice-rate", type=int, help="Set voice speed. Lower is softer, higher is faster.")
    config_parser.add_argument("--set-voice-pitch", type=int, help="Set voice pitch. Higher sounds brighter.")

    subparsers.add_parser("notify-test", help="Send a sample desktop notification.")

    return parser


def header(config: dict[str, object], mood_name: str, message: str | None = None) -> None:
    theme = config.get("theme", "wholesome")
    username = str(config.get("username") or "cutie")
    mood = get_mood(mood_name)
    art_panel = Panel.fit(
        random_reaction(mood.name),
        title=f"{mood.name} art",
        border_style="bright_white",
        padding=(0, 1),
    )
    top_block = "\n".join(
        [
            LOGO.strip("\n"),
            "",
            f"{mood.emoji} Welcome back, handsome.",
            "Type 'girlfriend --help' for commands.",
        ]
    )
    content: list[object] = [top_block]
    if message:
        content.extend(
            [
                "",
                Panel.fit(
                    f"[bold]{message}[/bold]",
                    title="Now Playing",
                    subtitle=f"{mood.name} mode",
                    border_style="bright_white",
                    padding=(0, 2),
                ),
            ]
        )
    content.extend(
        [
            "",
            f"[dim]mood: {mood.name} • theme: {theme} • operator: {username}[/dim]",
            "",
            Align.right(art_panel),
        ]
    )
    console.print(
        Panel.fit(
            Group(*content),
            title=f"girlfriend v{__version__}",
            subtitle=mood.outro,
            border_style=mood.color,
            padding=(1, 2),
        )
    )


def build_message(args: argparse.Namespace, config: dict[str, object]) -> tuple[str, str]:
    mood_name = args.mood or str(config.get("preferred_mood", "caring"))
    mood = get_mood(mood_name)

    if args.command == "compliment":
        body = random_compliment()
    elif args.command == "roast":
        body = random_roast()
    elif args.quote:
        body = random_quote()
    else:
        extras = [random_package_joke(), random_tmux_vim_joke()]
        body = random.choice([random_message(mood.name), *extras])

    full = f"{mood.emoji} {body} {mood.emoji}"
    return mood.name, full


def handle_default(args: argparse.Namespace, config: dict[str, object]) -> int:
    mood_name, message = build_message(args, config)
    header(config, mood_name, message)

    stats = update_streak()
    console.print(f"[dim]streak: {stats.current_streak} day(s) • total chats: {stats.total_interactions}[/dim]")

    if args.notify:
        ok = send_notification("girlfriend", message)
        console.print("[green]notification sent[/green]" if ok else "[yellow]notify-send not available[/yellow]")

    if bool(config.get("enable_voice", False)):
        if not speak_text(
            message,
            profile_name=str(config.get("voice_profile", "cute")),
            rate=int(config.get("voice_rate", 150)),
            pitch=int(config.get("voice_pitch", 68)),
        ):
            console.print("[yellow]voice requested in config, but espeak is unavailable.[/yellow]")
    return 0


def handle_streak(config: dict[str, object]) -> int:
    mood_name = str(config.get("preferred_mood", "caring"))
    header(config, mood_name, "Your streak report is ready.")
    stats = get_streak_stats()
    console.print(Panel.fit(f"Current streak: {stats.current_streak} day(s)\nLongest streak: {stats.longest_streak} day(s)\nLast seen: {stats.last_seen or 'never'}", title="Streak", border_style="magenta"))
    return 0


def handle_stats(config: dict[str, object]) -> int:
    mood_name = str(config.get("preferred_mood", "caring"))
    header(config, mood_name, "Here is your little romance report.")
    stats = get_streak_stats()
    table = Table(title="girlfriend stats")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")
    table.add_row("Current streak", str(stats.current_streak))
    table.add_row("Longest streak", str(stats.longest_streak))
    table.add_row("Total interactions", str(stats.total_interactions))
    table.add_row("Last seen", stats.last_seen or "never")
    table.add_row("Config path", str(get_config_path()))
    console.print(table)
    return 0


def handle_monitor(config: dict[str, object]) -> int:
    mood_name = str(config.get("preferred_mood", "caring"))
    header(config, mood_name, "Reading your machine with affection and suspicion.")
    stats = collect_stats()
    table = Table(title=f"System monitor • {stats.distro}")
    table.add_column("Signal", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("CPU", f"{stats.cpu_percent}%")
    table.add_row("RAM", f"{stats.ram_percent}%")
    table.add_row("Disk", f"{stats.disk_percent}%")
    table.add_row("Battery", f"{stats.battery_percent}%" if stats.battery_percent is not None else "not detected")
    console.print(table)
    console.print(Panel.fit(reaction_for_stats(stats), title="Reaction", border_style="red"))
    return 0


def handle_speak(config: dict[str, object]) -> int:
    mood_name = str(config.get("preferred_mood", "caring"))
    message = f"{get_mood(mood_name).emoji} {random_message(mood_name)}"
    header(config, mood_name, "Voice mode is warming up.")
    console.print(message)
    if not voice_supported():
        console.print("[yellow]espeak or espeak-ng is not installed, so I could not speak aloud.[/yellow]")
        return 1
    speak_text(
        message,
        profile_name=str(config.get("voice_profile", "cute")),
        rate=int(config.get("voice_rate", 150)),
        pitch=int(config.get("voice_pitch", 68)),
    )
    return 0


def _chat_mood(config: dict[str, object]) -> str:
    return str(config.get("chat_mood") or config.get("preferred_mood", "caring"))


def _chat_theme(config: dict[str, object]) -> str:
    return str(config.get("chat_theme") or config.get("theme", "wholesome"))


def handle_chat_config(config: dict[str, object]) -> int:
    console.print(
        Panel.fit(
            "Tune Gemini access and how chat feels without editing JSON by hand.",
            title="Chat Config",
            border_style="magenta",
        )
    )

    current_key = str(config.get("gemini_api_key", "") or "")
    masked_key = f"{current_key[:6]}...{current_key[-4:]}" if len(current_key) >= 10 else ("set" if current_key else "not set")

    current_table = Table(title="Current chat settings")
    current_table.add_column("Setting", style="cyan")
    current_table.add_column("Value", style="magenta")
    current_table.add_row("Gemini API key", masked_key)
    current_table.add_row("Chat mood", _chat_mood(config))
    current_table.add_row("Chat theme", _chat_theme(config))
    current_table.add_row("Response style", str(config.get("chat_response_style", "compact")))
    console.print(current_table)

    api_key_prompt = "Gemini API key"
    if current_key:
        api_key_prompt += " (press Enter to keep current key)"
    entered_key = Prompt.ask(api_key_prompt, default="")
    if entered_key.strip():
        config["gemini_api_key"] = entered_key.strip()

    mood_choices = list_moods()
    theme_choices = list(THEMES)
    style_choices = list(RESPONSE_STYLES)

    config["chat_mood"] = Prompt.ask(
        "Chat mood",
        choices=mood_choices,
        default=_chat_mood(config),
    )
    config["chat_theme"] = Prompt.ask(
        "Chat theme",
        choices=theme_choices,
        default=_chat_theme(config),
    )
    config["chat_response_style"] = Prompt.ask(
        "Response style",
        choices=style_choices,
        default=str(config.get("chat_response_style", "compact")),
    )

    save_config(config)

    updated_table = Table(title="Saved chat settings")
    updated_table.add_column("Setting", style="cyan")
    updated_table.add_column("Value", style="green")
    updated_table.add_row("Gemini API key", "saved" if str(config.get("gemini_api_key", "") or "").strip() else "not set")
    updated_table.add_row("Chat mood", str(config["chat_mood"]))
    updated_table.add_row("Chat theme", str(config["chat_theme"]))
    updated_table.add_row("Response style", str(config["chat_response_style"]))
    console.print(updated_table)
    console.print(f"[dim]Config file: {get_config_path()}[/dim]")
    return 0


def handle_chat(config: dict[str, object]) -> int:
    mood_name = _chat_mood(config)
    color = get_mood(mood_name).color
    theme_name = _chat_theme(config)
    header(config, mood_name, "Chat mode is open. Ask me anything.")
    console.print(
        Panel.fit(
            f"Chat mode. Type `exit` or `quit` to leave.\n[dim]theme: {theme_name} • style: {config.get('chat_response_style', 'compact')}[/dim]",
            title="Chat",
            border_style=color,
        )
    )
    while True:
        try:
            user_input = console.input("[bold cyan]you> [/bold cyan]").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            return 0
        if user_input.lower() in {"exit", "quit"}:
            typing_print("I will be here waiting in your terminal, babe.", color, True)
            return 0
        reply = chat_reply(user_input, config)
        typing_print(f"{get_mood(mood_name).emoji} {reply.text}", color, bool(config.get("typing_animation", True)))


def handle_config(args: argparse.Namespace, config: dict[str, object]) -> int:
    changed = False
    if args.set_name is not None:
        config["username"] = args.set_name
        changed = True
    if args.set_mood is not None:
        config["preferred_mood"] = args.set_mood
        changed = True
    if args.set_theme is not None:
        config["theme"] = args.set_theme
        changed = True
    if args.enable_voice:
        config["enable_voice"] = True
        changed = True
    if args.disable_voice:
        config["enable_voice"] = False
        changed = True
    if args.set_voice_profile is not None:
        config["voice_profile"] = args.set_voice_profile
        changed = True
    if args.set_voice_rate is not None:
        config["voice_rate"] = max(80, min(args.set_voice_rate, 260))
        changed = True
    if args.set_voice_pitch is not None:
        config["voice_pitch"] = max(0, min(args.set_voice_pitch, 99))
        changed = True
    if changed:
        save_config(config)
        console.print("[green]Config updated.[/green]")

    mood_name = str(config.get("preferred_mood", "caring"))
    header(config, mood_name, "Config loaded and ready.")
    table = Table(title="girlfriend config")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="magenta")
    for key, value in config.items():
        table.add_row(key, str(value))
    console.print(table)
    console.print(f"[dim]Config file: {get_config_path()}[/dim]")
    return 0


def handle_notify_test() -> int:
    config = load_config()
    mood_name = str(config.get("preferred_mood", "caring"))
    header(config, mood_name, "Testing desktop affection delivery.")
    if not notification_supported():
        console.print("[yellow]notify-send is not installed.[/yellow]")
        return 1
    sent = send_notification("girlfriend", "I miss you. Please blink and hydrate.")
    console.print("[green]Notification sent.[/green]" if sent else "[red]Notification failed.[/red]")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    config = load_config()

    if args.theme:
        config["theme"] = args.theme

    if args.command == "streak":
        return handle_streak(config)
    if args.command == "stats":
        return handle_stats(config)
    if args.command == "monitor":
        return handle_monitor(config)
    if args.command == "speak":
        return handle_speak(config)
    if args.command == "chat":
        if getattr(args, "config", False):
            return handle_chat_config(config)
        return handle_chat(config)
    if args.command == "config":
        return handle_config(args, config)
    if args.command == "notify-test":
        return handle_notify_test()

    return handle_default(args, config)


if __name__ == "__main__":
    sys.exit(main())
