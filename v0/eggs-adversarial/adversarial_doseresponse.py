#!/usr/bin/env python3
"""Adversarial dose-response — at what fraction of coordinated attackers does the
assessment machinery break, and which defense fails first?

DEFENSIVE security research: we red-team our OWN aggregation to find its breaking
point and harden it. Done fully OFFLINE (no agent run) so we can sweep the whole
attacker-fraction curve and every attack type cheaply and conservatively.

Honest base: 42 REAL good-faith neutral raters (pooled p8/p9/p10, all blind, all
79 nodes). Oracle: eggs-p5 expert panel. Attack goal: push the graph's verdict
toward "eggs are dangerous" (the real-world cholesterol-hawk brigade direction).

Attack types (each swept 0 -> majority attacker fraction):
  naive       : rate the attack pole on every node (real p6 cholesterol-hawk
                ratings used where available; else synthesized). Fails anchors.
  jittered    : attack pole + noise, to blur the cluster and evade detection.
  sleeper     : rate HONESTLY on anchors + most nodes, lie ONLY on the target
                (contested) nodes -- the sophisticated attacker that games the
                calibration gate. The real threat.
  sybil       : many identical low-effort copies of the naive vector (count-swamp).

Defenses tested (each a different aggregation of the mixed population):
  flat        : unweighted mean (no defense) -- baseline.
  calibrated  : per-rater affine calibration on external anchors + inverse-
                residual-variance weight (our recommended aggregator).
  superlinear : calibrated reputation raised to gamma (concentrate on the trusted).
Plus DETECTION: does spectral camp-detection flag the attacker bloc as a cluster
(recall/precision vs fraction) -- detection is valuable even where correction fails.

Metric: consensus-vs-oracle correlation + MAE on the TARGET nodes (where the
attack concentrates). Breakdown fraction = where a defense's target-node corr
falls below a usable threshold.
"""
import math
import random
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "coldstart-lab"))
from common import (node_a_matrix, load_roster, p5_oracle, oracle_competence,  # noqa
                    fit_affine, clip5, pearson, mean)

RNG = random.Random(20260715)
truth, ostd = p5_oracle()
NODES = [f"n{i:03d}" for i in range(1, 80)]

# ---------- honest base: 42 real neutral raters, pooled ----------
honest = {}
for run in ("eggs-p8", "eggs-p9", "eggs-p10"):
    r = load_roster(run)
    items = node_a_matrix(run, restrict_ids=set(r))
    for a, d in r.items():
        if d["disposition"] != "neutral":
            continue
        rated = {t: items[t][a] for t in items if a in items[t]}
        if len(rated) >= 70:
            honest[f"{run}:{a}"] = rated
HON = list(honest)

# ---------- attack model: per-node attack pole, from real p6 hawk direction ----------
p6 = node_a_matrix("eggs-p6", restrict_ids=set(load_roster("eggs-p6")))
r6 = load_roster("eggs-p6")
p6_biased = {t: mean([p6[t][a] for a in p6[t] if r6[a]["tier"] == "biased"])
             for t in p6 if any(r6[a]["tier"] == "biased" for a in p6[t])}
honest_flat = {t: mean([honest[h][t] for h in HON if t in honest[h]]) for t in NODES}
# attack pole = the extreme in the direction the p6 hawks pushed vs honest
attack_pole = {}
for t in NODES:
    if t in p6_biased:
        attack_pole[t] = 5.0 if p6_biased[t] >= honest_flat[t] else 0.0
    else:
        attack_pole[t] = 0.0 if honest_flat.get(t, 2.5) >= 2.5 else 5.0

# real p6 hawk rating vectors (for the "naive = real coordinated bias" template)
p6_hawks = [a for a in r6 if r6[a]["tier"] == "biased"]
hawk_vecs = [{t: p6[t][a] for t in p6 if a in p6[t]} for a in p6_hawks]

# ---------- anchors + target nodes ----------
contested = sorted([t for t in NODES if t in truth],
                   key=lambda t: -abs(honest_flat[t] - truth[t]))[:18]
anchors = sorted([t for t in contested if t in truth], key=lambda t: ostd[t])[:10]
anchor_set = set(anchors)
target_nodes = [t for t in contested if t not in anchor_set]  # where the attack bites, off-anchor


# ---------- attacker generators ----------
def mk_naive(i):
    # reuse a real p6 hawk vector if available, else the pole
    if i < len(hawk_vecs):
        v = dict(hawk_vecs[i])
        for t in NODES:
            v.setdefault(t, attack_pole[t])
        return v
    return {t: attack_pole[t] for t in NODES}


def mk_jittered(i):
    return {t: clip5(attack_pole[t] + RNG.gauss(0, 0.8)) for t in NODES}


def mk_sleeper(i):
    base = honest[HON[i % len(HON)]]  # copy an honest rater
    v = {t: base.get(t, honest_flat[t]) for t in NODES}
    for t in target_nodes:            # lie ONLY on target nodes; anchors stay honest
        v[t] = attack_pole[t]
    return v


def mk_sybil(i):
    return {t: attack_pole[t] for t in NODES}  # identical clones


ATTACKS = {"naive": mk_naive, "jittered": mk_jittered, "sleeper": mk_sleeper, "sybil": mk_sybil}


# ---------- defenses (aggregators over a mixed rater set) ----------
def calibrate(pool):
    maps = {}
    for a, vec in pool:
        pts = [(vec[t], truth[t]) for t in anchors if t in vec]
        maps[a] = fit_affine([p[0] for p in pts], [p[1] for p in pts])
    return maps


def agg_flat(pool):
    return {t: mean([vec[t] for _, vec in pool if t in vec]) for t in NODES}


def agg_calibrated(pool, gamma=1.0):
    maps = calibrate(pool)
    cons = {}
    for t in NODES:
        num = den = 0.0
        for a, vec in pool:
            if t not in vec:
                continue
            s, b, sd = maps[a]
            w = (1.0 / (sd * sd + 0.05)) ** gamma if sd is not None else 1.0
            num += w * clip5(s * vec[t] + b); den += w
        if den:
            cons[t] = num / den
    return cons


def target_metrics(cons):
    """MAE and verdict-capture on target nodes. Correlation is offset-invariant
    so it HIDES a coordinated level-shift attack — MAE and verdict-flip are what
    reveal a capture. verdict-flip = fraction of target nodes whose true/false
    verdict (relative to the 2.5 midpoint) got flipped by the consensus."""
    k = [t for t in target_nodes if t in cons and t in truth]
    mae = mean([abs(cons[t] - truth[t]) for t in k])
    flips = mean([1 if (cons[t] - 2.5) * (truth[t] - 2.5) < 0 else 0 for t in k])
    return mae, flips


# ---------- camp-detection (does it flag the attacker bloc?) ----------
def detect_attackers(pool, attacker_ids):
    ids = [a for a, _ in pool]
    prof = {a: v for a, v in pool}
    n = len(ids); idx = {a: i for i, a in enumerate(ids)}
    A = [[0.0] * n for _ in range(n)]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            sh = [t for t in prof[a] if t in prof[b]]
            if len(sh) >= 8:
                A[idx[a]][idx[b]] = A[idx[b]][idx[a]] = pearson([prof[a][t] for t in sh],
                                                                [prof[b][t] for t in sh])
    rowm = [mean(r) for r in A]; gm = mean(rowm)
    C = [[A[i][j] - rowm[i] - rowm[j] + gm for j in range(n)] for i in range(n)]
    v = [RNG.uniform(-1, 1) for _ in range(n)]
    for _ in range(300):
        nv = [sum(C[i][j] * v[j] for j in range(n)) for i in range(n)]
        nm = math.sqrt(sum(x * x for x in nv)) or 1.0; v = [x / nm for x in nv]
    # the cluster more enriched in attackers = the "flagged" cluster
    c1 = [a for a in ids if v[idx[a]] >= 0]; c0 = [a for a in ids if v[idx[a]] < 0]
    f1 = mean([1 if a in attacker_ids else 0 for a in c1]) if c1 else 0
    f0 = mean([1 if a in attacker_ids else 0 for a in c0]) if c0 else 0
    flagged = set(c1 if f1 >= f0 else c0)
    tp = len(flagged & attacker_ids)
    recall = tp / len(attacker_ids) if attacker_ids else float("nan")
    prec = tp / len(flagged) if flagged else float("nan")
    return recall, prec


# ---------- the sweep ----------
h_mae, h_flip = target_metrics(agg_flat([(h, honest[h]) for h in HON]))
print(f"honest base: {len(HON)} real neutral raters | anchors: {len(anchors)} | "
      f"target nodes: {len(target_nodes)}")
print(f"honest-only target-node MAE {h_mae:.2f}, verdict-flips {h_flip:.0%} (the clean baseline)\n")
print("MAE on target nodes (lower=better; ~2+ = captured) and [verdict-flip %]:")
print(f"{'attack':<9}{'f':>5}  {'flat':>13}{'calibrated':>13}{'superlin g4':>13}  {'detect rec/prec':>16}")
for atk, gen in ATTACKS.items():
    for f in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
        n_a = round(f / (1 - f) * len(HON))
        pool = [(h, honest[h]) for h in HON] + [(f"ATK_{atk}_{i}", gen(i)) for i in range(n_a)]
        attacker_ids = {a for a, _ in pool if a.startswith("ATK_")}
        fm, ff = target_metrics(agg_flat(pool))
        cm, cf = target_metrics(agg_calibrated(pool, 1.0))
        sm, sf = target_metrics(agg_calibrated(pool, 4.0))
        rec, prec = detect_attackers(pool, attacker_ids)
        print(f"{atk:<9}{f:>5.1f}  {fm:>6.2f}[{ff:>3.0%}]{cm:>7.2f}[{cf:>3.0%}]{sm:>7.2f}[{sf:>3.0%}]"
              f"  {rec:>7.2f}/{prec:.2f}")
    print()
print("MAE >~2 or verdict-flips >0 = the attack captured the target verdicts. detect rec/prec =")
print("did camp-detection flag the attacker bloc (recall=caught, prec=purity) even where correction failed.")
