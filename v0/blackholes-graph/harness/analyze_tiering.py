#!/usr/bin/env python3
"""Model-tiering result on the covid graph (TIERING-TEST-PLAN.md).

Reference = 4 Sonnet lens-raters (bloc b1). Cheap = 16 Haiku lens-raters (bloc
cheap), 4 lenses x 4 seeds. For each cheap-arm size N in {4,8,16} we subsample
STRATIFIED BY LENS (N/4 seeds per lens, so all four lenses stay represented and
only per-lens depth changes), average over draws, and measure vs the Sonnet
reference:
  1. mean-agreement    r(cheap node-mean, Sonnet node-mean)
  2. dispersion-repro   r(cheap node-stdev, Sonnet node-stdev)
  3. verdict            do the two top answers keep their Sonnet ordering?
Node ratings only. Stdlib + reasonable package; re-derivable from committed logs.
"""
import json, math, statistics as st, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
from reasonable import store, queries  # noqa

LENSES = ["ev", "bayes", "skeptic", "physics"]
SONNET = ["ev-s", "bayes-s", "skeptic-s", "physics-s"]
RNG = random.Random(2026)

ev = store.read_events(ROOT / "blackholes-graph")
# per-rater node ratings
R = {}
for e in ev:
    if e["verb"] != "rate":
        continue
    p = e["payload"]
    if p.get("dim") != "A" or not str(p.get("target", "")).startswith("n"):
        continue
    v = p.get("value")
    if not isinstance(v, (int, float)):
        continue
    R.setdefault(e["agent"], {})[p["target"]] = v

nodes = sorted({t for a in R for t in R[a]})
def mean_over(raters, t):
    vals = [R[a][t] for a in raters if t in R[a]]
    return st.mean(vals) if vals else None

sonnet_mean = {t: mean_over(SONNET, t) for t in nodes}
sonnet_std = {t: (st.pstdev([R[a][t] for a in SONNET if t in R[a]])
                  if sum(t in R[a] for a in SONNET) >= 2 else None) for t in nodes}


def pear(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pairs)
    if n < 2:
        return float("nan")
    xs, ys = zip(*pairs)
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy) if dx and dy else float("nan")


def cheap_raters(n_per_lens, draw):
    """Pick n_per_lens seeds per lens (stratified)."""
    picked = []
    for lens in LENSES:
        seeds = [f"{lens}-h{s}" for s in (1, 2, 3, 4)]
        picked += (seeds if n_per_lens >= 4 else RNG.sample(seeds, n_per_lens))
    return picked


print(f"reference: 4 Sonnet lenses (bloc b1) · cheap pool: 16 Haiku (4 lenses x 4 seeds) · {len(nodes)} nodes\n")
print(f"{'N':>3} {'r(mean)':>9} {'r(dispersion)':>14} {'MAE(mean)':>10}   [mean over draws]")
DRAWS = 50
results = {}
for N in (4, 8, 16):
    npl = N // 4
    rm, rd, mae = [], [], []
    draws = 1 if N == 16 else DRAWS
    for d in range(draws):
        raters = cheap_raters(npl, d)
        cm = {t: mean_over(raters, t) for t in nodes}
        cs = {t: (st.pstdev([R[a][t] for a in raters if t in R[a]])
                  if sum(t in R[a] for a in raters) >= 2 else None) for t in nodes}
        rm.append(pear([cm[t] for t in nodes], [sonnet_mean[t] for t in nodes]))
        rd.append(pear([cs[t] for t in nodes], [sonnet_std[t] for t in nodes]))
        pairs = [(cm[t], sonnet_mean[t]) for t in nodes if cm[t] is not None and sonnet_mean[t] is not None]
        mae.append(sum(abs(a-b) for a, b in pairs)/len(pairs))
    results[N] = (st.mean(rm), st.mean(rd), st.mean(mae))
    print(f"{N:>3} {st.mean(rm):>9.3f} {st.mean(rd):>14.3f} {st.mean(mae):>10.3f}")

# verdict preservation on the two top answers
print("\nverdict (the two top-level answers, node Agreement mean):")
allhaiku = [f"{l}-h{s}" for l in LENSES for s in (1, 2, 3, 4)]
for nid, label in (("n001", "LHC cannot destroy Earth"), ("n002", "real catastrophe risk")):
    s = sonnet_mean.get(nid); h = mean_over(allhaiku, nid)
    print(f"  {nid} {label:20} Sonnet {s:.2f}  |  Haiku-16 {h:.2f}")
sv = sonnet_mean["n001"] - sonnet_mean["n002"]
hv = mean_over(allhaiku, "n001") - mean_over(allhaiku, "n002")
print(f"  ordering: Sonnet n001-n002 = {sv:+.2f}, Haiku = {hv:+.2f} -> "
      f"{'PRESERVED' if (sv>0)==(hv>0) else 'FLIPPED'}")
