#!/usr/bin/env python3
"""E6 — Aggregator head-to-head under population stress:
    exclusion (the p6 recipe: anchor-blend reputation, gamma=6)
 vs calibration (per-rater affine on anchors, inverse-residual-variance mean)
 vs cluster-adjudication (E5: winning cluster's flat mean)

on three axes the FLYWHEEL analysis never covered together:
  1. MIN-COMPETENT sweep incl. nc=0: how few genuinely-competent raters does
     each need? Can calibrated BIASED raters alone (nc=0) track truth? (If
     their individual corr with truth is ~0, affine maps can't conjure signal
     for one rater -- but averaging 16 corrected raters cancels idiosyncratic
     noise, so whatever tiny shared truth-signal survives the bias could
     emerge. Measure, don't assume.)
  2. HARM CHECK on the healthy crowd (p5, flat consensus already 0.91): does
     each machine leave a good crowd alone? (analyze_p6's recipe was never
     pointed at a healthy population.)
  3. Anchor-budget sweep: performance at 2..10 anchors.
"""
import random
import statistics as st
from collections import defaultdict
from common import (node_a_matrix, load_roster, p5_oracle, fit_affine, clip5,
                    pearson, mean)

RNG = random.Random(20260710)
truth, ostd = p5_oracle()
PRIOR, K = 0.15, 8.0

r6 = load_roster("eggs-p6")
tier6 = {a: d["tier"] for a, d in r6.items()}
items6_full = node_a_matrix("eggs-p6", restrict_ids=set(r6))
flat6 = {t: st.mean(c.values()) for t, c in items6_full.items()}
biased_cluster = sorted([t for t in items6_full if t in truth],
                        key=lambda t: -abs(flat6[t] - truth[t]))[:18]
anchors10 = sorted(biased_cluster, key=lambda t: ostd[t])[:10]
held_out = [t for t in biased_cluster if t not in set(anchors10)]
all_biased = sorted(a for a in tier6 if tier6[a] == "biased")
all_comp = sorted(a for a in tier6 if tier6[a] == "competent")


def evaluate(cons, keys):
    keys = [t for t in keys if t in truth and t in cons]
    if len(keys) < 3:
        return float("nan"), float("nan")
    return (pearson([cons[t] for t in keys], [truth[t] for t in keys]),
            mean([abs(cons[t] - truth[t]) for t in keys]))


def agg_exclusion(items, raters, anchors, gamma=6.0, blend=0.9):
    """The analyze_p6.py recipe."""
    n_given = {a: sum(1 for t in items if a in items[t]) for a in raters}
    anch = {}
    for a in raters:
        pts = [abs(items[t][a] - truth[t]) / 5 for t in anchors if t in items and a in items[t]]
        anch[a] = (1 - sum(pts) / len(pts)) if pts else None

    def wcons(w):
        out = {}
        for t, c in items.items():
            num = den = 0.0
            for a, v in c.items():
                wa = w.get(a, PRIOR) ** gamma
                num += wa * v; den += wa
            out[t] = num / den if den else st.mean(c.values())
        return out
    w = {a: PRIOR for a in raters}
    for _ in range(30):
        cons = wcons(w)
        by = defaultdict(list)
        for t, c in items.items():
            for a, v in c.items():
                by[a].append((v, cons[t]))
        disc = {a: pearson([p[0] for p in pr], [p[1] for p in pr])
                for a, pr in by.items() if len(pr) >= 5}
        neww = {}
        for a in raters:
            d = max(0.0, disc.get(a, 0.0))
            an = anch.get(a)
            raw = (blend * an + (1 - blend) * d) if an is not None else d
            conf = n_given[a] / (n_given[a] + K)
            neww[a] = PRIOR + conf * (raw - PRIOR)
        if max(abs(neww[a] - w[a]) for a in raters) < 1e-4:
            w = neww; break
        w = neww
    return wcons(w)


def agg_calibration(items, raters, anchors, anchor_truth=None):
    at = anchor_truth or truth
    maps = {}
    for a in raters:
        pts = [(items[t][a], at[t]) for t in anchors if t in items and a in items[t]]
        maps[a] = fit_affine([p[0] for p in pts], [p[1] for p in pts])
    cons = {}
    for t, cell in items.items():
        num = den = 0.0
        for a, v in cell.items():
            s, b, sd = maps[a]
            w = 1.0 / (sd * sd + 0.05) if sd is not None else 1.0
            num += w * clip5(s * v + b); den += w
        if den:
            cons[t] = num / den
    return cons


def agg_cluster(items, raters, anchors_for_adjudication):
    """E5 machinery, self-contained: spectral-ish 2-split via seeded k-means on
    agreement profiles (simpler + fine at these sizes), adjudicate with the
    given anchors, return winning cluster's flat mean."""
    # rating profile per rater
    prof = {a: {} for a in raters}
    for t, cell in items.items():
        for a, v in cell.items():
            if a in prof:
                prof[a][t] = v
    # agreement to two seed raters: the pair with LOWEST mutual agreement
    pairs = []
    rl = list(raters)
    for i, a in enumerate(rl):
        for b in rl[i + 1:]:
            shared = [t for t in prof[a] if t in prof[b]]
            if len(shared) >= 8:
                pairs.append((pearson([prof[a][t] for t in shared],
                                      [prof[b][t] for t in shared]), a, b))
    if not pairs:
        return {t: st.mean(c.values()) for t, c in items.items()}
    _, s1, s2 = min(pairs)
    assign = {}
    for a in raters:
        def agree(b):
            shared = [t for t in prof[a] if t in prof[b]]
            return pearson([prof[a][t] for t in shared], [prof[b][t] for t in shared]) \
                if len(shared) >= 8 else 0.0
        assign[a] = 1 if agree(s1) >= agree(s2) else 0

    def cmean(cl):
        out = {}
        for t, cell in items.items():
            vs = [v for a, v in cell.items() if assign.get(a) == cl]
            if vs:
                out[t] = st.mean(vs)
        return out
    m1, m0 = cmean(1), cmean(0)
    d1 = mean([abs(m1[t] - truth[t]) for t in anchors_for_adjudication if t in m1])
    d0 = mean([abs(m0[t] - truth[t]) for t in anchors_for_adjudication if t in m0])
    return m1 if d1 <= d0 else m0


# ---------------- 1. min-competent sweep ----------------
print("MIN-COMPETENT SWEEP (16 biased fixed; nc competent; 10 anchors; held-out biased items)")
print(f"{'nc':>3} {'exclusion g=6':>14} {'calibration':>12} {'cluster-adj(2a)':>16}")
from itertools import combinations
adj_anchors = anchors10[:2]
for nc in (0, 1, 2, 3, 4):
    ex, ca, cl = [], [], []
    combos = list(combinations(all_comp, nc)) if nc else [()]
    for cc in combos:
        raters = list(cc) + all_biased
        sub = {t: {a: v for a, v in c.items() if a in raters} for t, c in items6_full.items()}
        sub = {t: c for t, c in sub.items() if len(c) >= 5}
        ex.append(evaluate(agg_exclusion(sub, raters, anchors10), held_out)[0])
        ca.append(evaluate(agg_calibration(sub, raters, anchors10), held_out)[0])
        cl.append(evaluate(agg_cluster(sub, raters, adj_anchors), held_out)[0])
    print(f"{nc:>3} {mean(ex):>8.2f}±{st.pstdev(ex) if len(ex) > 1 else 0:>4.2f} "
          f"{mean(ca):>7.2f}±{st.pstdev(ca) if len(ca) > 1 else 0:>4.2f} "
          f"{mean(cl):>11.2f}±{st.pstdev(cl) if len(cl) > 1 else 0:>4.2f}")
print("(nc=0: NO competent raters at all — anything >0 here is signal extracted from")
print(" the biased 16 alone. min_competent_fraction.py found exclusion needs >=2.)\n")

# ---------------- 2. harm check on the healthy p5 crowd ----------------
r5 = load_roster("eggs-p5")
crowd5 = sorted(a for a, d in r5.items() if d["tier"] == "crowd")
items5 = node_a_matrix("eggs-p5", restrict_ids=set(crowd5))
flat5 = {t: st.mean(c.values()) for t, c in items5.items()}
bc5 = sorted([t for t in items5 if t in truth], key=lambda t: -abs(flat5[t] - truth[t]))[:18]
anchors5 = sorted(bc5, key=lambda t: ostd[t])[:10]
eval_all5 = [t for t in items5 if t in truth and t not in set(anchors5)]

print("HARM CHECK — healthy p5 crowd (flat consensus is already good). corr / MAE on all")
print("non-anchor items:")
for name, cons in (
    ("flat mean", {t: st.mean(c.values()) for t, c in items5.items()}),
    ("exclusion g=6", agg_exclusion(items5, crowd5, anchors5)),
    ("calibration", agg_calibration(items5, crowd5, anchors5)),
    ("cluster-adj(2a)", agg_cluster(items5, crowd5, anchors5[:2])),
):
    c, m = evaluate(cons, eval_all5)
    print(f"  {name:<16} corr {c:.3f}  MAE {m:.3f}")
print()

# ---------------- 3. anchor-budget sweep (p6, full population) ----------------
print("ANCHOR-BUDGET SWEEP (p6 full 20 raters; held-out = biased cluster minus the 10):")
print(f"{'n_anchors':>9} {'exclusion':>10} {'calibration':>12} {'cluster-adj':>12}")
for na in (2, 3, 5, 7, 10):
    aset = anchors10[:na]
    ex = evaluate(agg_exclusion(items6_full, sorted(tier6), aset), held_out)[0]
    ca = evaluate(agg_calibration(items6_full, sorted(tier6), aset), held_out)[0]
    cl = evaluate(agg_cluster(items6_full, sorted(tier6), aset[:2]), held_out)[0]
    print(f"{na:>9} {ex:>10.2f} {ca:>12.2f} {cl:>12.2f}")
print("\n(calibration needs >=3 anchor points per rater for the affine fit; at 2 anchors")
print(" it falls back toward identity maps -> expect degradation there.)")
