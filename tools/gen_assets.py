#!/usr/bin/env python3
"""Generate every image on the profile, light and dark, from one source of truth.

    python tools/gen_assets.py      -> assets/*.svg

Design rules
- Two files per image, switched by <picture>: Safari ignores prefers-color-scheme
  inside an <img>-loaded SVG, <picture> works everywhere.
- Colours are GitHub Primer tokens, so each image looks native in either theme.
- System font stacks only; an <img> SVG cannot load web fonts. Monospace layout
  uses explicit x per column so alignment never depends on the viewer's font.
- SMIL animation only (works in <img> SVGs in Chrome, Firefox, Safari). The
  terminal reveals once and freezes; only the cursor, status dot and the Raft
  cluster loop.
- No numbers live anywhere but CHECKS / RAFT / CARDS below, and each one is
  copied from a file in the named repo. Change a number there, regenerate.
"""
from pathlib import Path
from xml.sax.saxutils import escape as _esc

ROOT = Path(__file__).resolve().parent.parent / "assets"

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono','DejaVu Sans Mono',monospace"

THEMES = {
    "dark": dict(
        bg0="#0d1117", bg1="#121a26", panel="#151b23", panel2="#0f141b",
        fg="#f0f6fc", text="#d1d7e0", muted="#9198a1", faint="#3d444d", border="#3d444d",
        dot="#262c36", accent="#4493f8", ok="#3fb950", bad="#f85149", warn="#d29922",
        purple="#ab7df8", orange="#db6d28", pink="#db61a2", teal="#39c5cf",
        glow_a=0.22, glow_b=0.14, chip="#1c2330",
    ),
    "light": dict(
        bg0="#ffffff", bg1="#f6f8fa", panel="#f6f8fa", panel2="#ffffff",
        fg="#1f2328", text="#25292e", muted="#59636e", faint="#d1d9e0", border="#d1d9e0",
        dot="#e1e6eb", accent="#0969da", ok="#1a7f37", bad="#d1242f", warn="#9a6700",
        purple="#8250df", orange="#bc4c00", pink="#bf3989", teal="#1b7c83",
        glow_a=0.12, glow_b=0.08, chip="#eef1f4",
    ),
}


def esc(s: str) -> str:
    return _esc(s, {'"': "&quot;"})


def svg_open(w, h, label, extra_style=""):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{esc(label)}">',
        f"<title>{esc(label)}</title>",
        f"<style>.s{{font-family:{SANS}}}.m{{font-family:{MONO}}}{extra_style}</style>",
    ]


def backdrop(c, w, h, uid, glow="accent", glow2="purple", rx=16):
    """Rounded panel with a dot grid and two soft colour glows."""
    return [
        "<defs>",
        f'<linearGradient id="{uid}bg" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{c["bg1"]}"/><stop offset="1" stop-color="{c["bg0"]}"/></linearGradient>',
        f'<radialGradient id="{uid}g1" cx="0.92" cy="0.0" r="0.65">'
        f'<stop offset="0" stop-color="{c[glow]}" stop-opacity="{c["glow_a"]}"/>'
        f'<stop offset="1" stop-color="{c[glow]}" stop-opacity="0"/></radialGradient>',
        f'<radialGradient id="{uid}g2" cx="0.0" cy="1.0" r="0.6">'
        f'<stop offset="0" stop-color="{c[glow2]}" stop-opacity="{c["glow_b"]}"/>'
        f'<stop offset="1" stop-color="{c[glow2]}" stop-opacity="0"/></radialGradient>',
        f'<pattern id="{uid}dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="2" cy="2" r="1" fill="{c["dot"]}"/></pattern>',
        f'<clipPath id="{uid}clip"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{rx}"/></clipPath>',
        "</defs>",
        f'<g clip-path="url(#{uid}clip)">',
        f'<rect width="{w}" height="{h}" fill="url(#{uid}bg)"/>',
        f'<rect width="{w}" height="{h}" fill="url(#{uid}dots)"/>',
        f'<rect width="{w}" height="{h}" fill="url(#{uid}g1)"/>',
        f'<rect width="{w}" height="{h}" fill="url(#{uid}g2)"/>',
        "</g>",
        f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="{rx}" fill="none" stroke="{c["border"]}"/>',
    ]


def chip_row(c, x, y, chips, fs=12, h=24, gap=8, color=None, max_x=None):
    """Pill chips. Width estimated from monospace advance, so it never overflows."""
    out, cx = [], x
    for t in chips:
        w = len(t) * 0.602 * fs + 22
        if max_x is not None:
            assert cx + w <= max_x, f"chip row overflows at {t!r}"
        out.append(
            f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{h/2}" '
            f'fill="{c["chip"]}" stroke="{c["border"]}"/>'
            f'<text class="m" x="{cx + 11:.1f}" y="{y + h/2 + fs*0.36:.1f}" font-size="{fs}" '
            f'fill="{color or c["muted"]}">{esc(t)}</text>'
        )
        cx += w + gap
    return out, cx


# ---------------------------------------------------------------- hero

NAME = "Suvidh Jain"
ROLE = "Backend & distributed-systems engineer"
TAGLINE = [
    "I build systems, then the machinery that tries to break them:",
    "crash harnesses, linearizability checkers, leakage tests,",
    "hand-labelled evals and load tests at a million rows.",
]
STATUS = "open to SDE internships · 2027 new-grad roles"
CREDS = [
    ("edu", "VIT Vellore · B.Tech CSE '27 · CGPA 9.26"),
    ("won", "1st / 100+ teams · JPMC Code for Good '25"),
    ("final", "Intain FinTech Challenge 2026"),
    ("work", "Datamatics · HPE CPP · SentinelGuard AI"),
]

# (passed?, repo, claim, evidence file). Each claim is copied from that file.
CHECKS = [
    (True,  "raft-kv",   "0 of 177,568 acked writes lost across 200 leader crashes", "BENCHMARKS.md"),
    (True,  "raft-kv",   "500/500 seeded chaos runs linearizable under Porcupine",  "BENCHMARKS.md"),
    (True,  "gatehouse", "slowest endpoint 4,022 ms → 2–5 ms at 1,000,828 sessions", "METRICS.md"),
    (True,  "lpie",      "12-month default AUC 0.973 out-of-time · 5/5 leaks caught", "model_card.md"),
    (True,  "handoff",   "79 of 82 classifier errors escalated to a human, not sent", "REPORT.md"),
    (True,  "geo-api",   "area within 0.25% of geodesic truth from 89°S to 89°N",    "README#accuracy"),
    (False, "drift-rag", "“3.00× over random” was a 3-seed artifact · withdrawn",     "STATUS.md §4"),
    (False, "lpie",      "confidence column runs backwards on 3 of 4 targets · kept", "decisions/D37"),
]


def hero(theme: str) -> str:
    c = THEMES[theme]
    W = 1000
    FS, LH = 13.5, 25
    CH = 0.602 * FS
    TX, TW = 36, W - 72          # terminal box
    TY = 262
    PAD = 22
    n_lines = 1 + len(CHECKS) + 1 + 1 + 1   # cmd, checks, blank, summary, prompt
    TH = 38 + PAD + n_lines * LH
    H = TY + TH + 36

    passed = sum(ok for ok, *_ in CHECKS)
    failed = len(CHECKS) - passed
    label = (f"{NAME}, {ROLE}. A terminal runs make verify across the portfolio: "
             f"{passed} claims reproduce, {failed} refuted results are kept on record.")
    o = svg_open(W, H, label, "@keyframes p{0%,100%{opacity:1}50%{opacity:.35}}")
    o += backdrop(c, W, H, "h")

    # status pill with a pulsing dot
    pill_w = len(STATUS) * 0.602 * 12 + 44
    o.append(f'<rect x="36" y="34" width="{pill_w:.0f}" height="28" rx="14" fill="{c["chip"]}" stroke="{c["border"]}"/>')
    o.append(f'<circle cx="54" cy="48" r="4.5" fill="{c["ok"]}">'
             f'<animate attributeName="opacity" values="1;0.3;1" dur="2.4s" repeatCount="indefinite"/></circle>')
    o.append(f'<circle cx="54" cy="48" r="4.5" fill="none" stroke="{c["ok"]}" stroke-width="1.5">'
             f'<animate attributeName="r" values="4.5;10" dur="2.4s" repeatCount="indefinite"/>'
             f'<animate attributeName="opacity" values="0.7;0" dur="2.4s" repeatCount="indefinite"/></circle>')
    o.append(f'<text class="m" x="68" y="52.5" font-size="12" fill="{c["text"]}">{esc(STATUS)}</text>')

    # identity
    o.append(f'<text class="s" x="34" y="124" font-size="52" font-weight="700" fill="{c["fg"]}" letter-spacing="-1">{esc(NAME)}</text>')
    o.append(f'<text class="s" x="36" y="160" font-size="20" font-weight="600" fill="{c["accent"]}">{esc(ROLE)}</text>')
    for i, line in enumerate(TAGLINE):
        o.append(f'<text class="s" x="36" y="{192 + i*21}" font-size="15" fill="{c["muted"]}">{esc(line)}</text>')

    # credentials panel
    px, py, pw, ph = 584, 34, 380, 196
    o.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="12" fill="{c["panel2"]}" fill-opacity="0.7" stroke="{c["border"]}"/>')
    o.append(f'<text class="m" x="{px+20}" y="{py+30}" font-size="11.5" fill="{c["muted"]}" letter-spacing="1.5">RECORD</text>')
    for i, (k, v) in enumerate(CREDS):
        y = py + 66 + i * 36
        o.append(f'<text class="m" x="{px+20}" y="{y}" font-size="11.5" fill="{c["accent"]}">{esc(k)}</text>')
        assert len(v) * 7.0 < pw - 88, f"credential too long: {v}"
        o.append(f'<text class="s" x="{px+76}" y="{y}" font-size="14" fill="{c["text"]}">{esc(v)}</text>')

    # terminal window
    o.append(f'<rect x="{TX}" y="{TY}" width="{TW}" height="{TH}" rx="12" fill="{c["panel"]}" stroke="{c["border"]}"/>')
    o.append(f'<path d="M{TX} {TY+38} H{TX+TW}" stroke="{c["border"]}"/>')
    for i, col in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        o.append(f'<circle cx="{TX+22+i*20}" cy="{TY+19}" r="6" fill="{col}"/>')
    o.append(f'<text class="m" x="{TX+TW/2}" y="{TY+23.5}" font-size="12" fill="{c["muted"]}" text-anchor="middle">'
             f'~/github.com/SuvidhJ — every number on this page, re-checked</text>')

    x0 = TX + PAD
    xr = TX + TW - PAD
    inner = TW - 2 * PAD
    y = TY + 38 + PAD + FS - 2
    o.append(f'<text class="m" x="{x0}" y="{y}" font-size="{FS}"><tspan fill="{c["ok"]}">➜</tspan>'
             f'<tspan fill="{c["accent"]}">  portfolio</tspan><tspan fill="{c["text"]}"> make verify</tspan></text>')

    defs = []
    T0, STEP, TYPE = 0.6, 0.42, 0.38

    def reveal(i, yy):
        b = T0 + i * STEP
        defs.append(
            f'<clipPath id="r{i}"><rect x="{x0-4}" y="{yy-FS-3}" height="{LH}" width="0">'
            f'<animate attributeName="width" from="0" to="{inner+8}" begin="{b:.2f}s" dur="{TYPE}s" fill="freeze"/>'
            f'</rect></clipPath>')

    REPO_COL = 11
    for i, (ok, repo, claim, ev) in enumerate(CHECKS):
        y += LH
        mark, col = ("✓", c["ok"]) if ok else ("✗", c["bad"])
        used = (3 + REPO_COL + len(claim)) * CH + (len(ev) + 3) * 0.602 * 12
        assert used <= inner, f"line too long: {claim!r} ({used:.0f} > {inner})"
        reveal(i, y)
        g = f'<g clip-path="url(#r{i})" font-size="{FS}">'
        g += f'<text class="m" x="{x0}" y="{y}" fill="{col}" font-weight="700">{mark}</text>'
        g += f'<text class="m" x="{x0 + 2.4*CH:.1f}" y="{y}" fill="{c["accent"]}">{esc(repo)}</text>'
        g += (f'<text class="m" x="{x0 + (2.4+REPO_COL)*CH:.1f}" y="{y}" '
              f'fill="{c["text"] if ok else c["bad"]}">{esc(claim)}</text>')
        g += (f'<text class="m" x="{xr}" y="{y}" font-size="12" text-anchor="end" fill="{c["muted"]}">'
              f'{esc(ev)} ↗</text></g>')
        o.append(g)

    y += LH * 2
    i = len(CHECKS)
    reveal(i, y)
    end = T0 + i * STEP + TYPE
    o.append(f'<text class="m" x="{x0}" y="{y}" font-size="{FS}" clip-path="url(#r{i})">'
             f'<tspan fill="{c["ok"]}" font-weight="700">{passed} reproduced</tspan>'
             f'<tspan fill="{c["muted"]}">  ·  </tspan>'
             f'<tspan fill="{c["bad"]}" font-weight="700">{failed} refuted, kept on record</tspan>'
             f'<tspan fill="{c["muted"]}">  ·  every claim links to the file that produces it</tspan></text>')
    y += LH
    o.append(f'<g opacity="0"><animate attributeName="opacity" to="1" begin="{end+0.25:.2f}s" dur="0.01s" fill="freeze"/>'
             f'<text class="m" x="{x0}" y="{y}" font-size="{FS}"><tspan fill="{c["ok"]}">➜</tspan>'
             f'<tspan fill="{c["accent"]}">  portfolio</tspan></text>'
             f'<rect x="{x0 + 13*CH:.1f}" y="{y-FS+2}" width="{CH:.1f}" height="{FS+1}" fill="{c["text"]}">'
             f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/>'
             f'</rect></g>')

    o.insert(3, "<defs>" + "".join(defs) + "</defs>")
    o.append("</svg>")
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- raft flagship

RAFT_FEATURES = ["pre-vote", "check-quorum", "leadership transfer", "ReadIndex reads",
                 "membership changes", "exactly-once sessions", "CRC32-C WAL", "torn writes"]
RAFT_TILES = [
    ("0", "ok", ["acked writes lost of 177,568,", "across 200 forced leader crashes"]),
    ("500/500", "ok", ["chaos runs linearizable: 1,426", "crashes, 2,830 partitions"]),
    ("8", "warn", ["consensus bugs caught by my", "harnesses · incl. a safety bug"]),
    ("514 ms", "accent", ["p99 to resume writes after a", "leader crash · was 1,140 ms"]),
]


def raft(theme: str) -> str:
    c = THEMES[theme]
    W, H = 1000, 392
    o = svg_open(W, H, "raft-kv: Raft written from scratch in Go and chaos-tested. 0 of 177,568 acknowledged "
                       "writes lost across 200 leader crashes; 500 of 500 chaos runs linearizable; 8 consensus bugs "
                       "found; p99 write recovery 514 ms.")
    o += backdrop(c, W, H, "r", glow="ok", glow2="accent")

    o.append(f'<text class="m" x="36" y="50" font-size="12" fill="{c["ok"]}" letter-spacing="1.5">FLAGSHIP · GO · NO RAFT LIBRARY</text>')
    o.append(f'<text class="s" x="34" y="98" font-size="40" font-weight="700" fill="{c["fg"]}" letter-spacing="-0.5">raft-kv</text>')
    o.append(f'<text class="s" x="36" y="130" font-size="16" fill="{c["text"]}">Raft consensus and a replicated KV store, written from scratch,</text>')
    o.append(f'<text class="s" x="36" y="152" font-size="16" fill="{c["text"]}">then attacked by a chaos harness until it stopped breaking.</text>')
    row1, _ = chip_row(c, 36, 174, RAFT_FEATURES[:4], max_x=640)
    row2, _ = chip_row(c, 36, 206, RAFT_FEATURES[4:], max_x=640)
    o += row1 + row2

    # stat tiles
    tw, th, ty, gap = 222, 112, 250, 12
    for i, (big, tone, cap) in enumerate(RAFT_TILES):
        tx = 36 + i * (tw + gap)
        o.append(f'<rect x="{tx}" y="{ty}" width="{tw}" height="{th}" rx="10" fill="{c["panel2"]}" fill-opacity="0.8" stroke="{c["border"]}"/>')
        o.append(f'<rect x="{tx}" y="{ty+14}" width="3" height="{th-28}" rx="1.5" fill="{c[tone]}"/>')
        o.append(f'<text class="s" x="{tx+20}" y="{ty+46}" font-size="32" font-weight="700" fill="{c[tone]}">{esc(big)}</text>')
        for j, line in enumerate(cap):
            o.append(f'<text class="s" x="{tx+20}" y="{ty+74+j*18}" font-size="13" fill="{c["muted"]}">{esc(line)}</text>')

    o += cluster(c, cx=820, cy=128, R=70)
    o.append("</svg>")
    return "\n".join(o) + "\n"


def cluster(c, cx, cy, R):
    """Five-node Raft cluster on a 10 s loop: heartbeats from n1, n1 crashes,
    n4 campaigns and wins, heartbeats resume from n4."""
    import math
    D = 10.0
    pts = [(cx + R * math.sin(2 * math.pi * k / 5), cy - R * math.cos(2 * math.pi * k / 5)) for k in range(5)]
    L1, L2 = 0, 3
    t_crash, t_won = 4.2, 5.4
    kt = lambda *ts: ";".join(f"{t/D:.3f}" for t in ts)
    out = []
    # links
    for a in range(5):
        for b in range(a + 1, 5):
            out.append(f'<line x1="{pts[a][0]:.1f}" y1="{pts[a][1]:.1f}" x2="{pts[b][0]:.1f}" y2="{pts[b][1]:.1f}" '
                       f'stroke="{c["faint"]}" stroke-width="1" stroke-dasharray="2 4"/>')

    def beats(src, start, stop, color):
        g = (f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" '
             f'keyTimes="{kt(0, start, start+0.01, stop, stop+0.01, D)}" dur="{D}s" repeatCount="indefinite"/>')
        for k in range(5):
            if k == src:
                continue
            (x1, y1), (x2, y2) = pts[src], pts[k]
            g += (f'<circle r="3" fill="{color}"><animateMotion dur="0.8s" repeatCount="indefinite" '
                  f'path="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}"/></circle>')
        return g + "</g>"

    out.append(beats(L1, 0, t_crash, c["ok"]))
    out.append(beats(L2, t_won, D, c["ok"]))
    # vote requests from the candidate
    g = (f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0;0" '
         f'keyTimes="{kt(0, t_crash+0.2, t_crash+0.21, t_won, t_won+0.01, D)}" dur="{D}s" repeatCount="indefinite"/>')
    for k in (1, 2, 4):
        (x1, y1), (x2, y2) = pts[L2], pts[k]
        g += (f'<circle r="3" fill="{c["warn"]}"><animateMotion dur="0.5s" repeatCount="indefinite" '
              f'path="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}"/></circle>')
    out.append(g + "</g>")

    # nodes
    for k, (x, y) in enumerate(pts):
        if k == L1:
            fill = (f'<animate attributeName="fill" values="{c["ok"]};{c["ok"]};{c["bad"]};{c["bad"]};{c["panel"]};{c["panel"]}" '
                    f'keyTimes="{kt(0, t_crash, t_crash+0.01, 8.6, 8.61, D)}" dur="{D}s" repeatCount="indefinite"/>')
            base = c["ok"]
        elif k == L2:
            fill = (f'<animate attributeName="fill" values="{c["panel"]};{c["panel"]};{c["warn"]};{c["warn"]};{c["ok"]};{c["ok"]}" '
                    f'keyTimes="{kt(0, t_crash+0.2, t_crash+0.21, t_won, t_won+0.01, D)}" dur="{D}s" repeatCount="indefinite"/>')
            base = c["panel"]
        else:
            fill, base = "", c["panel"]
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="{base}" stroke="{c["muted"]}" stroke-width="1.5">{fill}</circle>')
        out.append(f'<text class="m" x="{x:.1f}" y="{y+4:.1f}" font-size="11" text-anchor="middle" fill="{c["fg"]}">n{k+1}</text>')

    # caption that follows the story
    states = [
        (0, t_crash, "term 7 · leader n1 · heartbeats", c["muted"]),
        (t_crash, t_won, "n1 killed · n4 runs for election", c["bad"]),
        (t_won, D, "term 8 · leader n4 · writes resume", c["ok"]),
    ]
    for a, b, txt, col in states:
        vals = "0;0;1;1;0;0" if a > 0 else "1;1;0;0"
        kts = kt(0, a, a + 0.01, b, b + 0.01, D) if a > 0 else kt(0, b, b + 0.01, D)
        out.append(f'<text class="m" x="{cx}" y="{cy+R+44}" font-size="12" text-anchor="middle" fill="{col}" opacity="{1 if a == 0 else 0}">'
                   f'{esc(txt)}<animate attributeName="opacity" values="{vals}" keyTimes="{kts}" dur="{D}s" repeatCount="indefinite"/></text>')
    return out


# ---------------------------------------------------------------- project cards

CARDS = [
    dict(slug="handoff", name="Handoff", lang="Python", tone="ok",
         desc=["A support agent for @AmericanAir that drafts grounded replies,",
               "and decides when a person should send it instead — and why."],
         big="79 / 82", cap=["classifier errors escalated to a person, not sent;",
                             "auto-handles 22% at 6.2% error vs 37.6% sending all"],
         chips=["LLM-as-judge", "RAG", "eval harness"]),
    dict(slug="lpie", name="Loan Performance Engine", lang="Python", tone="purple",
         desc=["Default, delinquency and prepayment models on 8M Freddie Mac",
               "loan-months. Intain FinTech Challenge finalist."],
         big="AUC 0.973", cap=["12-month default, out-of-time, 95% CI 0.956–0.990;",
                               "leakage harness catches 5 of 5 injected leaks"],
         chips=["survival", "SHAP", "pre-registered"]),
    dict(slug="gatehouse", name="Gatehouse", lang="TypeScript", tone="accent",
         desc=["Car-park control for a multi-storey mall: Postgres 17,",
               "Express 5, React 19, a live WebSocket floor plan."],
         big="4,022 → 2–5 ms", cap=["slowest endpoint at 1,000,828 sessions; check-out",
                                    "race failures 8/22 → 0; coverage 9.8% → 86%"],
         chips=["Postgres", "load-tested", "172 tests"]),
    dict(slug="drift-rag", name="Drift-Aware RAG", lang="Python", tone="orange",
         desc=["Label-free detection of retrieval decay from embedding",
               "geometry, on real arXiv, Python-docs and Wikipedia revisions."],
         big="100% false alarms", cap=["when a drift threshold meets 10× less traffic.",
                                       "So it ships calibrated z-scores, not thresholds"],
         chips=["permutation nulls", "MMD", "negative result"]),
    dict(slug="geo-api", name="Geospatial Measurement API", lang="Python", tone="teal",
         desc=["Measures Shapefile, KML and KMZ features in a per-feature",
               "projected CRS, cross-checked against the WGS84 ellipsoid."],
         big="< 0.25%", cap=["area error vs geodesic truth from 89°S to 89°N;",
                             "Web Mercator is off by 297% at Oslo"],
         chips=["FastAPI", "Redis + RQ", "98% coverage"]),
    dict(slug="bitcoin", name="Bitcoin, from raw bytes", lang="Python · TS", tone="pink",
         desc=["Chain analysis from block files, a BIP-174 PSBT builder and",
               "a transaction parser, each a CLI plus a web visualizer."],
         big="12 heuristics", cap=["CIOH, change detection, CoinJoin, peeling chains,",
                                   "each with a confidence model and failure modes"],
         chips=["sherlock", "txforge", "chainlens"]),
]


def card(theme: str, d: dict) -> str:
    c = THEMES[theme]
    W, H = 480, 268
    tone = c[d["tone"]]
    label = f'{d["name"]}: {" ".join(d["desc"])} {d["big"]}: {" ".join(d["cap"])}'
    o = svg_open(W, H, label)
    o += backdrop(c, W, H, d["slug"][:3], glow=d["tone"], glow2="accent", rx=14)
    o.append(f'<rect x="24" y="0" width="64" height="3" rx="1.5" fill="{tone}"/>')
    o.append(f'<text class="s" x="24" y="46" font-size="21" font-weight="700" fill="{c["fg"]}">{esc(d["name"])}</text>')
    o.append(f'<circle cx="{W-24-len(d["lang"])*7.3-12}" cy="41" r="5" fill="{tone}"/>')
    o.append(f'<text class="m" x="{W-24}" y="45" font-size="12" text-anchor="end" fill="{c["muted"]}">{esc(d["lang"])}</text>')
    for i, line in enumerate(d["desc"]):
        assert len(line) <= 64, f"desc too long: {line}"
        o.append(f'<text class="s" x="24" y="{76 + i*20}" font-size="13.5" fill="{c["text"]}">{esc(line)}</text>')
    o.append(f'<text class="s" x="23" y="{158}" font-size="34" font-weight="700" fill="{tone}" letter-spacing="-0.5">{esc(d["big"])}</text>')
    for i, line in enumerate(d["cap"]):
        assert len(line) <= 56, f"caption too long: {line}"
        o.append(f'<text class="s" x="24" y="{184 + i*18}" font-size="13" fill="{c["muted"]}">{esc(line)}</text>')
    chips, _ = chip_row(c, 24, 222, d["chips"], fs=11.5, h=24, max_x=W - 24)
    o += chips
    o.append(f'<text class="m" x="{W-24}" y="{238}" font-size="12" text-anchor="end" fill="{tone}">view repo ↗</text>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


# ---------------------------------------------------------------- section rules

def rule(theme: str, title: str, slug: str, tone: str = "accent") -> str:
    """A thin section header: mono label, a gradient hairline."""
    c = THEMES[theme]
    W, H = 1000, 44
    o = svg_open(W, H, title)
    o.append(f'<defs><linearGradient id="l{slug}" x1="0" x2="1"><stop offset="0" stop-color="{c[tone]}"/>'
             f'<stop offset="0.35" stop-color="{c["border"]}"/><stop offset="1" stop-color="{c["border"]}" stop-opacity="0"/></linearGradient></defs>')
    tw = len(title) * 0.602 * 14 * 1.12
    o.append(f'<text class="m" x="2" y="27" font-size="14" font-weight="700" fill="{c[tone]}" letter-spacing="1.6">{esc(title.upper())}</text>')
    o.append(f'<rect x="{tw + 18:.0f}" y="21" width="{W - tw - 20:.0f}" height="1.5" fill="url(#l{slug})"/>')
    o.append("</svg>")
    return "\n".join(o) + "\n"


RULES = [
    ("flagship", "Flagship", "ok"),
    ("work", "Selected work", "accent"),
    ("record", "On the record: what didn't hold", "bad"),
    ("experience", "Experience", "purple"),
]


if __name__ == "__main__":
    ROOT.mkdir(exist_ok=True)
    jobs = {"hero": hero, "raft": raft}
    for t in THEMES:
        files = {f"hero-{t}.svg": hero(t), f"raft-{t}.svg": raft(t)}
        for d in CARDS:
            files[f'card-{d["slug"]}-{t}.svg'] = card(t, d)
        for slug, title, tone in RULES:
            files[f"rule-{slug}-{t}.svg"] = rule(t, title, slug, tone)
        for name, body in files.items():
            (ROOT / name).write_text(body, encoding="utf-8")
    total = sum(p.stat().st_size for p in ROOT.glob("*.svg"))
    print(f"wrote {len(list(ROOT.glob('*.svg')))} files, {total/1024:.0f} KB")
