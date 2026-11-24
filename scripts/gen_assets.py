"""Generate README SVG assets for ratchet-skills. Usage: python scripts/gen_assets.py assets"""
import math, sys
from pathlib import Path

out = Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)

FONT = ("-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans TC', 'PingFang TC', "
        "'Microsoft JhengHei', 'Noto Sans CJK TC', Helvetica, Arial, sans-serif")
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono', monospace"


def ratchet_path(cx, cy, r_out, r_in, teeth, rot=0.0):
    pts = []
    for i in range(teeth):
        a0 = rot + 2 * math.pi * i / teeth
        a1 = rot + 2 * math.pi * (i + 1) / teeth
        pts.append((cx + r_in * math.cos(a0), cy + r_in * math.sin(a0)))
        pts.append((cx + r_out * math.cos(a1 - 0.02), cy + r_out * math.sin(a1 - 0.02)))
        pts.append((cx + r_in * math.cos(a1), cy + r_in * math.sin(a1)))
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z"
    return d


# ---------------- banner ----------------
def banner():
    W, H = 1200, 340
    cx, cy = 220, 170
    gear = ratchet_path(cx, cy, 108, 84, 14, rot=-0.3)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ratchet-skills">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#0f172a"/>
      <stop offset="1" stop-color="#1e293b"/>
    </linearGradient>
    <linearGradient id="gear" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#fbbf24"/>
      <stop offset="1" stop-color="#f97316"/>
    </linearGradient>
    <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse">
      <path d="M32 0H0V32" fill="none" stroke="#ffffff" stroke-opacity="0.04"/>
    </pattern>
  </defs>
  <rect width="{W}" height="{H}" rx="20" fill="url(#bg)"/>
  <rect width="{W}" height="{H}" rx="20" fill="url(#grid)"/>
  <path d="{gear}" fill="url(#gear)"/>
  <circle cx="{cx}" cy="{cy}" r="52" fill="#0f172a"/>
  <circle cx="{cx}" cy="{cy}" r="20" fill="url(#gear)"/>
  <path d="M{cx-150},{cy+120} A160 160 0 0 1 {cx-160},{cy-40}" fill="none" stroke="#fbbf24" stroke-width="4" stroke-linecap="round" stroke-dasharray="2 12"/>
  <path d="M{cx-171},{cy-30} l11,-22 l11,22 z" fill="#fbbf24"/>
  <text x="420" y="150" font-family="{MONO}" font-size="64" font-weight="700" fill="#f8fafc">ratchet-skills</text>
  <text x="422" y="204" font-family="{FONT}" font-size="28" fill="#fbbf24">每次糾正，都變成一道只會收緊的檢查。</text>
  <text x="422" y="246" font-family="{FONT}" font-size="22" fill="#94a3b8">Every correction becomes a check that only tightens.</text>
  <text x="422" y="292" font-family="{MONO}" font-size="17" fill="#64748b">Agent Skills · Claude Code · Codex · Devin CLI · Windows / macOS / Linux</text>
</svg>
'''
    (out / "banner.svg").write_text(svg, encoding="utf-8")


# ---------------- inverted pyramid ----------------
LAYERS = {
    "zh": [
        ("程式碼庫與架構", "公開 API、型別、目錄邊界", "#16a34a"),
        ("靜態分析與編譯", "lint、型別檢查、依賴圖", "#65a30d"),
        ("執行期與形式驗證", "正常入口重跑、屬性測試", "#ca8a04"),
        ("自然語言規則", "AGENTS.md / CLAUDE.md", "#ea580c"),
        ("人工審查", "只留需要判斷的部分", "#dc2626"),
    ],
    "en": [
        ("Codebase &amp; architecture", "public APIs, types, boundaries", "#16a34a"),
        ("Static analysis", "lint, type checks, dep graph", "#65a30d"),
        ("Runtime &amp; formal checks", "real entry points, properties", "#ca8a04"),
        ("Written rules", "AGENTS.md / CLAUDE.md", "#ea580c"),
        ("Human review", "judgment only", "#dc2626"),
    ],
}
SKILLS = {  # (label, first layer, last layer)
    "zh": [("enforce-codebase-constraints", 0, 1), ("verify-software-behavior", 2, 2),
           ("refine-agent-instructions", 3, 3)],
    "en": [("enforce-codebase-constraints", 0, 1), ("verify-software-behavior", 2, 2),
           ("refine-agent-instructions", 3, 3)],
}
TXT = {
    "zh": dict(title="倒金字塔：把問題往上推到最便宜、最可靠的那一層",
               cost="成本遞增", catch="越早攔截越好", audit="audit-agent-engineering · 逐層盤點",
               outer="automate-quality-loop · 外迴圈：排程 / 發版 / 告警觸發"),
    "en": dict(title="The inverted pyramid: push each problem up to the cheapest reliable layer",
               cost="cost rises", catch="catch it early", audit="audit-agent-engineering · audits every layer",
               outer="automate-quality-loop · outer loop: schedule / release / alert"),
}


def pyramid(lang):
    W, H = 1100, 640
    top, band, gap = 96, 76, 8
    cx = 430
    w_top, w_bot = 680, 170
    n = 5
    t = TXT[lang]
    parts = [f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{t['title']}">
  <defs>
    <marker id="arr" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#94a3b8"/>
    </marker>
  </defs>
  <rect width="{W}" height="{H}" rx="18" fill="#0f172a"/>
  <text x="40" y="54" font-family="{FONT}" font-size="24" font-weight="700" fill="#f8fafc">{t['title']}</text>''']
    total = n * band + (n - 1) * gap
    ys = []
    for i, (name, sub, color) in enumerate(LAYERS[lang]):
        y0 = top + i * (band + gap)
        y1 = y0 + band
        f0 = (y0 - top) / total
        f1 = (y1 - top) / total
        w0 = w_top + (w_bot - w_top) * f0
        w1 = w_top + (w_bot - w_top) * f1
        ys.append((y0, y1, cx + w0 / 2))
        parts.append(
            f'  <path d="M{cx-w0/2:.1f},{y0} L{cx+w0/2:.1f},{y0} L{cx+w1/2:.1f},{y1} L{cx-w1/2:.1f},{y1} Z" fill="{color}" fill-opacity="0.9"/>')
        big = 22 if i < 3 else 19
        parts.append(f'  <text x="{cx}" y="{y0+34}" text-anchor="middle" font-family="{FONT}" font-size="{big}" font-weight="700" fill="#ffffff">{name}</text>')
        if i < 4:
            parts.append(f'  <text x="{cx}" y="{y0+58}" text-anchor="middle" font-family="{FONT}" font-size="15" fill="#ffffff" fill-opacity="0.85">{sub}</text>')
        else:
            parts.append(f'  <text x="{cx}" y="{y0+58}" text-anchor="middle" font-family="{FONT}" font-size="13" fill="#ffffff" fill-opacity="0.85">{sub}</text>')
    # cost arrow on left
    ax = 62
    parts.append(f'  <line x1="{ax}" y1="{top+10}" x2="{ax}" y2="{top+total-10}" stroke="#94a3b8" stroke-width="3" marker-end="url(#arr)"/>')
    parts.append(f'  <text x="{ax-14}" y="{top+total/2}" font-family="{FONT}" font-size="16" fill="#94a3b8" transform="rotate(-90 {ax-14} {top+total/2})" text-anchor="middle">{t["cost"]}</text>')
    # skill brackets on right
    bx = 830
    for label, a, b in SKILLS[lang]:
        y0 = ys[a][0] + 6
        y1 = ys[b][1] - 6
        edge = ys[a][2] + 14
        parts.append(f'  <path d="M{bx-10},{y0} h10 v{y1-y0} h-10" fill="none" stroke="#fbbf24" stroke-width="2.5"/>')
        parts.append(f'  <line x1="{edge:.1f}" y1="{(y0+y1)/2}" x2="{bx-16}" y2="{(y0+y1)/2}" stroke="#fbbf24" stroke-opacity="0.35" stroke-dasharray="4 5"/>')
        parts.append(f'  <text x="{bx+12}" y="{(y0+y1)/2+6}" font-family="{MONO}" font-size="15" fill="#fbbf24">{label}</text>')
    # review label
    yr = (ys[4][0] + ys[4][1]) / 2
    parts.append(f'  <text x="{bx+12}" y="{yr+6}" font-family="{FONT}" font-size="15" fill="#94a3b8">{"← 先看驗證證據" if lang=="zh" else "← reads evidence first"}</text>')
    # bottom bars: audit + outer loop
    yb = top + total + 28
    parts.append(f'  <rect x="40" y="{yb}" width="{W-80}" height="40" rx="10" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5"/>')
    parts.append(f'  <text x="{W/2}" y="{yb+26}" text-anchor="middle" font-family="{MONO}" font-size="15" fill="#38bdf8">{t["audit"]}</text>')
    yb2 = yb + 52
    parts.append(f'  <rect x="40" y="{yb2}" width="{W-80}" height="40" rx="10" fill="#1e293b" stroke="#a78bfa" stroke-width="1.5" stroke-dasharray="6 5"/>')
    parts.append(f'  <text x="{W/2}" y="{yb2+26}" text-anchor="middle" font-family="{MONO}" font-size="15" fill="#a78bfa">{t["outer"]}</text>')
    parts.append("</svg>\n")
    (out / f"pyramid.{lang}.svg").write_text("\n".join(parts), encoding="utf-8")


banner()
pyramid("zh")
pyramid("en")
print("ok", sorted(p.name for p in out.iterdir()))
