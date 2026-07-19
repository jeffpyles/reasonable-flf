#!/usr/bin/env python3
"""Does the discrimination flywheel turn? — offline test on data in hand.

Bootstrap reputation on the 52 Haiku CROWD only (competence = hidden care label,
high/mid/hasty), starting from a flat prior, using the True_R-weighted fixed-point
with DISCRIMINATION as the rating-quality signal. Two non-circular truth checks,
using the 8 experts (who the crowd never saw) as an INDEPENDENT truth reference:

  (A) reputation sorts competence:  corr(crowd True_R, hidden care) — should RISE
      across fixed-point iterations if the flywheel compounds.
  (B) consensus gets truer:  the True_R-weighted CROWD consensus should move toward
      the EXPERT mean (truth) vs the flat unweighted crowd mean.

Iteration 0 = flat weights (unweighted crowd mean). If A and B improve from
iteration 0 to convergence, the flywheel turns purely in the aggregation — no
re-rating needed for the compounding leg.
"""
import json, math, statistics as st, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parent.parent))
from reasonable import store, fold  # noqa

PRIOR, K = 0.15, 8.0

roster = json.loads((HERE / "roster.json").read_text())
tier = {a["id"]: a["tier"] for a in roster["agents"]}
care_rank = {a["id"]: {"high": 2, "mid": 1, "hasty": 0}.get(a.get("care"))
             for a in roster["agents"] if a["tier"] == "crowd"}

st_ = fold.fold(store.read_events("eggs-p5"))
# node-A items only (dense expert truth). ratings[item][agent]=v
items = {}
for t, dm in st_["ratings"].items():
    if "A" in dm and t.startswith("n"):
        cell = {a: v for a, v in dm["A"].items() if v != "abstain"}
        if cell:
            items[t] = cell

crowd_ids = [a for a in care_rank]
# expert truth per item (mean of expert ratings); keep items with >=3 experts
truth = {}
for t, cell in items.items():
    ev = [v for a, v in cell.items() if tier.get(a) == "expert"]
    if len(ev) >= 3:
        truth[t] = st.mean(ev)
# crowd-only rating view
crowd = {t: {a: v for a, v in cell.items() if tier.get(a) == "crowd"} for t, cell in items.items()}
crowd = {t: c for t, c in crowd.items() if len(c) >= 4}


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy) if dx and dy else 0.0


def rank(vals):
    o = sorted(range(len(vals)), key=lambda i: vals[i]); r = [0.0]*len(vals); i = 0
    while i < len(vals):
        j = i
        while j+1 < len(vals) and vals[o[j+1]] == vals[o[i]]:
            j += 1
        for k in range(i, j+1):
            r[o[k]] = (i+j)/2.0
        i = j+1
    return r


def spearman(xs, ys):
    return pearson(rank(xs), rank(ys))


def weighted_consensus(w):
    cons = {}
    for t, cell in crowd.items():
        num = den = 0.0
        for a, v in cell.items():
            wa = w.get(a, PRIOR)
            num += wa*v; den += wa
        cons[t] = num/den if den else st.mean(cell.values())
    return cons


def discrimination(cons):
    """corr of each crowd rater's values with the LOO-ish weighted consensus."""
    by = defaultdict(list)
    for t, cell in crowd.items():
        for a, v in cell.items():
            by[a].append((v, cons[t]))
    return {a: pearson([p[0] for p in pr], [p[1] for p in pr]) for a, pr in by.items() if len(pr) >= 5}


def consensus_truth_corr(cons):
    keys = [t for t in cons if t in truth]
    return pearson([cons[t] for t in keys], [truth[t] for t in keys]), \
        st.mean([abs(cons[t]-truth[t]) for t in keys])


# EXTERNAL competence per crowd rater: how well their OWN ratings track expert truth
true_comp = {}
for a in crowd_ids:
    pts = [(crowd[t][a], truth[t]) for t in crowd if a in crowd[t] and t in truth]
    if len(pts) >= 5:
        true_comp[a] = pearson([p[0] for p in pts], [p[1] for p in pts])
tc_vals = list(true_comp.values())
print(f"crowd={len(crowd_ids)} raters, {len(crowd)} items, expert-truth on {len(truth)} items")
print(f"external competence (crowd rater's corr with expert truth): "
      f"mean {st.mean(tc_vals):.2f}, range {min(tc_vals):.2f}..{max(tc_vals):.2f} "
      f"(real gradient exists if range is wide)")
# is the care LABEL a valid competence proxy? corr(care, true_comp)
common = [a for a in true_comp if care_rank.get(a) is not None]
print(f"corr(care label, external competence) = "
      f"{spearman([care_rank[a] for a in common],[true_comp[a] for a in common]):.3f} "
      f"(near 0 => the care prompt-label is NOT real rating competence)\n")

n_given = {a: sum(1 for t in crowd if a in crowd[t]) for a in crowd_ids}
w = {a: PRIOR for a in crowd_ids}
print(f"{'iter':>4} {'TrueR~trueComp':>15} {'TrueR~care':>11} {'cons~truth':>11} {'cons MAE':>9} {'max Δw':>8}")
for it in range(0, 8):
    cons = weighted_consensus(w)
    disc = discrimination(cons)
    tc, mae = consensus_truth_corr(cons)
    neww = {}
    for a in crowd_ids:
        raw = max(0.0, disc.get(a, 0.0))          # anti-correlated -> 0
        conf = n_given[a]/(n_given[a]+K)
        neww[a] = PRIOR + conf*(raw - PRIOR)
    dw = max(abs(neww[a]-w[a]) for a in crowd_ids)
    scored = [a for a in disc if a in true_comp]
    rc = spearman([true_comp[a] for a in scored], [neww[a] for a in scored])
    cc = spearman([care_rank[a] for a in scored if care_rank.get(a) is not None],
                  [neww[a] for a in scored if care_rank.get(a) is not None])
    tag = "  <- flat baseline" if it == 0 else ""
    print(f"{it:>4} {rc:>15.3f} {cc:>11.3f} {tc:>11.3f} {mae:>9.3f} {dw:>8.3f}{tag}")
    w = neww
    if dw < 0.001:
        break
print("\nRow 0's consensus columns = FLAT (unweighted crowd mean) baseline.")
print("If corr(TrueR,care) and cons~truth corr RISE (and MAE falls) past row 0, the flywheel turns:")
print("discrimination-weighting sorts the crowd by competence AND pulls their consensus toward expert truth.")
