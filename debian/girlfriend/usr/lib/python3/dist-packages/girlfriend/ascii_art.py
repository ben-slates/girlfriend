"""ASCII art assets for the CLI."""

from __future__ import annotations

from random import choice

LOGO = r"""
██████╗ ██╗██████╗ ██╗     ███████╗██████╗ ██╗███████╗███╗   ██╗██████╗
██╔════╝ ██║██╔══██╗██║     ██╔════╝██╔══██╗██║██╔════╝████╗  ██║██╔══██╗
██║  ███╗██║██████╔╝██║     █████╗  ██████╔╝██║█████╗  ██╔██╗ ██║██║  ██║
██║   ██║██║██╔══██╗██║     ██╔══╝  ██╔══██╗██║██╔══╝  ██║╚██╗██║██║  ██║
╚██████╔╝██║██║  ██║███████╗██║     ██║  ██║██║███████╗██║ ╚████║██████╔╝
 ╚═════╝ ╚═╝╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝  ╚═══╝╚═════╝
"""

REACTIONS = [
    r"""
      (\_/)
      (o.o)
      />❤️  compiling feelings...
    """,

    r'''
      .-"""-.
     / .===. \
     \/ 6 6 \/
     ( \___/ )
___ooo__V__ooo________________________________
    ''',

    r"""
      /\_/\  
     ( ^.^ ) 
      > ^ <   your terminal cuteness is detected
    """,

    r"""
      [^_^]
      /|_|\   sudo apt install affection
       / \
    """,

    r"""
       (\_/)
      ( •_•)
      / >🍪   cookies deployed successfully
    """,

    r"""
      ┌( ಠ_ಠ)┘
      └(ಠ_ಠ └)   dancing through your stack traces
    """,

    r"""
       _____
      /     \
     | 0   0 |
     |   ^   |   system happiness: ONLINE
      \ \_/ /
       ----- 
    """,

    r"""
      (ﾉ◕ヮ◕)ﾉ*:･ﾟ✧
        launching positive vibes...
    """,

    r"""
       /\___/\
      (  o o  )
      /   *   \   meow.exe is running
      \__\_/__/
    """,

    r"""
       __
     <(o )___
      ( ._> /   debugging duck approved
       `---'
    """,

    r"""
      ╭(◕ ◡ ◕)╮
        loading friendship module...
    """,

    r"""
       (☞ﾟヮﾟ)☞
       code looks suspiciously awesome
    """,

    r"""
      ┏(-_-)┛┗(-_- )┓
         synchronized coding achieved
    """,

    r"""
       💻 + ☕ + 🎧
         productivity combo activated
    """,

    r"""
      ╔════════════╗
      ║ no bugs :) ║
      ╚════════════╝
           ...hopefully
    """,
]

def random_reaction() -> str:
    """Return a random ASCII reaction."""

    return choice(REACTIONS)
