#!/usr/bin/env python3
"""Print today's receipt: pull public GitHub stats, write receipt/data.json,
then render receipt/receipt.svg with the SHA-256 of that JSON printed on it.

Standard library only. Needs GITHUB_TOKEN; PROFILE_LOGIN defaults to Ritesh-Root.
If the API call fails the script exits non-zero and nothing is overwritten.
"""
import datetime as dt
import hashlib
import json
import os
import pathlib
import sys
import urllib.request
from xml.sax.saxutils import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "receipt"
LOGIN = os.environ.get("PROFILE_LOGIN", "Ritesh-Root")

QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    createdAt
    repositories(first: 100, after: $after, ownerAffiliations: OWNER,
                 privacy: PUBLIC, isFork: false,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes { name pushedAt primaryLanguage { name } }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def graphql(variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={
            "Authorization": f"bearer {os.environ['GITHUB_TOKEN']}",
            "Content-Type": "application/json",
            "User-Agent": "profile-receipt-printer",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors") or not body.get("data", {}).get("user"):
        sys.exit(f"GraphQL error: {body.get('errors')}")
    return body["data"]["user"]


def fetch():
    user = graphql({"login": LOGIN, "after": None})
    repos = list(user["repositories"]["nodes"])
    page = user["repositories"]["pageInfo"]
    while page["hasNextPage"]:
        more = graphql({"login": LOGIN, "after": page["endCursor"]})
        repos += more["repositories"]["nodes"]
        page = more["repositories"]["pageInfo"]
    return user, repos


def build_data(user, repos, today):
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [(d["date"], d["contributionCount"])
            for w in cal["weeks"] for d in w["contributionDays"]]
    busiest = max(days, key=lambda d: (d[1], d[0])) if days else ("", 0)

    langs = {}
    for r in repos:
        if r["primaryLanguage"]:
            n = r["primaryLanguage"]["name"]
            langs[n] = langs.get(n, 0) + 1
    top = max(langs.items(), key=lambda kv: (kv[1], kv[0])) if langs else ("-", 0)
    with_lang = sum(langs.values()) or 1

    shipped = next((r for r in repos if r["name"].lower() != LOGIN.lower()), None)
    created = dt.date.fromisoformat(user["createdAt"][:10])

    return {
        "as_of": today.isoformat(),
        "login": LOGIN,
        "days_on_github": (today - created).days,
        "public_original_repos": len(repos),
        "contributions_last_year": cal["totalContributions"],
        "active_days_last_year": sum(1 for _, c in days if c),
        "busiest_day": {"date": busiest[0], "contributions": busiest[1]},
        "top_language": {"name": top[0], "share_of_repos_pct": round(100 * top[1] / with_lang)},
        "last_shipped": {"repo": shipped["name"], "pushed_at": shipped["pushedAt"]} if shipped else None,
        "source": "GitHub GraphQL API via .github/workflows/receipt.yml",
    }


# ------------------------------------------------------------------ render

COLS = 42            # characters per printed line
FS = 13.5            # font size
CW = FS * 0.6        # monospace advance
LH = 19              # line height
PAD = 26             # paper side padding
PAPER_W = round(COLS * CW + 2 * PAD)
W = PAPER_W + 64     # canvas width (room for printer + shadow)
PX = (W - PAPER_W) / 2
SLOT_Y = 46          # where paper leaves the printer
MONO = ("ui-monospace,'SFMono-Regular','JetBrains Mono',Menlo,Consolas,"
        "'DejaVu Sans Mono','Liberation Mono',monospace")


def row(left, right="", fill="."):
    """Exactly COLS chars: left, leader, right."""
    gap = COLS - len(left) - len(right)
    if gap < 2:
        left = left[: COLS - len(right) - 3] + "~"
        gap = COLS - len(left) - len(right)
    leader = " " + fill * (gap - 2) + " " if fill != " " else " " * gap
    return left + leader + right


def center(s):
    return s.center(COLS)


def render(data, items, qr, digest):
    lines = []  # (kind, text)

    def add(kind, text=""):
        lines.append((kind, text))

    add("title", "RITESH-ROOT GENERAL STORE")
    add("italic", "AI that shows its receipts")
    add("plain", center("riteshhoon.online  ·  BTech CSE"))
    add("rule", "=" * COLS)
    d = dt.date.fromisoformat(data["as_of"])
    add("plain", row(f"RCPT #{data['days_on_github']:04d}", d.strftime("%d %b %Y").upper(), " "))
    add("plain", row("CASHIER", "RITESH (HUMAN)", " "))
    add("rule", "-" * COLS)
    add("dim", row("QTY ITEM", "WHERE", " "))
    for it in items:
        add("plain", row(f" 1  {it['repo']}", it["tag"]))
    add("rule", "-" * COLS)
    add("plain", row("PUBLIC REPOS (ORIGINAL)", str(data["public_original_repos"])))
    add("plain", row("CONTRIBUTIONS, 365 DAYS", f"{data['contributions_last_year']:,}"))
    add("plain", row("ACTIVE DAYS, 365 DAYS", str(data["active_days_last_year"])))
    bd = data["busiest_day"]
    if bd["date"]:
        when = dt.date.fromisoformat(bd["date"]).strftime("%d %b").upper()
        add("plain", row("BUSIEST DAY", f"{bd['contributions']} ON {when}"))
    tl = data["top_language"]
    add("plain", row("TOP LANGUAGE", f"{tl['name'].upper()} {tl['share_of_repos_pct']}%"))
    if data["last_shipped"]:
        add("plain", row("LAST SHIPPED", data["last_shipped"]["repo"]))
    add("rule", "-" * COLS)
    add("plain", row("SUBTOTAL", "many late nights", " "))
    add("plain", row("GST @ 18%", "filed by TaxEasy", " "))
    add("bold", row("TOTAL", "1 DEMO THAT RUNS", " "))
    add("rule", "=" * COLS)
    add("plain", row("PAID BY", "CHAI, UPI", " "))
    add("plain", row("CHANGE", "0.00", " "))
    add("qr", "")
    add("dim", center("SHA-256 OF receipt/data.json"))
    add("hash", center(digest[:32]))
    add("hash", center(digest[32:]))
    add("gap", "")
    add("bold", center("NO CLAIM WITHOUT A RECEIPT"))
    add("plain", center("THANK YOU  ·  PLEASE COME AGAIN"))
    add("dim", center("*** CUSTOMER COPY ***"))

    QR_SCALE = 3.2
    qr_units = qr["size"] + 2          # 1-module quiet zone on paper
    qr_px = qr_units * QR_SCALE

    y = 4                            # inside paper coordinates
    body, stamp_y = [], 0
    for kind, text in lines:
        if kind == "title":
            y += 30
            body.append(f'<text x="{PAPER_W/2}" y="{y}" text-anchor="middle" class="t">{escape(text)}</text>')
            y += 6
            continue
        if kind == "italic":
            y += 22
            body.append(f'<text x="{PAPER_W/2}" y="{y}" text-anchor="middle" class="i">{escape(text)}</text>')
            continue
        if kind == "gap":
            y += LH * 0.6
            continue
        if kind == "qr":
            y += 14
            qx = PAD
            body.append(
                f'<g transform="translate({qx} {y}) scale({QR_SCALE})">'
                f'<rect width="{qr_units}" height="{qr_units}" fill="#fffdf6"/>'
                f'<path transform="translate(1 1)" d="{qr["path"]}" class="ink"/></g>')
            lx = qx + qr_px + 16
            body.append(f'<text x="{lx}" y="{y + 26}" class="b">SCAN FOR THE</text>')
            body.append(f'<text x="{lx}" y="{y + 26 + LH}" class="b">FULL PORTFOLIO</text>')
            body.append(f'<text x="{lx}" y="{y + 26 + 2.3*LH}" class="d">reprinted daily by</text>')
            body.append(f'<text x="{lx}" y="{y + 26 + 3.3*LH}" class="d">GitHub Actions</text>')
            y += max(qr_px, 26 + 3.3 * LH + 6) + 8
            continue
        y += LH
        cls = {"plain": "p", "rule": "r", "dim": "d", "bold": "b", "hash": "h"}[kind]
        if text.startswith("PAID BY"):
            stamp_y = y
        body.append(
            f'<text x="{PAD}" y="{y}" class="{cls}" textLength="{COLS*CW:.1f}" '
            f'lengthAdjust="spacing">{escape(text)}</text>')

    paper_h = round(y + 30)
    teeth = 14
    tw = PAPER_W / teeth
    # torn edge: zigzag right-to-left along the bottom
    pts =[f"L{PAPER_W - i*tw/2:.1f} {paper_h + (7 if i % 2 else 0)}" for i in range(2*teeth + 1)]
    paper_path = f"M0 0 H{PAPER_W} V{paper_h} " + " ".join(pts) + " Z"

    H = SLOT_Y + paper_h + 30
    feed = paper_h + 10
    stamp_cx, stamp_cy = PAPER_W / 2 + 6, stamp_y + 4

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" xml:space="preserve" role="img" aria-labelledby="ttl desc">
<title id="ttl">Ritesh-Root: a receipt for my GitHub</title>
<desc id="desc">An animated thermal receipt. {data['public_original_repos']} public original repos, {data['contributions_last_year']} contributions in the last year, active on {data['active_days_last_year']} days, busiest day {data['busiest_day']['contributions']} contributions, top language {tl['name']}. SHA-256 of receipt/data.json: {digest}.</desc>
<defs>
  <linearGradient id="paper" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fdfaf2"/><stop offset="1" stop-color="#f1e9d6"/>
  </linearGradient>
  <linearGradient id="body" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#3a3a40"/><stop offset="1" stop-color="#1e1e22"/>
  </linearGradient>
  <filter id="shadow" x="-10%" y="-5%" width="120%" height="115%">
    <feDropShadow dx="0" dy="6" stdDeviation="7" flood-color="#000" flood-opacity=".28"/>
  </filter>
  <filter id="ink" x="-20%" y="-20%" width="140%" height="140%">
    <feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7" result="n"/>
    <feDisplacementMap in="SourceGraphic" in2="n" scale="1.8"/>
  </filter>
  <clipPath id="below-slot"><rect x="0" y="{SLOT_Y}" width="{W}" height="{H}"/></clipPath>
</defs>
<style>
  text {{ font-family: {MONO}; font-size: {FS}px; fill: #2a2622; white-space: pre; }}
  .t {{ font-size: 19px; font-weight: 800; letter-spacing: .5px; }}
  .i {{ font-style: italic; font-size: 14px; fill: #6b5f4f; }}
  .b {{ font-weight: 700; }}
  .d {{ fill: #8a7d6b; font-size: 12px; }}
  .r {{ fill: #b9ad97; }}
  .h {{ fill: #4b4339; letter-spacing: .3px; }}
  .ink {{ fill: #2a2622; }}
  .feed {{ animation: feed 3.4s steps(34, end) .5s both; }}
  .stamp {{ transform-box: fill-box; transform-origin: center; opacity: 0;
           animation: thunk .28s cubic-bezier(.3,1.6,.6,1) 4.2s forwards; }}
  .led {{ animation: blink .25s steps(2) .5s 14, settle .01s linear 4s forwards; }}
  @keyframes feed {{ from {{ transform: translateY(-{feed}px); }} to {{ transform: translateY(0); }} }}
  @keyframes thunk {{ from {{ opacity: 0; transform: scale(1.9); }} to {{ opacity: .88; transform: scale(1); }} }}
  @keyframes blink {{ from {{ fill: #34d399; }} to {{ fill: #14532d; }} }}
  @keyframes settle {{ to {{ fill: #34d399; }} }}
  @media (prefers-reduced-motion: reduce) {{
    .feed, .led {{ animation: none; }}
    .stamp {{ animation: none; opacity: .88; }}
  }}
</style>
<g clip-path="url(#below-slot)">
  <g class="feed">
    <g transform="translate({PX} {SLOT_Y - 4})">
      <path d="{paper_path}" fill="url(#paper)" filter="url(#shadow)"/>
      {chr(10).join("      " + b for b in body).lstrip()}
      <g transform="translate({stamp_cx} {stamp_cy}) rotate(-11)">
        <g class="stamp" filter="url(#ink)">
          <rect x="-86" y="-27" width="172" height="54" rx="7" fill="none" stroke="#c0392b" stroke-width="3.2"/>
          <rect x="-80" y="-21" width="160" height="42" rx="4" fill="none" stroke="#c0392b" stroke-width="1.2"/>
          <text x="0" y="3" text-anchor="middle" style="font-size:22px;font-weight:900;fill:#c0392b;letter-spacing:3px">VERIFIED</text>
          <text x="0" y="17" text-anchor="middle" style="font-size:8.5px;font-weight:700;fill:#c0392b;letter-spacing:1.5px">BY GITHUB API · {d.strftime('%d.%m.%y')}</text>
        </g>
      </g>
    </g>
  </g>
</g>
<rect x="{PX - 22}" y="6" width="{PAPER_W + 44}" height="{SLOT_Y - 6}" rx="12" fill="url(#body)"/>
<rect x="{PX - 8}" y="{SLOT_Y - 9}" width="{PAPER_W + 16}" height="5" rx="2.5" fill="#0b0b0d"/>
<circle cx="{PX}" cy="22" r="4" fill="#34d399" class="led"/>
<text x="{PX + 14}" y="26" style="font-size:10.5px;fill:#a1a1aa;letter-spacing:2px">PRINTING YOUR VISIT</text>
<text x="{PX + PAPER_W}" y="26" text-anchor="end" style="font-size:10.5px;fill:#71717a;letter-spacing:1px">{escape(LOGIN.upper())}·TM-42</text>
</svg>
'''


def main():
    today = dt.datetime.now(dt.timezone.utc).date()
    user, repos = fetch()
    data = build_data(user, repos, today)
    raw = (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()
    digest = hashlib.sha256(raw).hexdigest()
    items = json.loads((OUT / "items.json").read_text())
    qr = json.loads((OUT / "qr.json").read_text())
    svg = render(data, items, qr, digest)
    (OUT / "data.json").write_bytes(raw)
    (OUT / "receipt.svg").write_text(svg)
    print(f"printed receipt for {LOGIN}: sha256 {digest}")


if __name__ == "__main__":
    main()
