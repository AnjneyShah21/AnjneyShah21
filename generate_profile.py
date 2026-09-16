#!/usr/bin/env python3
"""
Generate the terminal-style GitHub profile SVG.

Edit PROFILE below for your own details. The GitHub Action runs this script
automatically and refreshes the public GitHub statistics.
"""
from pathlib import Path
import base64, html, os, urllib.request, json
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
OUT = ROOT / "profile.svg"

PROFILE = {
    "username": "AnjneyShah21",
    "host": "RV College of Engineering",
    "kernel": "Computer Science • 2029",
    "ide": "VS Code",
    "programming": "C, Java, Python",
    "computer": "HTML, CSS, Git, GitHub",
    "real": "English, Kannada",
    "software": "AI/ML, Computer Vision, Hackathons",
    "hardware": "Arduino, ESP32, Sensors, IoT",
    "github": "github.com/AnjneyShah21",
    "linkedin": "Add your LinkedIn",
    "discord": "AnjneyShah21",
    "tagline": "Build . Break . Learn . Repeat _",
}

# Terminal palette — intentionally close to the screenshot style.
BG = "#10161d"
PANEL = "#171e26"
WHITE = "#d8dee9"
MUTED = "#718096"
BLUE = "#69b7ff"
CYAN = "#49d7d0"
ORANGE = "#ff9d35"
GREEN = "#35d07f"
PURPLE = "#c792ea"

def esc(x):
    return html.escape(str(x))

def text(x, y, value, size=15, color=WHITE, weight="400", anchor="start"):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="JetBrains Mono,Consolas,monospace" font-size="{size}px" font-weight="{weight}" text-anchor="{anchor}">{esc(value)}</text>'

def line(x1, y, x2):
    return f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="#2a3542" stroke-width="1"/>'

def stat_row(y, label, value, color=BLUE):
    dots = "." * max(8, 30 - len(label))
    return (
        text(760, y, label, 15, ORANGE) +
        text(900, y, dots, 15, MUTED) +
        text(1120, y, value, 15, color)
    )

def get_github_stats():
    token = os.getenv("GITHUB_TOKEN", "")
    query = """
    query($login:String!) {
      user(login:$login) {
        repositories(ownerAffiliations:OWNER, first:100, privacy:PUBLIC) {
          totalCount
          nodes { stargazerCount }
        }
        followers { totalCount }
        contributionsCollection {
          contributionCalendar { totalContributions }
          totalCommitContributions
        }
      }
    }
    """
    payload = json.dumps({"query": query, "variables": {"login": PROFILE["username"]}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "AnjneyShah21-profile-generator",
            **({"Authorization": f"bearer {token}"} if token else {}),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            data = json.loads(r.read().decode())
        u = data["data"]["user"]
        stars = sum(x["stargazerCount"] for x in u["repositories"]["nodes"])
        return {
            "repos": u["repositories"]["totalCount"],
            "commits": u["contributionsCollection"]["totalCommitContributions"],
            "stars": stars,
            "followers": u["followers"]["totalCount"],
            "contributions": u["contributionsCollection"]["contributionCalendar"]["totalContributions"],
        }
    except Exception:
        return {"repos": "—", "commits": "—", "stars": "—", "followers": "—", "contributions": "—"}

def make_ascii():
    chars = "@%#*+=-:. "
    img = Image.open(ASSETS / "profile.jpg").convert("L")
    w, h = img.size
    img = img.crop((max(0, int(w*0.04)), 0, min(w, int(w*0.96)), h))
    target_w = 58
    target_h = max(20, int(img.height / img.width * target_w * 0.48))
    img = ImageOps.autocontrast(img.resize((target_w, target_h)))
    rows = []
    for y in range(img.height):
        row = []
        for x in range(img.width):
            p = img.getpixel((x, y))
            idx = min(len(chars)-1, int(p / 256 * len(chars)))
            row.append(chars[idx])
        rows.append("".join(row).rstrip())
    return rows

def make_svg(stats):
    W, H = 1500, 900
    rows = make_ascii()
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        f'<rect width="{W}" height="{H}" fill="{BG}"/>',
        f'<rect x="18" y="18" width="{W-36}" height="{H-36}" rx="13" fill="none" stroke="#33404f"/>',
        f'<rect x="24" y="58" width="{W-48}" height="{H-82}" rx="20" fill="{PANEL}"/>',
        # top accent
        '<rect x="24" y="18" width="115" height="3" fill="#ff6b61"/>',
    ]
    # ASCII portrait
    start_x, start_y, step = 55, 105, 10.0
    for i, row in enumerate(rows):
        if row:
            svg.append(text(start_x, start_y + i*step, row, 9, BLUE))
    # right panel
    x = 705
    svg.append(text(x, 95, f'{PROFILE["username"]}@github', 22, CYAN, "700"))
    svg.append(text(x+270, 95, "─"*62, 15, MUTED))
    svg.append(stat_row(135, "OS", "Windows 11"))
    svg.append(stat_row(160, "Uptime", "RVCE • 3rd Semester"))
    svg.append(stat_row(185, "Host", PROFILE["host"]))
    svg.append(stat_row(210, "Kernel", PROFILE["kernel"]))
    svg.append(stat_row(235, "IDE", PROFILE["ide"]))
    svg.append(line(x, 260, 1450))
    svg.append(text(x, 292, "⌘  Languages.Programming", 15, ORANGE))
    svg.append(text(1020, 292, "......", 15, MUTED))
    svg.append(text(1120, 292, PROFILE["programming"], 15, BLUE))
    svg.append(text(x, 320, "⌘  Languages.Computer", 15, ORANGE))
    svg.append(text(1020, 320, "........", 15, MUTED))
    svg.append(text(1120, 320, PROFILE["computer"], 15, BLUE))
    svg.append(text(x, 348, "◎  Languages.Real", 15, ORANGE))
    svg.append(text(1020, 348, "............", 15, MUTED))
    svg.append(text(1120, 348, PROFILE["real"], 15, BLUE))
    svg.append(line(x, 373, 1450))
    svg.append(text(x, 405, "⌁  Hobbies.Software", 15, ORANGE))
    svg.append(text(1020, 405, ".........", 15, MUTED))
    svg.append(text(1120, 405, PROFILE["software"], 15, BLUE))
    svg.append(text(x, 433, "▣  Hobbies.Hardware", 15, ORANGE))
    svg.append(text(1020, 433, ".........", 15, MUTED))
    svg.append(text(1120, 433, PROFILE["hardware"], 15, BLUE))
    svg.append(line(x, 458, 1450))
    svg.append(text(x, 490, "─ Contact", 15, CYAN, "700"))
    svg.append(text(x, 520, "GitHub", 15, ORANGE))
    svg.append(text(900, 520, ".................", 15, MUTED))
    svg.append(text(1120, 520, PROFILE["github"], 15, BLUE))
    svg.append(text(x, 548, "LinkedIn", 15, ORANGE))
    svg.append(text(900, 548, ".................", 15, MUTED))
    svg.append(text(1120, 548, PROFILE["linkedin"], 15, BLUE))
    svg.append(text(x, 576, "Discord", 15, ORANGE))
    svg.append(text(900, 576, "...................", 15, MUTED))
    svg.append(text(1120, 576, PROFILE["discord"], 15, BLUE))
    svg.append(line(x, 603, 1450))
    svg.append(text(x, 635, "─ GitHub Stats", 15, CYAN, "700"))
    svg.append(stat_row(665, "Repos", str(stats["repos"])))
    svg.append(stat_row(693, "Commits", str(stats["commits"])))
    svg.append(stat_row(721, "Stars", str(stats["stars"])))
    svg.append(stat_row(749, "Followers", str(stats["followers"])))
    svg.append(stat_row(777, "Contributions", str(stats["contributions"]), GREEN))
    svg.append(text(55, 860, "➜  " + PROFILE["tagline"], 17, GREEN, "700"))
    svg.append("</svg>")
    return "\n".join(svg)

if __name__ == "__main__":
    OUT.write_text(make_svg(get_github_stats()), encoding="utf-8")
    print(f"Wrote {OUT}")
