#!/usr/bin/env python3
"""E10 — Tune the "spin up the contested-region machinery" trigger.

Every prior finding said: don't fire camp-detection/adjudication/calibration off
a global population-structure score (it under-reads real divides); fire it per
ITEM off the shape of that item's rating distribution (the v1.4 histogram data).
This turns "two-humped → fire" from a vibe into a calibrated threshold.

Method: pool every rated node across the three regimes on the shared 79 node ids
  - p5 crowd  (52, homogeneous good-faith — NO real divide → the false-positive test)
  - p6        (20, strong shared bias → the divide the machinery must catch)
  - p7        (28, soft graded bias → the hard middle)
For each item compute two cheap distribution stats a live site already has:
  - stdev of the raw ratings
  - Sarle's bimodality coefficient BC = (skew^2 + 1)/kurtosis  (≈0.56 uniform,
    →1 as a distribution splits into two humps; >0.555 is the textbook flag)
Label each item by whether the machinery is actually NEEDED there = the flat
(unweighted) consensus is far from oracle truth (p5 8-expert panel). Then find a
threshold that catches the high-error items while rarely firing on p5 (where
firing is wasted). Report precision/recall so the trigger is a defensible number.
"""
import statistics as st
from collections import defaultdict
from common import node_a_matrix, load_roster, p5_oracle, pearson, mean

truth, _ = p5_oracle()
ERR_HI = 1.0   # |flat - truth| above this = the crowd is meaningfully wrong here


def bimodality_coefficient(vals):
    n = len(vals)
    if n < 4:
        return None
    m = mean(vals)
    m2 = sum((v - m) ** 2 for v in vals) / n
    if m2 == 0:
        return None
    m3 = sum((v - m) ** 3 for v in vals) / n
    m4 = sum((v - m) ** 4 for v in vals) / n
    skew = m3 / (m2 ** 1.5)
    kurt = m4 / (m2 ** 2)                       # Pearson (non-excess) kurtosis
    return (skew ** 2 + 1) / kurt


def collect(run, restrict=None):
    roster = load_roster(run)
    ids = set(roster) if restrict is None else {a for a in roster if roster[a]["tier"] in restrict}
    items = node_a_matrix(run, restrict_ids=ids)
    rows = []
    for t, cell in items.items():
        if t not in truth or len(cell) < 6:
            continue
        vals = list(cell.values())
        flat = mean(vals)
        rows.append({
            "run": run, "item": t, "n": len(vals),
            "stdev": st.pstdev(vals),
            "bc": bimodality_coefficient(vals),
            "err": abs(flat - truth[t]),
        })
    return rows


rows = (collect("eggs-p5", restrict={"crowd"})
        + collect("eggs-p6")
        + collect("eggs-p7"))
rows = [r for r in rows if r["bc"] is not None]

print(f"pooled items: {len(rows)}  "
      f"(p5 {sum(r['run']=='eggs-p5' for r in rows)}, "
      f"p6 {sum(r['run']=='eggs-p6' for r in rows)}, "
      f"p7 {sum(r['run']=='eggs-p7' for r in rows)})")
print(f"'machinery needed' = |flat-truth| > {ERR_HI}: "
      f"{sum(r['err'] > ERR_HI for r in rows)} of {len(rows)} items\n")

# how well does each stat rank the high-error items?
for stat in ("stdev", "bc"):
    xs = [r[stat] for r in rows]
    ys = [r["err"] for r in rows]
    print(f"corr({stat}, |flat-truth|) = {pearson(xs, ys):+.2f}")

# per-regime mean of each stat, split by needed/not — is the trigger separable?
print(f"\n{'regime':<10}{'items':>6}{'mean stdev':>12}{'mean BC':>10}{'%need':>7}")
for run in ("eggs-p5", "eggs-p6", "eggs-p7"):
    rr = [r for r in rows if r["run"] == run]
    need = [r for r in rr if r["err"] > ERR_HI]
    print(f"{run:<10}{len(rr):>6}{mean([r['stdev'] for r in rr]):>12.2f}"
          f"{mean([r['bc'] for r in rr]):>10.2f}{100*len(need)/len(rr):>6.0f}%")

# threshold sweep on BC and on stdev: precision/recall for catching high-error items
print("\nthreshold sweep — catch |flat-truth|>1.0 items, minimize false fires on settled items")
print(f"{'stat':<7}{'thresh':>7}{'fires':>7}{'precision':>11}{'recall':>8}{'p5 false-fire rate':>20}")
needed = [r for r in rows if r["err"] > ERR_HI]
p5_settled = [r for r in rows if r["run"] == "eggs-p5" and r["err"] <= ERR_HI]
for stat, threshs in (("bc", (0.45, 0.50, 0.555, 0.60, 0.65)),
                      ("stdev", (0.5, 0.7, 0.9, 1.1, 1.3))):
    for th in threshs:
        fires = [r for r in rows if r[stat] >= th]
        tp = sum(r["err"] > ERR_HI for r in fires)
        prec = tp / len(fires) if fires else float("nan")
        rec = tp / len(needed) if needed else float("nan")
        p5ff = sum(r[stat] >= th for r in p5_settled) / len(p5_settled) if p5_settled else float("nan")
        print(f"{stat:<7}{th:>7.3f}{len(fires):>7}{prec:>11.2f}{rec:>8.2f}{p5ff:>20.2f}")

print("""
Reading: precision = of items we fire on, fraction that really need it; recall =
of items that need it, fraction we catch; p5 false-fire = fraction of healthy
homogeneous items we'd needlessly escalate. E9 showed false fires are cheap
(<=0.04 corr cost) and misses are not, so favor RECALL — pick the lowest
threshold whose p5 false-fire rate is still tolerable. The chosen number is the
site's 'contested?' tripwire; combine BC (shape) with a stdev floor (ignore
tight distributions BC can call bimodal on tiny wiggles).""")
