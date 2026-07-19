#!/usr/bin/env python3
"""E5 — Cluster-then-adjudicate: discover viewpoint structure WITHOUT an
oracle, then spend external ground truth only on deciding which viewpoint to
trust.

The p6 recipe spends 10 heavily-trusted anchors calibrating every rater. But
the population structure (16 hawks vs 4 evidence-trackers) is in principle
discoverable unsupervised -- raters within a viewpoint agree with each other
more than across. If so, the oracle budget drops from O(raters) to
O(clusters): a couple of anchors to pick the right cluster.

Steps:
  1. Rater-rater agreement matrix (pearson over co-rated items), then spectral
     split (top eigenvector of the centered agreement matrix, sign split).
     Applied to BOTH p6 (should find the hawk/evidence divide) and p5 crowd
     (homogeneous -- should find NO strong divide). The eigengap / split
     "strength" must distinguish the two, or the method hallucinates factions
     where there are none.
  2. Cluster quality vs hidden tiers (p6): does the split recover the tiers?
  3. ADJUDICATION BUDGET: with j = 1..5 anchor items, pick the cluster whose
     within-cluster mean is closer to anchor truth; report how often the
     right cluster wins (over random anchor draws from the contested set,
     and from ALL items).
  4. END-TO-END: consensus = adjudicated winning cluster's flat mean.
     Held-out-biased-items corr vs the full-calibration recipe's +0.90.
  5. NEWCOMER PROBES (no oracle needed): the top between-cluster-separation
     items make an entrance exam; classify each rater into a cluster from j
     probe ratings (nearest centroid, leave-self-out). Tier accuracy vs j.
"""
import math
import random
import statistics as st
from collections import defaultdict
from common import (node_a_matrix, load_roster, p5_oracle, pearson, mean)

RNG = random.Random(20260710)
truth, ostd = p5_oracle()


def agreement_matrix(items, raters):
    co = {a: {} for a in raters}
    for t, cell in items.items():
        for a in cell:
            if a in co:
                co[a][t] = cell[a]
    M = {}
    for i, a in enumerate(raters):
        for b in raters[i + 1:]:
            shared = [t for t in co[a] if t in co[b]]
            if len(shared) >= 8:
                r = pearson([co[a][t] for t in shared], [co[b][t] for t in shared])
                M[(a, b)] = M[(b, a)] = r
    return M


def spectral_split(raters, M, iters=200):
    """Top eigenvector of the (row-centered) agreement matrix via power
    iteration; split by sign. Returns (assignment dict, split_strength)."""
    n = len(raters)
    idx = {a: i for i, a in enumerate(raters)}
    A = [[0.0] * n for _ in range(n)]
    for (a, b), r in M.items():
        A[idx[a]][idx[b]] = r
    # center rows/cols (remove the global "everyone agrees a bit" component)
    rowm = [mean([x for x in row]) for row in A]
    gm = mean(rowm)
    C = [[A[i][j] - rowm[i] - rowm[j] + gm for j in range(n)] for i in range(n)]
    v = [RNG.uniform(-1, 1) for _ in range(n)]
    lam = 0.0
    for _ in range(iters):
        nv = [sum(C[i][j] * v[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(x * x for x in nv)) or 1.0
        v = [x / norm for x in nv]
        lam = sum(v[i] * sum(C[i][j] * v[j] for j in range(n)) for i in range(n))
    # split strength: |lambda_1| / total variance -- how much of the agreement
    # structure one axis explains
    total = sum(C[i][j] ** 2 for i in range(n) for j in range(n)) ** 0.5 or 1.0
    strength = abs(lam) / total
    assign = {a: (1 if v[idx[a]] >= 0 else 0) for a in raters}
    return assign, strength, v


def cluster_means(items, assign, cl):
    out = {}
    for t, cell in items.items():
        vs = [v for a, v in cell.items() if assign.get(a) == cl]
        if vs:
            out[t] = st.mean(vs)
    return out


# ---------------- p6 ----------------
r6 = load_roster("eggs-p6")
tier6 = {a: d["tier"] for a, d in r6.items()}
items6 = node_a_matrix("eggs-p6", restrict_ids=set(r6))
raters6 = sorted({a for c in items6.values() for a in c})
M6 = agreement_matrix(items6, raters6)
assign6, strength6, _ = spectral_split(raters6, M6)

# align cluster label 1 with "competent" for reporting
c1 = [a for a in raters6 if assign6[a] == 1]
if mean([1 if tier6[a] == "competent" else 0 for a in c1]) < 0.5:
    assign6 = {a: 1 - v for a, v in assign6.items()}
comp_cl = [a for a in raters6 if assign6[a] == 1]
bias_cl = [a for a in raters6 if assign6[a] == 0]
acc = mean([1 if (assign6[a] == 1) == (tier6[a] == "competent") else 0 for a in raters6])
print(f"p6 spectral split: strength {strength6:.2f}; clusters {len(comp_cl)}/{len(bias_cl)}; "
      f"tier accuracy {acc:.2f}")

# ---------------- p5 crowd (null case) ----------------
r5 = load_roster("eggs-p5")
crowd5 = {a for a, d in r5.items() if d["tier"] == "crowd"}
items5 = node_a_matrix("eggs-p5", restrict_ids=crowd5)
raters5 = sorted({a for c in items5.values() for a in c})
M5 = agreement_matrix(items5, raters5)
assign5, strength5, _ = spectral_split(raters5, M5)
n1 = sum(1 for a in raters5 if assign5[a] == 1)
print(f"p5 crowd spectral split (null case): strength {strength5:.2f}; "
      f"split {n1}/{len(raters5) - n1}")
print("(a much lower strength on p5 than p6 = the statistic detects real divides "
      "without hallucinating them)\n")

# ---------------- adjudication budget ----------------
mean_comp = cluster_means(items6, assign6, 1)
mean_bias = cluster_means(items6, assign6, 0)
flat6 = {t: st.mean(c.values()) for t, c in items6.items()}
biased_cluster_items = sorted([t for t in items6 if t in truth],
                              key=lambda t: -abs(flat6[t] - truth[t]))[:18]
contested = [t for t in biased_cluster_items]
all_items = [t for t in items6 if t in truth]
# candidate anchor pools: contested (where clusters disagree) vs any item
sep = {t: abs(mean_comp.get(t, 2.5) - mean_bias.get(t, 2.5)) for t in all_items}

print("ADJUDICATION: pick the cluster whose mean is closer to anchor truth on j items")
print(f"{'j':>3} {'pool':<22} {'right-cluster win rate':>23}")
for pool_name, pool in (("contested items", contested),
                        ("all items (random)", all_items),
                        ("top-separation items", sorted(all_items, key=lambda t: -sep[t])[:10])):
    for j in (1, 2, 3, 5):
        wins = trials = 0
        for _ in range(300):
            js = RNG.sample(pool, min(j, len(pool)))
            d_comp = mean([abs(mean_comp[t] - truth[t]) for t in js if t in mean_comp])
            d_bias = mean([abs(mean_bias[t] - truth[t]) for t in js if t in mean_bias])
            if d_comp == d_bias:
                continue
            trials += 1
            wins += 1 if d_comp < d_bias else 0
        print(f"{j:>3} {pool_name:<22} {wins / trials if trials else float('nan'):>23.2f}")
    print()

# ---------------- end-to-end consensus ----------------
anchors10 = sorted(contested, key=lambda t: ostd[t])[:10]
held_out = [t for t in biased_cluster_items if t not in set(anchors10)]


def evaluate(cons, keys):
    keys = [t for t in keys if t in truth and t in cons]
    return (pearson([cons[t] for t in keys], [truth[t] for t in keys]),
            mean([abs(cons[t] - truth[t]) for t in keys]))


# adjudicate with 2 contested anchors (drawn many times), then use winning cluster mean
corrs, maes = [], []
for _ in range(200):
    js = RNG.sample([t for t in contested if t not in held_out] or contested, 2)
    d_comp = mean([abs(mean_comp[t] - truth[t]) for t in js])
    d_bias = mean([abs(mean_bias[t] - truth[t]) for t in js])
    winner = mean_comp if d_comp <= d_bias else mean_bias
    c, m = evaluate(winner, held_out)
    corrs.append(c); maes.append(m)
print("END-TO-END (2-anchor adjudication -> winning cluster's flat mean):")
print(f"  held-out biased items corr {mean(corrs):.2f} ± {st.pstdev(corrs):.2f}, "
      f"MAE {mean(maes):.2f}")
print("  (reference: full 10-anchor calibration recipe reached corr ~0.90, MAE 0.44-0.60;")
print("   oracle-cluster ceiling: winning-cluster mean =",
      f"{evaluate(mean_comp, held_out)[0]:.2f} corr, MAE {evaluate(mean_comp, held_out)[1]:.2f})")

# ---------------- newcomer probes (no oracle) ----------------
print("\nNEWCOMER PROBES: classify a rater into a cluster from j top-separation items")
probe_pool = sorted(all_items, key=lambda t: -sep[t])
accs = {}
for j in (1, 2, 3, 5, 8):
    hits = tot = 0
    for a in raters6:
        # leave-self-out centroids
        mc = cluster_means({t: {x: v for x, v in c.items() if x != a}
                            for t, c in items6.items()}, assign6, 1)
        mb = cluster_means({t: {x: v for x, v in c.items() if x != a}
                            for t, c in items6.items()}, assign6, 0)
        probes = [t for t in probe_pool if a in items6[t]][:j]
        if not probes:
            continue
        dc = mean([abs(items6[t][a] - mc[t]) for t in probes if t in mc])
        db = mean([abs(items6[t][a] - mb[t]) for t in probes if t in mb])
        guess = 1 if dc < db else 0
        hits += 1 if guess == assign6[a] else 0
        tot += 1
    accs[j] = hits / tot
    print(f"  j={j}: cluster-assignment accuracy {hits / tot:.2f}")
print("\n(probes need NO oracle -- only the discovered centroids; the oracle is spent")
print(" once, on adjudication. Newcomer cost: j probe ratings; oracle cost: ~2 anchors.)")
