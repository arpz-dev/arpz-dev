#!/usr/bin/env python3
"""Generate the profile banner and three linked social images for a GitHub README."""

from argparse import ArgumentParser
from datetime import date
from html import escape
from pathlib import Path
from urllib.parse import urlsplit

RED = "#ed0026"
BLACK = "#0d0d0d"

SOCIALS = (
    (
        "discord", "Discord",
        '<path fill="#fff" fill-rule="evenodd" d="M4 6c5-4 11-4 16 0l2 11c-2 2-4 3-6 3l-1-2a13 13 0 0 1-6 0l-1 2c-2 0-4-1-6-3L4 6Zm4 5a1.5 1.8 0 1 0 0 3.6A1.5 1.8 0 0 0 8 11Zm8 0a1.5 1.8 0 1 0 0 3.6 1.5 1.8 0 0 0 0-3.6Z"/>',
        "M0 0h320v96H20A20 20 0 0 1 0 76Z",
    ),
    (
        "instagram", "Instagram",
        '<g fill="none" stroke="#fff" stroke-width="1.9"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/></g><circle cx="17.5" cy="6.5" r="1.15" fill="#fff"/>',
        "M0 0h320v96H0Z",
    ),
    (
        "x", "X / Twitter",
        '<path fill="none" stroke="#fff" stroke-width="1.8" stroke-linecap="round" d="M3 3l18 18M21 3 3 21"/>',
        "M0 0h320v76a20 20 0 0 1-20 20H0Z",
    ),
)


def banner(year):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="960" height="360" viewBox="0 0 960 360">
  <title>arpz-dev</title>
  <desc>I design tiny web pages, build Discord bots and share the process.</desc>
  <path d="M32 0h896a32 32 0 0 1 32 32v328H0V32A32 32 0 0 1 32 0Z" fill="{RED}"/>
  <g fill="#fff" font-family="monospace" font-size="15" letter-spacing="2">
    <text x="48" y="54">(01) WEB PAGES</text>
    <text x="244" y="54">(02) DISCORD BOTS</text>
    <text x="480" y="54">(03) DESIGN LAB</text>
    <text x="912" y="54" text-anchor="end">© {year}</text>
  </g>
  <path d="M48 74h864" stroke="#fff" stroke-opacity=".45"/>
  <circle cx="784" cy="205" r="128" fill="none" stroke="#fff" stroke-opacity=".6" stroke-dasharray="2 10"/>
  <circle cx="784" cy="205" r="100" fill="{BLACK}"/>
  <path d="M790 132l68 79-79 68-68-79Z" fill="none" stroke="#fff" stroke-width="2"/>
  <circle cx="902" cy="153" r="9" fill="#fff"/>
  <text x="46" y="230" font-family="Georgia, serif" font-size="132" font-style="italic"
        textLength="556" lengthAdjust="spacingAndGlyphs" fill="#fff">arpz<tspan fill="{BLACK}">-dev</tspan></text>
  <text x="48" y="276" fill="#fff" font-family="Arial, sans-serif" font-size="20">
    I design tiny web pages, build Discord bots and share the process.
  </text>
  <rect x="48" y="300" width="326" height="34" rx="17" fill="{BLACK}"/>
  <circle cx="69" cy="317" r="5" fill="#a5a5a5"/>
  <text x="86" y="322" fill="#fff" font-family="monospace" font-size="12"
        font-weight="700" letter-spacing="1.2">OPEN FOR NEW MINI-PROJECTS</text>
</svg>
"""


def social_card(label, icon, background):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="320" height="96" viewBox="0 0 320 96">
  <title>{escape(label)}</title>
  <path d="{background}" fill="{RED}"/>
  <rect x="22" y="15" width="276" height="58" rx="29" fill="{BLACK}"/>
  <g transform="translate(50 32)">{icon}</g>
  <text x="90" y="50" fill="#fff" font-family="monospace" font-size="18"
        letter-spacing="1.5">{escape(label.upper())}</text>
  <path d="M255 51l17-17m-13 0h13v13" fill="none" stroke="#fff"
        stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
"""


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--assets-dir", type=Path, default=Path("assets"))
    for name, label, _, _ in SOCIALS:
        parser.add_argument(f"--{name}", required=True, help=f"URL completa de {label}")
    args = parser.parse_args()

    for name, label, _, _ in SOCIALS:
        url = urlsplit(getattr(args, name))
        if url.scheme != "https" or not url.hostname:
            parser.error(f"--{name} necesita una URL https válida para {label}")

    args.assets_dir.mkdir(parents=True, exist_ok=True)
    (args.assets_dir / "profile-hero.svg").write_text(banner(date.today().year), encoding="utf-8")

    buttons = []
    for name, label, icon, background in SOCIALS:
        filename = f"social-{name}.svg"
        (args.assets_dir / filename).write_text(social_card(label, icon, background), encoding="utf-8")
        url = escape(getattr(args, name), quote=True)
        buttons.append(f'<a href="{url}"><img src="./assets/{filename}" alt="{escape(label)}" width="33.3%"></a>')

    print('<img src="./assets/profile-hero.svg" alt="arpz-dev — web pages, Discord bots and design" width="100%">')
    print("<br>")
    print("".join(buttons))
    print("<br>")


if __name__ == "__main__":
    main()
