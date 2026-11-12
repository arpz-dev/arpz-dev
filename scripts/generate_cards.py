import json
import math
import os
import urllib.request
from datetime import datetime

USER = os.environ.get("GH_USER", "arpz-dev")
TOKEN = os.environ["GITHUB_TOKEN"]

FONT_SERIF = "Georgia, 'Times New Roman', serif"
FONT_MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
BG, RED, WHITE, GREY = "#0A0A0A", "#E10600", "#FFFFFF", "#8A8A8A"
LEVELS = ["#262626", "#5A0F0C", "#99120E", "#D41A12", "#FF2A1F"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { contributionCount date weekday } }
      }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as response:
        data = json.load(response)
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def wrap(width, height, body):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">'
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="22" fill="{BG}" '
        f'stroke="{RED}" stroke-opacity="0.55" stroke-width="2"/>{body}</svg>'
    )


def heatmap_svg(weeks):
    width, pad, top = 880, 36, 96
    days = [d for w in weeks for d in w["contributionDays"]]
    peak = max((d["contributionCount"] for d in days), default=1) or 1
    pitch = (width - 2 * pad) / len(weeks)
    radius = pitch * 0.36
    height = int(top + 7 * pitch + pad)

    parts = [
        f'<text x="{pad}" y="56" font-family="{FONT_SERIF}" font-size="30" font-style="italic" fill="{WHITE}">'
        f'Every day, <tspan fill="{RED}">in red</tspan></text>',
        f'<text x="{width - pad}" y="52" text-anchor="end" font-family="{FONT_MONO}" font-size="10" '
        f'letter-spacing="2" fill="{GREY}">UPDATED DAILY</text>',
    ]

    i = 0
    for col, week in enumerate(weeks):
        for day in week["contributionDays"]:
            count = day["contributionCount"]
            level = 0 if count == 0 else max(1, min(4, math.ceil(4 * count / peak)))
            cx = pad + col * pitch + pitch / 2
            cy = top + day["weekday"] * pitch + pitch / 2
            if level >= 3:
                begin = (i % 25) * 0.12
                parts.append(
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.1f}" fill="{LEVELS[level]}">'
                    f'<animate attributeName="opacity" values="1;0.5;1" dur="3s" begin="{begin:.2f}s" repeatCount="indefinite"/>'
                    f'</circle>'
                )
                i += 1
            else:
                parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{radius:.1f}" fill="{LEVELS[level]}"/>')

    return wrap(width, height, "".join(parts))


def contributions_svg(calendar):
    width, height, pad = 880, 270, 36
    by_month = {}
    for week in calendar["weeks"]:
        for day in week["contributionDays"]:
            key = day["date"][:7]
            by_month[key] = by_month.get(key, 0) + day["contributionCount"]

    months = sorted(by_month)[-12:]
    values = [by_month[m] for m in months]
    peak = max(values) or 1
    base, max_h = 232, 76
    slot = (width - 2 * pad) / len(months)
    bar_w = slot * 0.62

    parts = [
        f'<text x="{pad}" y="52" font-family="{FONT_MONO}" font-size="10" letter-spacing="2" '
        f'fill="{GREY}">THE LAST 12 MONTHS ON GITHUB</text>',
        f'<text x="{pad}" y="124" font-family="{FONT_SERIF}" font-size="64" font-style="italic" fill="{WHITE}">'
        f'{calendar["totalContributions"]:,} <tspan fill="{RED}">contributions</tspan></text>',
    ]

    for i, (month, value) in enumerate(zip(months, values)):
        h = max(3, round(max_h * value / peak))
        x = pad + i * slot + (slot - bar_w) / 2
        color = RED if value == peak else WHITE
        label = datetime.strptime(month + "-01", "%Y-%m-%d").strftime("%b").upper()
        delay = i * 0.06
        parts.append(
            f'<rect x="{x:.1f}" y="{base - h}" width="{bar_w:.1f}" height="{h}" rx="3" fill="{color}">'
            f'<animate attributeName="height" from="0" to="{h}" dur="0.8s" begin="{delay:.2f}s" fill="freeze"/>'
            f'<animate attributeName="y" from="{base}" to="{base - h}" dur="0.8s" begin="{delay:.2f}s" fill="freeze"/>'
            f'</rect>'
        )
        parts.append(
            f'<text x="{x + bar_w / 2:.1f}" y="{base + 20}" text-anchor="middle" '
            f'font-family="{FONT_MONO}" font-size="10" fill="{GREY}">{label}</text>'
        )

    return wrap(width, height, "".join(parts))


def main():
    calendar = fetch()
    os.makedirs("assets", exist_ok=True)
    with open("assets/daily-heatmap.svg", "w", encoding="utf-8") as f:
        f.write(heatmap_svg(calendar["weeks"]))
    with open("assets/contributions-card.svg", "w", encoding="utf-8") as f:
        f.write(contributions_svg(calendar))


if __name__ == "__main__":
    main()
