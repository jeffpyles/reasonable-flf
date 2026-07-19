#!/usr/bin/env python3
"""E3 — Newcomer assessment: which signal identifies a new rater fastest,
per rating spent, and against which reference?

Frame: an ESTABLISHED graph (all other raters at full data) receives one
newcomer who gives only k ratings. For each rater in turn (leave-one-out), we
subsample k of their items (many draws) and score them with each candidate
signal, then ask how well the score recovers their true competence / tier.

Signals compared at each budget k:
  align_flat   : 1 - |v - flat consensus| (the failed live rule)
  disc_flat    : corr with flat (unweighted) LOO consensus  -- self-referential
  disc_fixed   : corr with the ANCHOR-CALIBRATED consensus (the E-bias_correction
                 consensus computed from everyone else) -- the flywheel's gift
                 to newcomer assessment: once the consensus is fixed, tracking
                 it IS tracking truth
  anchor_rand  : agreement with anchor truth on whatever anchors land in a
                 random k (expected k*10/79 hits)
  anchor_routed: the first min(k,10) of the newcomer's items are FORCED to be
                 anchors (the "entrance exam" routing design)

Populations: eggs-p6 (disposition-split; the case that matters) and eggs-p5
crowd (homogeneous; expect everything ceiling-bound per E2).
Metrics over draws: spearman(score, oracle competence) across raters, and the
competent-tier mean percentile (p6 only).
"""
import random
import statistics as st
from collections import defaultdict
from common import (node_a_matrix, load_roster, p5_oracle, oracle_competence,
                    fit_affine, clip5, pearson, spearman, pctile, mean)

RNG = random.Random(20260710)
truth, ostd = p5_oracle()
N_DRAWS = 30


def calibrated_consensus(items, anchors, exclude=None):
    """The review/bias_correction.py aggregator: per-rater ridge affine fit on
    anchors, inverse-residual-variance weights, unweighted across raters
    otherwise. Computed EXCLUDING the newcomer."""
    raters = sorted({a for c in items.values() for a in c if a != exclude})
    maps = {}
    for a in raters:
        pts = [(items[t][a], truth[t]) for t in anchors if a in items.get(t, {})]
        maps[a] = fit_affine([p[0] for p in pts], [p[1] for p in pts])
    cons = {}
    for t, cell in items.items():
        num = den = 0.0
        for a, v in cell.items():
            if a == exclude or a not in maps:
                continue
            s, b, sd = maps[a]
            w = 1.0 / (sd * sd + 0.05) if sd is not None else 1.0
            num += w * clip5(s * v + b)
            den += w
        if den:
            cons[t] = num / den
    return cons


def flat_consensus(items, exclude=None):
    cons = {}
    for t, cell in items.items():
        vs = [v for a, v in cell.items() if a != exclude]
        if vs:
            cons[t] = st.mean(vs)
    return cons


def eval_population(name, run, tier_filter, anchors):
    roster = load_roster(run)
    ids = {a for a, d in roster.items() if tier_filter is None or d["tier"] == tier_filter}
    items = node_a_matrix(run, restrict_ids=ids)
    by = defaultdict(dict)
    for t, cell in items.items():
        if t in truth:
            for a, v in cell.items():
                by[a][t] = v
    comp = oracle_competence(items, truth, min_items=8)
    raters = sorted(a for a in by if a in comp)
    tiers = {a: roster[a]["tier"] for a in raters}

    # per-newcomer references, precomputed once (leave-one-out)
    flat_ref = {a: flat_consensus(items, exclude=a) for a in raters}
    fixed_ref = {a: calibrated_consensus(items, anchors, exclude=a) for a in raters}

    print(f"\n=== {name}: {len(raters)} raters, anchors={len(anchors)} ===")
    print(f"{'k':>4} {'signal':<14} {'spearman~comp':>14}" +
          ("  competent_pctile" if run == "eggs-p6" else ""))
    for k in (4, 6, 10, 15, 20):
        results = defaultdict(list)
        for _ in range(N_DRAWS):
            scores = defaultdict(dict)
            for a in raters:
                own = list(by[a])
                if len(own) < k:
                    continue
                RNG.shuffle(own)
                sub = own[:k]
                # routed: force anchors first
                a_own = [t for t in own if t in anchors]
                routed = (a_own[:min(k, len(a_own))] +
                          [t for t in own if t not in anchors])[:k]

                def sc_align(ts):
                    ds = [abs(by[a][t] - flat_ref[a][t]) / 5 for t in ts if t in flat_ref[a]]
                    return 1 - mean(ds) if ds else None

                def sc_disc(ts, ref):
                    pts = [(by[a][t], ref[t]) for t in ts if t in ref]
                    return pearson([p[0] for p in pts], [p[1] for p in pts]) if len(pts) >= 3 else None

                def sc_anchor(ts):
                    pts = [abs(by[a][t] - truth[t]) / 5 for t in ts if t in anchors]
                    return 1 - mean(pts) if pts else None

                for sig, val in (("align_flat", sc_align(sub)),
                                 ("disc_flat", sc_disc(sub, flat_ref[a])),
                                 ("disc_fixed", sc_disc(sub, fixed_ref[a])),
                                 ("anchor_rand", sc_anchor(sub)),
                                 ("anchor_routed", sc_anchor(routed))):
                    if val is not None:
                        scores[sig][a] = val
            for sig, sc in scores.items():
                common = [a for a in raters if a in sc]
                if len(common) < 10:
                    continue
                results[sig].append(spearman([sc[a] for a in common],
                                             [comp[a] for a in common]))
                if run == "eggs-p6":
                    vals = [sc[a] for a in common]
                    cp = [pctile(sc[a], vals) for a in common if tiers[a] == "competent"]
                    results[sig + "_cp"].append(mean(cp))
        for sig in ("align_flat", "disc_flat", "disc_fixed", "anchor_rand", "anchor_routed"):
            if not results[sig]:
                continue
            row = f"{k:>4} {sig:<14} {mean(results[sig]):>10.2f} ±{st.pstdev(results[sig]):>4.2f}"
            if run == "eggs-p6":
                row += f"   {mean(results[sig + '_cp']):>13.2f}"
            print(row)
        print()


# p6 anchors: the contested set from analyze_p6.py (fixed there, reused here)
r6 = load_roster("eggs-p6")
items6 = node_a_matrix("eggs-p6", restrict_ids=set(r6))
flat6 = {t: st.mean(c.values()) for t, c in items6.items()}
biased_cluster = sorted([t for t in items6 if t in truth],
                        key=lambda t: -abs(flat6[t] - truth[t]))[:18]
anchors6 = sorted(biased_cluster, key=lambda t: ostd[t])[:10]

eval_population("eggs-p6 (disposition-split)", "eggs-p6", None, anchors6)

# p5 crowd anchors: same construction on the p5 crowd's flat consensus
r5 = load_roster("eggs-p5")
crowd5 = {a for a, d in r5.items() if d["tier"] == "crowd"}
items5 = node_a_matrix("eggs-p5", restrict_ids=crowd5)
flat5 = {t: st.mean(c.values()) for t, c in items5.items()}
bc5 = sorted([t for t in items5 if t in truth], key=lambda t: -abs(flat5[t] - truth[t]))[:18]
anchors5 = sorted(bc5, key=lambda t: ostd[t])[:10]

eval_population("eggs-p5 crowd (homogeneous)", "eggs-p5", "crowd", anchors5)

print("""Reading guide: disc_fixed vs disc_flat isolates the value of having FIXED the
consensus first (flywheel benefit to newcomer assessment). anchor_routed vs
anchor_rand isolates the value of ROUTING newcomers through an entrance exam.
E2's ceiling says p5-crowd numbers can't exceed ~0.3-0.5 at these k.""")
