#!/usr/bin/env python3
"""eggs-p7 analysis — the mild/graded-divide stress test, run against the real
agent ratings once the workflow completes.

Reuses coldstart-lab/common.py (oracle, competence, clustering pieces) and the
E5/E6/E2 methods, adapted to p7's four tiers (lean_strong, lean_slight, neutral,
competent) and its DESIGN INTENT: the divide is meant to be SOFT. So the script
first checks whether a usable divide even formed, then only reads the
detection/adjudication numbers in that light.

Sections:
  0. Coverage + per-tier oracle accuracy (did the gradient land where intended?)
  1. Divide geometry: accuracy separation between lean camps; per-item
     bimodality (the trigger signal) on contested vs settled items.
  2. Camp detection (E5 spectral split): strength vs the p5 null (0.27) and
     vs p6 (0.83); tier-recovery accuracy. Does the soft divide surface?
  3. Adjudication + calibration (E6): 1-3 anchor camp-pick win rate; per-rater
     un-distortion from a wholly-lean pool; end-to-end held-out repair.
  4. Ranking speed / heterogeneity (E2): split-half reliability of competence
     for this more varied population, and the neutral haiku-vs-sonnet contrast
     (same prompt, two models) — a first real read on how model spread changes
     how fast users can be finely ranked.

Run:  python3 eggs-p7/harness/analyze_p7.py     (from repo root)
"""
import math
import random
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "coldstart-lab"))
from common import (node_a_matrix, load_roster, p5_oracle, oracle_competence,  # noqa
                    pearson, spearman, pctile, mean, fit_affine, clip5)

RNG = random.Random(20260714)
truth, ostd = p5_oracle()
roster = load_roster("eggs-p7")
tier = {a: d["tier"] for a, d in roster.items()}
model = {a: d["model"] for a, d in roster.items()}
LEAN = {"lean_strong", "lean_slight"}
LED = {"neutral", "competent"}

items = node_a_matrix("eggs-p7", restrict_ids=set(tier))
if not items:
    print("No eggs-p7 ratings yet — run the workflow first (workflow_p7.js).")
    sys.exit(0)

comp = oracle_competence(items, truth, min_items=8)
raters = sorted(a for a in tier if a in comp)


# ---------- 0. coverage + per-tier accuracy ----------
def cov(a):
    return sum(1 for t in items if a in items[t])


print(f"=== 0. COVERAGE + PER-TIER ACCURACY (oracle = p5 experts, {len(truth)} nodes) ===")
print(f"{len(raters)} raters scored; mean coverage {mean([cov(a) for a in raters]):.0f}/79 nodes")
for tg in ("lean_strong", "lean_slight", "neutral", "competent"):
    cs = [comp[a] for a in raters if tier[a] == tg]
    if cs:
        print(f"  {tg:<12} n={len(cs):>2}  accuracy mean {mean(cs):+.2f}  "
              f"range {min(cs):+.2f}..{max(cs):+.2f}")
lean_acc = [comp[a] for a in raters if tier[a] in LEAN]
led_acc = [comp[a] for a in raters if tier[a] in LED]
gap = mean(led_acc) - mean(lean_acc)
print(f"\n  evidence-led minus lean accuracy gap: {gap:+.2f}")
if gap < 0.1:
    print("  -> divide is VERY soft / absent (leans stayed accurate). Detection is expected to")
    print("     read ~null; the informative result is then 'no camps to find', not a failure.")
elif gap < 0.4:
    print("  -> divide landed in the intended HARD MIDDLE zone (real but soft). This is the test.")
else:
    print("  -> divide is fairly strong (closer to p6). Detection should be easy; note it read hard.")


# ---------- 1. divide geometry + bimodality trigger ----------
print("\n=== 1. DIVIDE GEOMETRY + BIMODALITY TRIGGER ===")
flat = {t: mean(items[t].values()) for t in items}
# contested = flat consensus farthest from oracle truth
contested = sorted([t for t in items if t in truth], key=lambda t: -abs(flat[t] - truth[t]))[:18]
settled = sorted([t for t in items if t in truth], key=lambda t: abs(flat[t] - truth[t]))[:18]


def dip(vals):
    """Cheap bimodality proxy: stdev, plus the gap between the two halves' means
    (a two-humped item has a big between-half gap relative to within-half sd)."""
    if len(vals) < 6:
        return 0.0, 0.0
    s = sorted(vals)
    h = len(s) // 2
    lo, hi = s[:h], s[h:]
    between = mean(hi) - mean(lo)
    within = (st.pstdev(lo) + st.pstdev(hi)) / 2 or 0.01
    return st.pstdev(vals), between / within


for label, keys in (("contested", contested), ("settled", settled)):
    sds = [st.pstdev(list(items[t].values())) for t in keys if len(items[t]) >= 6]
    ratios = [dip(list(items[t].values()))[1] for t in keys if len(items[t]) >= 6]
    print(f"  {label:<10} mean stdev {mean(sds):.2f}   mean between/within-half {mean(ratios):.2f}")
print("  (trigger works if contested items show higher stdev AND higher between/within than settled)")


# ---------- 2. camp detection (E5 spectral split) ----------
def agreement_matrix(items, raters):
    prof = {a: {} for a in raters}
    for t, cell in items.items():
        for a in cell:
            if a in prof:
                prof[a][t] = cell[a]
    M = {}
    for i, a in enumerate(raters):
        for b in raters[i + 1:]:
            shared = [t for t in prof[a] if t in prof[b]]
            if len(shared) >= 8:
                M[(a, b)] = M[(b, a)] = pearson([prof[a][t] for t in shared],
                                                [prof[b][t] for t in shared])
    return M


def spectral_split(raters, M, seed, iters=400):
    n = len(raters)
    idx = {a: i for i, a in enumerate(raters)}
    A = [[0.0] * n for _ in range(n)]
    for (a, b), r in M.items():
        A[idx[a]][idx[b]] = r
    rowm = [mean(row) for row in A]
    gm = mean(rowm)
    C = [[A[i][j] - rowm[i] - rowm[j] + gm for j in range(n)] for i in range(n)]
    rng = random.Random(seed)
    v = [rng.uniform(-1, 1) for _ in range(n)]
    for _ in range(iters):
        nv = [sum(C[i][j] * v[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(x * x for x in nv)) or 1.0
        v = [x / norm for x in nv]
    lam = sum(v[i] * sum(C[i][j] * v[j] for j in range(n)) for i in range(n))
    total = math.sqrt(sum(C[i][j] ** 2 for i in range(n) for j in range(n))) or 1.0
    return {a: (1 if v[idx[a]] >= 0 else 0) for a in raters}, abs(lam) / total


print("\n=== 2. CAMP DETECTION (spectral split; ref: p5 null 0.27, p6 divide 0.83) ===")
M = agreement_matrix(items, raters)
# The soft-divide regime makes the top two eigenvalues close, so a single
# power-iteration restart is seed-unstable. Run many restarts: report the
# recovery distribution AND a co-association consensus (how often each pair
# lands together) as the stability measure.
N_RESTART = 40
recs, strengths, assigns = [], [], []
for s in range(N_RESTART):
    asg, strg = spectral_split(raters, M, seed=1000 + s)
    if mean([comp[a] for a in raters if asg[a] == 1]) < \
       mean([comp[a] for a in raters if asg[a] == 0]):
        asg = {a: 1 - v for a, v in asg.items()}
    acc = mean([1 if (asg[a] == 1) == (tier[a] in LED) else 0 for a in raters])
    recs.append(max(acc, 1 - acc))
    strengths.append(strg)
    assigns.append(asg)
# consensus assignment = majority vote per rater across restarts (oriented)
assign = {a: (1 if mean([asg[a] for asg in assigns]) >= 0.5 else 0) for a in raters}
# stability: mean fraction of restarts agreeing with the consensus label
stab = mean([max(mean([asg[a] for asg in assigns]),
                 1 - mean([asg[a] for asg in assigns])) for a in raters])
print(f"  split strength {mean(strengths):.2f}   consensus clusters "
      f"{sum(v for v in assign.values())}/{len(raters) - sum(v for v in assign.values())}")
print(f"  tier recovery over {N_RESTART} restarts: mean {mean(recs):.2f} "
      f"(range {min(recs):.2f}..{max(recs):.2f})")
print(f"  assignment stability: {stab:.2f} (1.0 = every restart agrees)")
# Is the recovered axis DISPOSITION (lean vs led) or MODEL (haiku vs sonnet)?
# They are confounded in this population; the neutral tier (same prompt, both
# models) is the disambiguator.
disp = mean([1 if (assign[a] == 1) == (tier[a] in LED) else 0 for a in raters])
mod = mean([1 if (assign[a] == 1) == (model[a] == "sonnet") else 0 for a in raters])
nh_side = [assign[a] for a in raters if tier[a] == "neutral" and model[a] == "haiku"]
print(f"  axis vs disposition {max(disp, 1 - disp):.2f}  vs model {max(mod, 1 - mod):.2f}; "
      f"neutral-haiku land on {'led' if mean(nh_side) >= 0.5 else 'lean'} side "
      f"({sum(nh_side)}/{len(nh_side)} led) — confound flag")


# ---------- 3. adjudication + calibration ----------
print("\n=== 3. ADJUDICATION + CALIBRATION (soft-divide regime) ===")
anchors = sorted(contested, key=lambda t: ostd[t])[:10]
held_out = [t for t in contested if t not in set(anchors)]


def cluster_means(cl):
    out = {}
    for t, cell in items.items():
        vs = [v for a, v in cell.items() if assign.get(a) == cl]
        if vs:
            out[t] = mean(vs)
    return out


def cluster_means_for(asg, cl):
    out = {}
    for t, cell in items.items():
        vs = [v for a, v in cell.items() if asg.get(a) == cl]
        if vs:
            out[t] = mean(vs)
    return out


# adjudication, averaged over the SAME restart set (so it reflects the real
# clustering instability, not one lucky seed)
print("  adjudication (avg over restarts — does j-anchor pick the truer cluster?):")
for j in (1, 2, 3):
    seed_rates = []
    for asg in assigns:
        m1, m0 = cluster_means_for(asg, 1), cluster_means_for(asg, 0)
        d1 = mean([abs(m1[t] - truth[t]) for t in held_out if t in m1])
        d0 = mean([abs(m0[t] - truth[t]) for t in held_out if t in m0])
        right = 1 if d1 <= d0 else 0
        wins = tot = 0
        for _ in range(60):
            js = RNG.sample(anchors, j)
            dd1 = mean([abs(m1[t] - truth[t]) for t in js if t in m1])
            dd0 = mean([abs(m0[t] - truth[t]) for t in js if t in m0])
            if dd1 == dd0:
                continue
            tot += 1
            wins += 1 if (1 if dd1 <= dd0 else 0) == right else 0
        if tot:
            seed_rates.append(wins / tot)
    print(f"    {j}-anchor: {mean(seed_rates):.2f} (range {min(seed_rates):.2f}.."
          f"{max(seed_rates):.2f}) — 'right cluster' is itself near-tied when the divide is soft")


def calibrate(pool_ids, anchor_truth=None):
    at = anchor_truth or truth
    maps = {}
    for a in pool_ids:
        pts = [(items[t][a], at[t]) for t in anchors if a in items.get(t, {})]
        maps[a] = fit_affine([p[0] for p in pts], [p[1] for p in pts])
    cons = {}
    for t, cell in items.items():
        num = den = 0.0
        for a, v in cell.items():
            if a not in maps:
                continue
            s, b, sd = maps[a]
            w = 1.0 / (sd * sd + 0.05) if sd is not None else 1.0
            num += w * clip5(s * v + b); den += w
        if den:
            cons[t] = num / den
    return cons


def corr_on_held(cons):
    k = [t for t in held_out if t in cons]
    return pearson([cons[t] for t in k], [truth[t] for t in k])


lean_only = [a for a in raters if tier[a] in LEAN]
comp_mean = {t: mean([items[t][a] for a in raters if tier[a] == "competent" and a in items[t]])
             for t in items if any(tier[a] == "competent" and a in items[t] for a in raters)}
flatc = pearson([flat[t] for t in held_out], [truth[t] for t in held_out])
print(f"  held-out contested repair (flat baseline corr {flatc:+.2f}):")
print(f"    calibrate FULL pool (28):        {corr_on_held(calibrate(raters)):+.2f}")
print(f"    calibrate LEAN-only ({len(lean_only)}, nc=0):   {corr_on_held(calibrate(lean_only)):+.2f}"
      f"   <- can the leans alone be un-distorted?")
print(f"    winning-cluster mean (consensus): {corr_on_held(cluster_means(1)):+.2f}"
      f"   <- adjudicated aggregate")
print(f"    oracle competent-tier mean:      {corr_on_held(comp_mean):+.2f}   <- ceiling")


# ---------- 4. ranking speed / heterogeneity (E2) ----------
print("\n=== 4. RANKING SPEED / HETEROGENEITY (E2 split-half; ref: p5 crowd r1~0.013, p6 r1~0.107) ===")


def per_rater_items(ids):
    by = defaultdict(dict)
    for t, cell in items.items():
        if t in truth:
            for a, v in cell.items():
                if a in ids:
                    by[a][t] = v
    return by


def split_half(by, n=200, min_half=6):
    rs = []
    for _ in range(n):
        c1, c2 = {}, {}
        for a, sub in by.items():
            ts = list(sub)
            if len(ts) < 2 * min_half:
                continue
            RNG.shuffle(ts)
            h = len(ts) // 2
            c1[a] = pearson([sub[t] for t in ts[:h]], [truth[t] for t in ts[:h]])
            c2[a] = pearson([sub[t] for t in ts[h:2 * h]], [truth[t] for t in ts[h:2 * h]])
        both = [a for a in c1 if a in c2]
        if len(both) >= 8:
            rs.append(pearson([c1[a] for a in both], [c2[a] for a in both]))
    return mean(rs) if rs else float("nan")


for label, ids in (("all 28", set(raters)),
                   ("leans only (16)", {a for a in raters if tier[a] in LEAN}),
                   ("evidence-led (12)", {a for a in raters if tier[a] in LED})):
    by = per_rater_items(ids)
    rL = split_half(by)
    L = mean([len(s) for s in by.values()]) / 2
    r1 = rL / (L - (L - 1) * rL) if rL == rL and L > 1 else float("nan")
    print(f"  {label:<18} split-half r {rL:+.2f} (L≈{L:.0f})  per-item r1 {r1:.3f}")

# neutral haiku vs sonnet: same prompt, two models
nh = [a for a in raters if tier[a] == "neutral" and model[a] == "haiku"]
ns = [a for a in raters if tier[a] == "neutral" and model[a] == "sonnet"]
if nh and ns:
    print(f"\n  neutral prompt, model contrast (same instructions):")
    print(f"    haiku  (n={len(nh)}): accuracy mean {mean([comp[a] for a in nh]):+.2f}")
    print(f"    sonnet (n={len(ns)}): accuracy mean {mean([comp[a] for a in ns]):+.2f}")
    print("    (a gap here = model tier drives accuracy even at identical prompt/disposition)")

print("\nDone. See eggs-p7/FINDINGS.md for the written synthesis.")
