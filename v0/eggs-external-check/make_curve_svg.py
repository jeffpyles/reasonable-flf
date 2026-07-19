#!/usr/bin/env python3
"""Render the panel-size vs error curve as a clean, theme-aware SVG.
Single data series (empirical MAE) + fitted sqrt(floor^2 + noise^2/k) overlay +
the irreducible-floor asymptote. Data from panel_size_curve.py."""
import math
from pathlib import Path

K = list(range(1, 9))
MAE = [0.196, 0.158, 0.142, 0.133, 0.126, 0.121, 0.118, 0.114]
FLOOR, NOISE = 0.100, 0.170

W, H = 660, 430
L, R, T, B = 78, 34, 66, 58          # margins
PW, PH = W - L - R, H - T - B
YMAX = 0.22


def xp(k):
    return L + (k - 1) / 7 * PW


def yp(v):
    return T + (1 - v / YMAX) * PH


def fit(k):
    return math.sqrt(FLOOR ** 2 + NOISE ** 2 / k)


# fitted smooth curve
fit_pts = []
i = 1.0
while i <= 8.0001:
    fit_pts.append(f"{xp(i):.1f},{yp(fit(i)):.1f}")
    i += 0.1
fit_path = "M" + " L".join(fit_pts)
emp_path = "M" + " L".join(f"{xp(k):.1f},{yp(MAE[k-1]):.1f}" for k in K)

ygrid = [0.0, 0.05, 0.10, 0.15, 0.20]
svg = []
svg.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" font-family="ui-sans-serif,system-ui,sans-serif">')
svg.append('''<style>
  :root{--ink:#111827;--muted:#6b7280;--grid:#e9ecf1;--surface:#ffffff;--accent:#2563eb;--floor:#9aa2af;}
  @media (prefers-color-scheme:dark){:root{--ink:#e8eaed;--muted:#9aa2af;--grid:#2a3242;--surface:#0f1420;--accent:#5b9dff;--floor:#7c8494;}}
  :root[data-theme=dark]{--ink:#e8eaed;--muted:#9aa2af;--grid:#2a3242;--surface:#0f1420;--accent:#5b9dff;--floor:#7c8494;}
  :root[data-theme=light]{--ink:#111827;--muted:#6b7280;--grid:#e9ecf1;--surface:#ffffff;--accent:#2563eb;--floor:#9aa2af;}
  .ink{fill:var(--ink)} .mut{fill:var(--muted)} .gl{stroke:var(--grid)}
</style>''')
svg.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="var(--surface)"/>')
svg.append(f'<text x="{L}" y="30" class="ink" font-size="16" font-weight="600">Panel size vs error: variance reduction hits a shared-bias floor</text>')
svg.append(f'<text x="{L}" y="48" class="mut" font-size="12">8 Sonnet experts, all C(8,k) subsets scored against the documented external reference (mean abs error, of 5)</text>')

# y gridlines + labels
for v in ygrid:
    y = yp(v)
    svg.append(f'<line x1="{L}" y1="{y:.1f}" x2="{L+PW}" y2="{y:.1f}" class="gl" stroke-width="1"/>')
    svg.append(f'<text x="{L-10}" y="{y+4:.1f}" class="mut" font-size="11" text-anchor="end">{v:.2f}</text>')
# x ticks
for k in K:
    svg.append(f'<text x="{xp(k):.1f}" y="{T+PH+22}" class="mut" font-size="11" text-anchor="middle">{k}</text>')
svg.append(f'<text x="{L+PW/2:.1f}" y="{T+PH+44}" class="mut" font-size="12" text-anchor="middle">panel size (independent voices)</text>')

# floor asymptote
yf = yp(FLOOR)
svg.append(f'<line x1="{L}" y1="{yf:.1f}" x2="{L+PW}" y2="{yf:.1f}" stroke="var(--floor)" stroke-width="1.5" stroke-dasharray="2 4"/>')
svg.append(f'<text x="{L+PW}" y="{yf-7:.1f}" class="mut" font-size="11" text-anchor="end">irreducible shared-bias floor ≈ 0.10 — no number of same-model voices reaches it</text>')

# fitted curve
svg.append(f'<path d="{fit_path}" fill="none" stroke="var(--accent)" stroke-width="1.5" stroke-dasharray="5 4" opacity="0.7"/>')
# empirical line + points
svg.append(f'<path d="{emp_path}" fill="none" stroke="var(--accent)" stroke-width="2.5"/>')
for k in K:
    svg.append(f'<circle cx="{xp(k):.1f}" cy="{yp(MAE[k-1]):.1f}" r="4.5" fill="var(--accent)" stroke="var(--surface)" stroke-width="2"/>')
# value labels on a few key points
for k in (1, 4, 8):
    dy = -12 if k != 8 else -12
    svg.append(f'<text x="{xp(k):.1f}" y="{yp(MAE[k-1])+dy:.1f}" class="ink" font-size="11" font-weight="600" text-anchor="middle">{MAE[k-1]:.3f}</text>')

# knee annotation at k=4
kx, ky = xp(4), yp(MAE[3])
svg.append(f'<text x="{kx+10:.1f}" y="{ky+26:.1f}" class="mut" font-size="11">k=4: ~78% of the achievable reduction</text>')
# fit label
svg.append(f'<text x="{L+8}" y="{T+14}" class="mut" font-size="11">fit  MAE(k) = √(0.10² + 0.17²/k)</text>')
svg.append('</svg>')

out = Path(__file__).resolve().parent / "panel_size_curve.svg"
out.write_text("\n".join(svg))
print(f"wrote {out}")
