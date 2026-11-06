"""Render the last 52 weeks of contributions as an ECG strip: one heartbeat per week."""
import datetime as dt
from xml.sax.saxutils import escape

MONO = ("ui-monospace,'SFMono-Regular','JetBrains Mono',Menlo,Consolas,"
        "'DejaVu Sans Mono','Liberation Mono',monospace")
W, H = 840, 272
X0, X1 = 34, 806
BASE, AMP_MAX = 198, 104
DRAW, START = 5.5, .6          # seconds: needle sweep, delay before it starts


def _beats(weeks):
    """Path commands, the polyline we measure, and each week's R-peak point."""
    cell = (X1 - X0) / len(weeks)
    peak = max(w["contributions"] for w in weeks) or 1
    cmds, pts, tops = [f"M{X0 - 18} {BASE}"], [(X0 - 18, BASE)], []
    for i, w in enumerate(weeks):
        x, v = X0 + i * cell, w["contributions"]
        if v <= 0:
            cmds.append(f"L{x + cell:.1f} {BASE}")
            pts.append((x + cell, BASE))
            tops.append((x + cell * .46, BASE))
            continue
        a = max(9, AMP_MAX * (v / peak) ** .5)
        p = lambda fx, fy: (x + cell * fx, BASE - a * fy)   # noqa: E731
        P0, P1, P2 = p(.14, 0), p(.22, .18), p(.30, 0)        # P wave
        Q, R, S, J = p(.38, -.07), p(.46, 1), p(.54, -.2), p(.60, 0)
        T1, T2, E = p(.73, .3), p(.86, 0), p(1, 0)            # T wave
        cmds.append(f"L{P0[0]:.1f} {P0[1]:.1f} Q{P1[0]:.1f} {P1[1]:.1f} {P2[0]:.1f} {P2[1]:.1f}")
        cmds.append(" ".join(f"L{px:.1f} {py:.1f}" for px, py in (Q, R, S, J)))
        cmds.append(f"Q{T1[0]:.1f} {T1[1]:.1f} {T2[0]:.1f} {T2[1]:.1f} L{E[0]:.1f} {E[1]:.1f}")
        pts += [P0, P2, Q, R, S, J, T2, E]
        tops.append(R)
    return " ".join(cmds), pts, tops, cell


def render_pulse(data, login):
    weeks = data["weeks"]
    if not weeks:
        return ""
    trace, pts, tops, cell = _beats(weeks)
    peak = max(w["contributions"] for w in weeks)

    cum, total = [0.0], 0.0
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        total += ((bx - ax) ** 2 + (by - ay) ** 2) ** .5
        cum.append(total)

    def reach(x):  # fraction of the sweep when the needle gets to x
        return next((c / total for (px, _), c in zip(pts, cum) if px >= x), 1.0)

    # label the biggest weeks, skipping any label that would collide
    boxes, labels = [], []
    for i in sorted(range(len(weeks)), key=lambda i: -weeks[i]["contributions"]):
        w = weeks[i]
        if len(labels) == 5 or w["contributions"] < peak * .12 or not w["top_public_repo"]:
            continue
        bx, by = tops[i]
        name = w["top_public_repo"]
        when = dt.date.fromisoformat(w["start"])
        head = f"{w['contributions']} · WK OF {when.strftime('%b').upper()} {when.day}"
        width = max(len(name), len(head)) * 6.3 + 8
        lx = min(max(bx, X0 + width / 2), X1 - width / 2)
        box = (lx - width / 2, by - 42, lx + width / 2, by - 6)
        if any(not (box[2] < b[0] or box[0] > b[2] or box[3] < b[1] or box[1] > b[3]) for b in boxes):
            continue
        if any(box[0] - 4 <= tx <= box[2] + 4 and ty < box[3] for j, (tx, ty) in enumerate(tops) if j != i):
            continue  # a taller spike would poke through the label
        boxes.append(box)
        labels.append(
            f'<g class="lbl" style="animation-delay:{START + DRAW * reach(bx):.2f}s">'
            f'<line x1="{bx:.1f}" y1="{by - 4:.1f}" x2="{lx:.1f}" y2="{by - 12:.1f}" class="lead"/>'
            f'<text x="{lx:.1f}" y="{by - 29:.1f}" text-anchor="middle" class="n">{head}</text>'
            f'<text x="{lx:.1f}" y="{by - 17:.1f}" text-anchor="middle" class="repo">{escape(name)}</text></g>')

    months, last = [], None
    for i, w in enumerate(weeks):
        m = w["start"][:7]
        if i and m != last:
            x = X0 + i * cell
            months.append(f'<line x1="{x:.1f}" y1="{BASE + 18}" x2="{x:.1f}" y2="{BASE + 22}" class="tick"/>'
                          f'<text x="{x:.1f}" y="{BASE + 33}" class="m">'
                          f'{dt.date.fromisoformat(w["start"]).strftime("%b").upper()}</text>')
        last = m

    holes = "".join(f"M{x} {y}a3.2 3.2 0 1 0 6.4 0a3.2 3.2 0 1 0 -6.4 0z"
                    for x in range(22, W - 20, 22) for y in (11, H - 11))
    endx, endy = pts[-1]
    grid_top = BASE - AMP_MAX - 44

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="pt pd">
<title id="pt">Pulse: a year of contributions as an ECG</title>
<desc id="pd">One heartbeat per week for the last {len(weeks)} weeks, {data["contributions_last_year"]} contributions in total, biggest week {peak}. Spikes are labelled with the public repo that got the most commits that week.</desc>
<defs>
  <pattern id="minor" width="8" height="8" patternUnits="userSpaceOnUse" x="{X0}" y="{BASE}">
    <path d="M8 0H0V8" fill="none" stroke="#efcbc4" stroke-width=".6"/>
  </pattern>
  <pattern id="major" width="40" height="40" patternUnits="userSpaceOnUse" x="{X0}" y="{BASE}">
    <path d="M40 0H0V40" fill="none" stroke="#e2a297" stroke-width="1"/>
  </pattern>
  <linearGradient id="tp" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fdfaf2"/><stop offset="1" stop-color="#f3ecdc"/>
  </linearGradient>
  <filter id="glow" x="-300%" y="-300%" width="700%" height="700%">
    <feGaussianBlur stdDeviation="3"/><feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
</defs>
<style>
  text {{ font-family: {MONO}; fill: #2a2622; }}
  .h {{ font-size: 13px; font-weight: 800; letter-spacing: 1.5px; }}
  .s {{ font-size: 10.5px; fill: #8a7d6b; letter-spacing: .4px; }}
  .n {{ font-size: 9.5px; font-weight: 700; fill: #b4321f; }}
  .repo {{ font-size: 10.5px; font-weight: 700; }}
  .m {{ font-size: 10px; fill: #8a7d6b; letter-spacing: 1px; }}
  .lead {{ stroke: #b4321f; stroke-width: 1; }}
  .tick {{ stroke: #b9ad97; stroke-width: 1; }}
  .trace {{ fill: none; stroke: #1f1b17; stroke-width: 1.7; stroke-linejoin: round;
            stroke-dasharray: 1; stroke-dashoffset: 1; animation: draw {DRAW}s linear {START}s forwards; }}
  .lbl {{ opacity: 0; animation: pop .35s ease-out forwards; }}
  .now {{ opacity: 0; transform-box: fill-box; transform-origin: center;
          animation: pop .3s {START + DRAW:.1f}s forwards, beat 1.1s ease-in-out {START + DRAW + .3:.1f}s infinite; }}
  @keyframes draw {{ to {{ stroke-dashoffset: 0; }} }}
  @keyframes pop {{ from {{ opacity: 0; }} to {{ opacity: 1; }} }}
  @keyframes beat {{ 0%, 60%, 100% {{ transform: scale(1); }} 15% {{ transform: scale(1.8); }}
                     30% {{ transform: scale(1.1); }} 45% {{ transform: scale(1.5); }} }}
  @media (prefers-reduced-motion: reduce) {{
    .trace {{ animation: none; stroke-dashoffset: 0; }}
    .lbl, .now {{ animation: none; opacity: 1; }}
  }}
</style>
<path d="M8 0H{W - 8}V{H}H8Z{holes}" fill="url(#tp)" fill-rule="evenodd" stroke="#e0d3b8"/>
<rect x="{X0 - 18}" y="{grid_top}" width="{X1 - X0 + 36}" height="{BASE + 24 - grid_top}" fill="url(#minor)"/>
<rect x="{X0 - 18}" y="{grid_top}" width="{X1 - X0 + 36}" height="{BASE + 24 - grid_top}" fill="url(#major)"/>
<text x="{X0 - 14}" y="40" class="h">♥ PULSE · {escape(login.upper())}</text>
<text x="{X0 + 210}" y="40" class="s">one beat = one week · spikes = hackathons</text>
<text x="{X1 + 14}" y="40" text-anchor="end" class="s">25 mm/s · LEAD: GIT</text>
{"".join(months)}
<path d="{trace}" pathLength="1" class="trace"/>
{"".join(labels)}
<circle cx="{endx:.1f}" cy="{endy:.1f}" r="4" fill="#e11d48" filter="url(#glow)" class="now"/>
<text x="{X0 - 14}" y="{H - 25}" class="s">{data["contributions_last_year"]} CONTRIBUTIONS · {data["active_days_last_year"]} ACTIVE DAYS · PEAK {peak}/WEEK</text>
<text x="{X1 + 14}" y="{H - 25}" text-anchor="end" class="s">THIS WEEK: {weeks[-1]["contributions"]} · RHYTHM: HACKATHON-DRIVEN</text>
</svg>
'''
