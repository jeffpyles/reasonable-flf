#!/usr/bin/env python3
"""Split-half reliability + SEM precision on the four v2 flagship graphs.

For each graph, per node-Agreement (dim A) target we have {agent: value}. Two
complementary measures of "how many raters until the aggregate is trustworthy":

  (1) RELATIVE reliability -- split each target's raters into two disjoint halves
      of size p/2, mean each half, Pearson-correlate the two half-means ACROSS
      targets; Spearman-Brown up -> reliability of a p-rater aggregate's ORDERING
      of nodes. Averaged over many seeded splits. Reported as a curve over p.
  (2) ABSOLUTE precision -- SEM = per-target stdev / sqrt(n): how tightly the
      mean itself is pinned on the 0-5 scale. Reported at the current median n,
      plus the n implied to reach SEM targets (from the pooled rater stdev).

Unweighted means (these graphs are anchor-free, so the published True_R-weighted
aggregate ~= the plain mean anyway). Deterministic: fixed RNG seed.

Run from v0/:
  python3 v2-reliability/splithalf.py covid-graph-v2 eggs-graph-v2 blackholes-graph-v2 debate-graph-v2
"""
import math
import random
import statistics as st
import sys
from pathlib import Path

V0 = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(V0))
from reasonable import store            # noqa: E402
from reasonable.fold import fold        # noqa: E402

TRIALS = 300
SEED = 20260718


def node_A_ratings(data_dir):
    """{target: {agent: float}} for numeric dim-A ratings on n-nodes (current era)."""
    state = fold(store.read_events(V0 / data_dir))
    out = {}
    for target, dmap in state["ratings"].items():
        if not target.startswith("n") or "A" not in dmap:
            continue
        cell = {a: float(v) for a, v in dmap["A"].items()
                if v != "abstain" and isinstance(v, (int, float))}
        if len(cell) >= 2:
            out[target] = cell
    return out


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return None
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def reliability_at(ratings, p, rng):
    """Spearman-Brown reliability of a p-rater aggregate (targets with >= p raters)."""
    half = p // 2
    pool = {t: list(v.values()) for t, v in ratings.items() if len(v) >= p}
    if len(pool) < 3:
        return None, len(pool)
    rs = []
    for _ in range(TRIALS):
        xa, xb = [], []
        for vals in pool.values():
            picks = rng.sample(vals, p)
            xa.append(sum(picks[:half]) / half)
            xb.append(sum(picks[half:]) / half)
        r = pearson(xa, xb)
        if r is not None:
            rs.append(r)
    if not rs:
        return None, len(pool)
    r_half = sum(rs) / len(rs)
    return (2 * r_half / (1 + r_half)) if (1 + r_half) else None, len(pool)


def analyze(data_dir):
    ratings = node_A_ratings(data_dir)
    counts = sorted(len(v) for v in ratings.values())
    med_n = int(st.median(counts))
    stdevs = [st.stdev(list(v.values())) for v in ratings.values() if len(v) >= 2]
    pooled_sd = st.median(stdevs)
    sems = [st.stdev(list(v.values())) / math.sqrt(len(v)) for v in ratings.values() if len(v) >= 2]
    mean_sem = sum(sems) / len(sems)
    print(f"\n=== {data_dir} ===")
    print(f"  targets(dim A): {len(ratings)} | rater-count per target: "
          f"min {counts[0]} / median {med_n} / max {counts[-1]}")
    print(f"  pooled per-item rater stdev (median): {pooled_sd:.2f}  |  mean SEM at current n: {mean_sem:.3f}")
    rng = random.Random(SEED)
    reached = {}
    print("  split-half reliability (ordering of nodes) vs panel size p:")
    for p in range(4, min(counts[-1], 24) + 1, 2):
        rel, npool = reliability_at(ratings, p, rng)
        if rel is None:
            continue
        for thr in (0.7, 0.8, 0.9):
            if thr not in reached and rel >= thr:
                reached[thr] = p
        print(f"    p={p:>2}: reliability={rel:.3f}  ({npool} targets have >= {p} raters)")
    for thr in (0.7, 0.8, 0.9):
        print(f"  -> reliable ordering at {thr}: p = {reached.get(thr, '> measurable range')}")
    print(f"  absolute precision -- n needed for a given SEM (n=(sd/SEM)^2, sd={pooled_sd:.2f}):")
    for tgt in (0.35, 0.30, 0.25, 0.20):
        print(f"    SEM<={tgt}: n>={math.ceil((pooled_sd / tgt) ** 2)}")


if __name__ == "__main__":
    graphs = sys.argv[1:] or ["covid-graph-v2", "eggs-graph-v2", "blackholes-graph-v2", "debate-graph-v2"]
    for d in graphs:
        analyze(d)
