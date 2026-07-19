#!/usr/bin/env python3
"""Panel-size vs error curve: subsample panels of size k=1..8 from the 8 eggs-p5
Sonnet experts, score each subsample's mean against the documented external
reference, and see where the error flattens (the variance-reduction 'knee').

Exhaustive over all C(8,k) subsets per size -> no sampling noise. Error is mean
absolute error vs the external values on the scored nodes. Overlays the
theoretical shape error(k) = sqrt(floor^2 + noise^2/k) fit to the empirical MAE,
so the irreducible (shared-bias) floor and the per-voice noise are read off.
"""
import contextlib
import io
import math
import sys
from itertools import combinations
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "coldstart-lab"))
from common import load_roster, node_a_matrix, mean  # noqa

# reuse the external reference (suppress its import-time print)
with contextlib.redirect_stdout(io.StringIO()):
    import external_grounding as eg  # noqa
EXT = {k: v[0] for k, v in eg.EXT.items() if v is not None}

# per-expert node-A ratings
roster = load_roster("eggs-p5")
experts = sorted(a for a, d in roster.items() if d["tier"] == "expert")
items = node_a_matrix("eggs-p5", restrict_ids=set(experts))
# per expert: {node: value}
by = {e: {t: items[t][e] for t in items if e in items[t]} for e in experts}
nodes = [n for n in EXT if all(n in by[e] for e in experts)]
print(f"{len(experts)} experts, {len(nodes)} externally-scored nodes\n")


def subset_mae(subset):
    err = []
    for n in nodes:
        m = mean([by[e][n] for e in subset])
        err.append(abs(m - EXT[n]))
    return mean(err)


curve = []
for k in range(1, len(experts) + 1):
    subs = list(combinations(experts, k))
    maes = [subset_mae(s) for s in subs]
    curve.append((k, mean(maes), min(maes), max(maes), len(subs)))

# fit MAE(k) ~ sqrt(floor^2 + noise^2/k) by grid search (cheap, robust)
best = None
for floor in [i / 200 for i in range(0, 60)]:          # 0..0.30
    for noise in [i / 100 for i in range(1, 120)]:     # 0.01..1.20
        sse = sum((mae - math.sqrt(floor ** 2 + noise ** 2 / k)) ** 2 for k, mae, *_ in curve)
        if best is None or sse < best[0]:
            best = (sse, floor, noise)
_, floor, noise = best

print(f"{'k':>3} {'mean MAE':>9} {'min':>6} {'max':>6} {'fit':>6}  {'subsets':>7}")
for k, m, lo, hi, nsub in curve:
    fit = math.sqrt(floor ** 2 + noise ** 2 / k)
    print(f"{k:>3} {m:>9.3f} {lo:>6.3f} {hi:>6.3f} {fit:>6.3f}  {nsub:>7}")
print(f"\nfit MAE(k) = sqrt({floor:.3f}^2 + {noise:.3f}^2 / k)  "
      f"-> irreducible floor {floor:.3f}, per-voice noise {noise:.3f}")

# marginal gain per added voice + % of total available reduction captured by size k
mae1, mae8 = curve[0][1], curve[-1][1]
total = mae1 - mae8
print(f"\n{'k':>3} {'MAE':>8} {'Δ vs k-1':>9} {'% of max reduction captured':>28}")
prev = None
for k, m, *_ in curve:
    d = "" if prev is None else f"{prev - m:+.3f}"
    pct = (mae1 - m) / total * 100 if total else 0
    print(f"{k:>3} {m:>8.3f} {d:>9} {pct:>27.0f}%")
    prev = m

# ASCII plot
print("\nMAE vs panel size (● empirical, · fit floor):")
lo_y, hi_y = 0.0, max(c[1] for c in curve) * 1.15
W = 50
for k, m, *_ in curve:
    col = round((m - lo_y) / (hi_y - lo_y) * W)
    fitcol = round((floor - lo_y) / (hi_y - lo_y) * W)
    row = [" "] * (W + 1)
    if 0 <= fitcol <= W:
        row[fitcol] = "·"
    row[max(0, min(W, col))] = "●"
    print(f"k={k}  {m:5.3f} |" + "".join(row))
print(f"        {lo_y:5.2f} " + " " * (W) + f"{hi_y:.2f}   (MAE, of 5)")
print(f"        · = fitted irreducible floor ({floor:.3f})")
