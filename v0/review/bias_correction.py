#!/usr/bin/env python3
"""Bias-CORRECTION vs bias-EXCLUSION on eggs-p6.

The FLYWHEEL recipe treats biased raters as noise to be down-weighted to ~0
(gamma=6 concentrates nearly all weight on the 4 competent). But a SHARED,
DIRECTIONAL bias is information: a rater who is predictably wrong is a
miscalibrated instrument, not a broken one. If their error is systematic, a
small anchor set can estimate each rater's transfer function and INVERT it --
then 16 corrected-biased raters + 4 competent all contribute signal, instead of
16 being zeroed.

Method: for each rater, fit an affine map truth ~ a*rating + b on the 10
contested-anchor items only (same anchors, same budget as the recipe), ridge-
regularized toward identity (lam pulls a->1, b->0; anchors are few). Apply the
map to every rating, aggregate with a PLAIN UNWEIGHTED mean (no reputation, no
gamma), and evaluate on the held-out biased items -- head-to-head against the
recipe's superlinear-exclusion numbers (held-out corr 0.90 / MAE 0.44).

Also reports: correction + inverse-residual-variance weights (each rater's
anchor residual sd -> weight 1/(sd^2+eps)), a soft version of trusting whoever
the anchors say is accurate, without gamma; and each arm's robustness when k
anchors are corrupted with the biased-crowd value (same worst-case protocol as
review/anchor_error_sensitivity.py).
"""
import json, math, statistics as st, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from reasonable import store, fold  # noqa

LAM = 2.0     # ridge strength toward (a=1, b=0), in units of anchor points

roster = json.loads((HERE.parent / "eggs-p6/harness/roster.json").read_text())
tier = {a["id"]: a["tier"] for a in roster["agents"]}
p6 = fold.fold(store.read_events("eggs-p6"))
items = {}
for t, dm in p6["ratings"].items():
    if "A" in dm and t.startswith("n"):
        cell = {a: v for a, v in dm["A"].items() if v != "abstain" and a in tier}
        if cell:
            items[t] = cell
p5 = fold.fold(store.read_events("eggs-p5"))
r5 = json.loads((HERE.parent / "eggs-p5/harness/roster.json").read_text())
etier = {a["id"]: a["tier"] for a in r5["agents"]}
truth, ostd = {}, {}
for t, dm in p5["ratings"].items():
    if "A" in dm:
        ev = [v for a, v in dm["A"].items() if etier.get(a) == "expert" and v != "abstain"]
        if len(ev) >= 3:
            truth[t] = st.mean(ev); ostd[t] = st.pstdev(ev)


def pear(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy) if dx and dy else 0.0


ids = sorted(a for a in tier if any(a in items[t] for t in items))
flat = {t: st.mean(items[t].values()) for t in items}
biased_cluster = sorted([t for t in items if t in truth], key=lambda t: -abs(flat[t]-truth[t]))[:18]
anchors = sorted([t for t in biased_cluster if t in truth], key=lambda t: ostd[t])[:10]
held_out = [t for t in biased_cluster if t not in set(anchors)]


def fit_affine(a, anchor_truth):
    """Ridge-regularized least squares of truth on rating over the anchors."""
    pts = [(items[t][a], anchor_truth[t]) for t in anchors if a in items[t]]
    if len(pts) < 3:
        return 1.0, 0.0, None
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    n = len(pts)
    mx, my = sum(xs)/n, sum(ys)/n
    sxx = sum((x-mx)**2 for x in xs)
    sxy = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    # ridge toward slope 1: minimize sum (y - (a x + b))^2 + LAM (a-1)^2
    slope = (sxy + LAM) / (sxx + LAM)
    inter = my - slope*mx
    resid = [y - (slope*x + inter) for x, y in zip(xs, ys)]
    sd = math.sqrt(sum(r*r for r in resid)/n)
    return slope, inter, sd


def clip(v):
    return max(0.0, min(5.0, v))


def evaluate(cons, keys):
    keys = [t for t in keys if t in truth and t in cons]
    return (pear([cons[t] for t in keys], [truth[t] for t in keys]),
            st.mean([abs(cons[t]-truth[t]) for t in keys]))


def arm_corrected(anchor_truth, weight_mode="uniform"):
    maps = {a: fit_affine(a, anchor_truth) for a in ids}
    cons = {}
    for t, cell in items.items():
        num = den = 0.0
        for a, v in cell.items():
            slope, inter, sd = maps[a]
            cv = clip(slope*v + inter)
            if weight_mode == "invvar" and sd is not None:
                w = 1.0/(sd*sd + 0.05)
            else:
                w = 1.0
            num += w*cv; den += w
        cons[t] = num/den if den else st.mean(cell.values())
    return cons


def arm_flat():
    return {t: st.mean(c.values()) for t, c in items.items()}


print(f"anchors: {len(anchors)} contested items; held-out: {len(held_out)} biased items; "
      f"ridge lam={LAM}\n")
print(f"{'arm':<42} {'held-out corr':>13} {'held-out MAE':>13} {'all-79 corr':>12}")
for name, cons in (
    ("flat unweighted (baseline)", arm_flat()),
    ("affine-corrected, uniform mean", arm_corrected(truth)),
    ("affine-corrected + inv-residual-var wts", arm_corrected(truth, "invvar")),
):
    ho_c, ho_m = evaluate(cons, held_out)
    all_c, _ = evaluate(cons, list(items))
    print(f"{name:<42} {ho_c:>13.2f} {ho_m:>13.2f} {all_c:>12.2f}")
print("\nrecipe reference (analyze_p6.py, trust=0.9 gamma=6): held-out corr 0.90, MAE 0.44")

print("\nrobustness: k worst-case anchors corrupted with the biased flat consensus")
print(f"{'k_bad':>5} {'corrected+invvar corr':>22} {'MAE':>6}")
for k in (0, 1, 2, 3, 4, 5):
    at = dict((t, truth[t]) for t in anchors)
    for t in anchors[:k]:
        at[t] = flat[t]
    cons = arm_corrected(at, "invvar")
    c, m = evaluate(cons, held_out)
    print(f"{k:>5} {c:>22.2f} {m:>6.2f}")
print("\n(compare review/anchor_error_sensitivity.py: the exclusion recipe holds to k=2 then")
print("collapses to strongly-negative by k=4; does correction degrade more gracefully?)")
