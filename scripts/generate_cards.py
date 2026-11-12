import json
import math
import os
import re
import urllib.parse
import urllib.request
from datetime import datetime
from xml.sax.saxutils import escape

# ---------- CONFIG ----------
USER = os.environ.get("GH_USER", "arpz-dev")
INSTAGRAM = "YOUR_INSTAGRAM"
TWITTER = "YOUR_TWITTER"
FEATURED = []  # e.g. ["repo-one", "repo-two"]; empty = top 4 by stars
TOKEN = os.environ["GITHUB_TOKEN"]

RED, DARK_RED, BLACK, WHITE, GREY = "#E10600", "#9B1510", "#0A0A0A", "#FFFFFF", "#8A8A8A"
SERIF = "Georgia, 'Times New Roman', serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"
LEVELS = ["#262626", "#5C0F0B", "#9B1510", "#D41A12", "#FF3B30"]
LANG_COLORS = [RED, WHITE, DARK_RED, GREY, "#FF6A5F", "#5A5A5A", "#FFB3AE", "#333333"]

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

ICONS = {
    "instagram": '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/>'
                 '<circle cx="17.3" cy="6.7" r="0.8" fill="{c}"/>',
    "discord": '<path fill="{c}" stroke="none" fill-rule="evenodd" d="M5.2 5.6C8.6 3.4 15.4 3.4 18.8 5.6'
               'C20.8 9 21.8 13 21.6 17.4C19.6 19 17.6 19.8 15.8 20L14.6 18.2C13.1 18.6 10.9 18.6 9.4 18.2'
               'L8.2 20C6.4 19.8 4.4 19 2.4 17.4C2.2 13 3.2 9 5.2 5.6ZM7 12a1.9 2.2 0 1 0 3.8 0a1.9 2.2 0 1 0 -3.8 0Z'
               'M13.2 12a1.9 2.2 0 1 0 3.8 0a1.9 2.2 0 1 0 -3.8 0Z"/>',
    "x": '<path d="M5 4L19 20M19 4L5 20"/>',
    "star": '<path fill="{c}" stroke="none" d="M12 2.5l2.9 6.2 6.8.8-5 4.7 1.3 6.7-6-3.3-6 3.3 1.3-6.7-5-4.7 6.8-.8z"/>',
    "repo": '<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 7h6M9 11h6"/>',
    "users": '<circle cx="9" cy="8" r="3.5"/><path d="M2.5 20c0-3.6 3-6 6.5-6s6.5 2.4 6.5 6"/>'
             '<circle cx="17.5" cy="9" r="2.5"/><path d="M17.5 14c2.5 0 4.5 1.8 4.5 4.5"/>',
    "commit": '<circle cx="12" cy="12" r="4"/><path d="M2 12h6M16 12h6"/>',
}


def api(url, payload=None):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode() if payload else None,
        headers={
            "Authorization": f"bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req) as response:
        return json.load(response)


def save(name, content):
    os.makedirs("assets", exist_ok=True)
    with open(f"assets/{name}", "w", encoding="utf-8") as f:
        f.write(content)


def svg(w, h, body, bg, rx=24):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect width="{w}" height="{h}" rx="{rx}" fill="{bg}"/>{body}</svg>'
    )


def icon(name, x, y, size, color, extra=""):
    inner = ICONS[name].replace("{c}", color)
    return (
        f'<g transform="translate({x} {y}) scale({size / 24})" fill="none" stroke="{color}" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{inner}{extra}</g>'
    )


# ---------- BLOCK 1: hero + social tiles + stat tiles ----------
def hero_svg():
    head, dash, tail = USER.partition("-")
    body = f"""
  <g font-family="{MONO}" font-size="12" letter-spacing="2" fill="{WHITE}">
    <text x="40" y="52">(01) WEB PAGES</text>
    <text x="220" y="52">(02) DISCORD BOTS</text>
    <text x="436" y="52">(03) DESIGN LAB</text>
    <text x="840" y="52" text-anchor="end">&#169; {datetime.now().year}</text>
  </g>
  <line x1="40" y1="68" x2="840" y2="68" stroke="{WHITE}" stroke-opacity="0.5"/>
  <text x="440" y="200" text-anchor="middle" font-family="{SERIF}" font-size="150" font-style="italic" fill="{WHITE}">
    <animate attributeName="opacity" from="0" to="1" dur="1s" fill="freeze"/>{escape(head)}<tspan fill="{BLACK}">{escape(dash + tail)}</tspan>
  </text>
"""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" width="880" height="250" viewBox="0 0 880 250">'
        f'<path d="M0 28A28 28 0 0 1 28 0H852A28 28 0 0 1 880 28V250H0Z" fill="{RED}"/>{body}</svg>'
    )


def button_svg(name, icon_name, label, position):
    w, h, m, r, ph = 294, 88, 20, 28, 52
    shapes = {
        "left": f"M0 0H{w}V{h}H{r}A{r} {r} 0 0 1 0 {h - r}Z",
        "middle": f"M0 0H{w}V{h}H0Z",
        "right": f"M0 0H{w}V{h - r}A{r} {r} 0 0 1 {w - r} {h}H0Z",
    }
    cy = 18 + ph / 2
    body = (
        f'<path d="{shapes[position]}" fill="{RED}"/>'
        f'<rect x="{m}" y="18" width="{w - 2 * m}" height="{ph}" rx="{ph / 2}" fill="{BLACK}"/>'
        + icon(icon_name, m + 24, cy - 13, 26, WHITE)
        + f'<text x="{m + 64}" y="{cy + 5}" font-family="{MONO}" font-size="15" letter-spacing="2" fill="{WHITE}">{label}</text>'
        + f'<g transform="translate({w - m - 42} {cy - 7})"><g fill="none" stroke="{WHITE}" stroke-width="2.5" stroke-linecap="round">'
        + '<animateTransform attributeName="transform" type="translate" values="0 0;3 -3;0 0" dur="2s" repeatCount="indefinite"/>'
        + '<path d="M0 14L14 0M3 0H14V11"/></g></g>'
    )
    save(name, f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{body}</svg>')


# ---------- Languages ----------
def languages_svg(langs):
    w, pad = 880, 36
    bar_w = w - 2 * pad
    parts = [
        f'<text x="{pad}" y="56" font-family="{SERIF}" font-size="30" font-style="italic" fill="{WHITE}">'
        f'Languages, <tspan fill="{RED}">in the wild</tspan></text>',
        f'<text x="{w - pad}" y="52" text-anchor="end" font-family="{MONO}" font-size="10" letter-spacing="2" fill="{GREY}">ALL PUBLIC REPOS</text>',
        f'<clipPath id="bar"><rect x="{pad}" y="82" width="{bar_w}" height="24" rx="12"/></clipPath><g clip-path="url(#bar)">',
    ]
    x = pad
    for i, (lang, pct) in enumerate(langs):
        sw = bar_w * pct / 100
        parts.append(
            f'<rect x="{x:.1f}" y="82" width="{sw:.1f}" height="24" fill="{LANG_COLORS[i % len(LANG_COLORS)]}">'
            f'<animate attributeName="width" from="0" to="{sw:.1f}" dur="0.8s" begin="{i * 0.15:.2f}s" fill="freeze"/></rect>'
        )
        x += sw
    parts.append("</g>")
    for i, (lang, pct) in enumerate(langs[:6]):
        lx, ly = pad + (i % 3) * 270, 144 + (i // 3) * 28
        parts.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>')
        parts.append(
            f'<text x="{lx + 18}" y="{ly}" font-family="{MONO}" font-size="13" fill="{WHITE}">'
            f'{escape(lang)} <tspan fill="{GREY}">{pct:.1f}%</tspan></text>'
        )
    return svg(w, 204, "".join(parts), BLACK)


# ---------- Contributions (red squares) ----------
def contributions_svg(calendar):
    w, pad, top = 880, 36, 150
    weeks = calendar["weeks"]
    pitch = (w - 2 * pad) / len(weeks)
    side = pitch * 0.78
    days = [d for wk in weeks for d in wk["contributionDays"]]
    peak = max((d["contributionCount"] for d in days), default=1) or 1
    h = int(top + 7 * pitch + 56)
    parts = [
        f'<text x="{pad}" y="48" font-family="{MONO}" font-size="10" letter-spacing="2" fill="{GREY}">THE LAST 12 MONTHS ON GITHUB</text>',
        f'<text x="{pad}" y="112" font-family="{SERIF}" font-size="56" font-style="italic" fill="{WHITE}">'
        f'{calendar["totalContributions"]:,} <tspan fill="{RED}">contributions</tspan></text>',
    ]
    for col, wk in enumerate(weeks):
        for d in wk["contributionDays"]:
            count = d["contributionCount"]
            level = 0 if count == 0 else max(1, min(4, math.ceil(4 * count / peak)))
            x = pad + col * pitch + (pitch - side) / 2
            y = top + d["weekday"] * pitch + (pitch - side) / 2
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{side:.1f}" height="{side:.1f}" rx="3" fill="{LEVELS[level]}" opacity="0">'
                f'<animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{col * 0.025:.2f}s" fill="freeze"/></rect>'
            )
    lx, ly = w - pad - 190, int(top + 7 * pitch + 24)
    parts.append(f'<text x="{lx}" y="{ly + 10}" font-family="{MONO}" font-size="10" fill="{GREY}">LESS</text>')
    for i, color in enumerate(LEVELS):
        parts.append(f'<rect x="{lx + 40 + i * 18}" y="{ly}" width="12" height="12" rx="3" fill="{color}"/>')
    parts.append(f'<text x="{lx + 136}" y="{ly + 10}" font-family="{MONO}" font-size="10" fill="{GREY}">MORE</text>')
    return svg(w, h, "".join(parts), BLACK)


# ---------- README blocks ----------
def replace_block(text, tag, content):
    pattern = re.compile(rf"(<!--{tag}:START-->)(.*?)(<!--{tag}:END-->)", re.S)
    return pattern.sub(lambda m: f"{m.group(1)}\n{content}\n{m.group(3)}", text)


def main():
    profile = api(f"https://api.github.com/users/{USER}")
    repos = [
        r for r in api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
        if not r["fork"] and r["name"] != USER
    ]
    calendar = api(
        "https://api.github.com/graphql", {"query": QUERY, "variables": {"login": USER}}
    )["data"]["user"]["contributionsCollection"]["contributionCalendar"]

    stars = sum(r["stargazers_count"] for r in repos)

    # Block 1
    save("hero.svg", hero_svg())
    button_svg("button-discord.svg", "discord", "DISCORD", "left")
    button_svg("button-instagram.svg", "instagram", "INSTAGRAM", "middle")
    button_svg("button-twitter.svg", "x", "TWITTER", "right")

    # Languages
    totals = {}
    for r in repos:
        for lang, n in api(r["languages_url"]).items():
            totals[lang] = totals.get(lang, 0) + n
    grand = sum(totals.values())
    ranked = sorted(totals.items(), key=lambda kv: kv[1], reverse=True)
    langs = [(k, v * 100 / grand) for k, v in ranked[:7]] if grand else [("No data yet", 100.0)]
    rest = sum(v for _, v in ranked[7:])
    if grand and rest:
        langs.append(("Other", rest * 100 / grand))
    save("languages.svg", languages_svg(langs))
    save("contributions.svg", contributions_svg(calendar))

    # README: clickable language chips + featured repos
    if not os.path.exists("README.md"):
        return
    with open("README.md", encoding="utf-8") as f:
        readme = f.read()

    chips = []
    for lang, pct in langs:
        if lang in ("Other", "No data yet"):
            continue
        label = urllib.parse.quote(lang.replace("-", "--").replace("_", "__"))
        url = f"https://github.com/{USER}?tab=repositories&language={urllib.parse.quote(lang)}"
        chips.append(
            f'<a href="{url}"><img src="https://img.shields.io/badge/{label}-{pct:.1f}%25-E10600'
            f'?style=for-the-badge&labelColor=0A0A0A" alt="{escape(lang)}"></a>'
        )
    readme = replace_block(readme, "LANGS", "\n".join(chips))

    by_name = {r["name"]: r for r in repos}
    picked = [by_name[n] for n in FEATURED if n in by_name] or sorted(
        repos, key=lambda r: (r["stargazers_count"], r["pushed_at"]), reverse=True
    )[:4]
    cards = [
        f'<a href="{r["html_url"]}"><img width="48%" alt="{escape(r["name"])}" '
        f'src="https://github-readme-stats.vercel.app/api/pin/?username={USER}&repo={r["name"]}'
        f'&bg_color=0A0A0A&title_color=E10600&text_color=FFFFFF&icon_color=E10600&border_color=E10600"></a>'
        for r in picked
    ]
    readme = replace_block(readme, "REPOS", "\n".join(cards))

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(readme)


if __name__ == "__main__":
    main()
