#!/usr/bin/env python3
"""E9 — Soft-divide stress test: where does the contested-region machinery
break as the divide weakens?

E5/E6's constants (1 anchor adjudicates, 1-3 probes classify, calibration
works at nc=0) come from eggs-p6, whose divide is maximal (competence 0.01 vs
0.89). Real divides are softer: partial bias, overlapping clusters. This
sweeps divide strength in a dense synthetic world (eggs-calibrated noise) and
measures, at each softness level:

  harm      : flat-consensus corr on contested items (how much fixing is even
              needed);
  detect    : spectral split strength (E5's statistic) and its tier accuracy;
  adjudicate: win rate of 1/3-anchor cluster adjudication;
  probe     : 3-probe newcomer cluster-classification accuracy;
  calibrate : nc=0-style test -- calibrated+invvar consensus from the BIASED
              raters ONLY, held-out contested corr;
  fix       : end-to-end cluster-adjudicated consensus corr on held-out
              contested items vs flat.

The practical deliverable is the TRIGGER design: does detection strength track
actual harm, so the site knows when to spin up the expensive machinery -- and
in the regime where detection fails, is there anything left to fix?

World: 30 raters (24 biased-leaning, 6 evidence-tracking) x 120 items (30
contested incl. 10 anchors, 20 held-out). bias_w in [0..0.85] scales how far
biased raters' perception is pulled toward the shared wrong target on
contested items. 6 seeds per level.
"""
import math
import random
import statistics as st
from collections import defaultdict
from common import pearson, fit_affine, clip5, mean

N_BIASED, N_COMP = 24, 6
N_ITEMS, N_CONTESTED, N_ANCHORS = 120, 30, 10
CENTER = 2.75
SEEDS = 6


def build(rng, bias_w):
    items = []
    for i in range(N_ITEMS):
        q = rng.uniform(0.3, 4.7)
        contested = i < N_CONTESTED
        b = 5.0 - q if contested else q
        items.append({"q": q, "b": b, "contested": contested})
    raters = ([{"id": f"b{i}", "tier": "biased", "gain": 0.8, "noise": 0.7,
                "bw": bias_w} for i in range(N_BIASED)] +
              [{"id": f"c{i}", "tier": "competent", "gain": 1.0, "noise": 0.5,
                "bw": 0.0} for i in range(N_COMP)])
    ratings = defaultdict(dict)
    for r in raters:
        for i, it in enumerate(items):
            perceived = (1 - r["bw"]) * it["q"] + r["bw"] * it["b"] \
                if it["contested"] else it["q"]
            v = CENTER + r["gain"] * (perceived - CENTER) + rng.gauss(0, r["noise"])
            ratings[i][r["id"]] = max(0.0, min(5.0, v))
    return items, raters, ratings


def spectral(raters, ratings, rng):
    ids = [r["id"] for r in raters]
    prof = {a: {} for a in ids}
    for i, cell in ratings.items():
        for a, v in cell.items():
            prof[a][i] = v
    n = len(ids)
    idx = {a: k for k, a in enumerate(ids)}
    A = [[0.0] * n for _ in range(n)]
    for x, a in enumerate(ids):
        for b in ids[x + 1:]:
            shared = list(prof[a].keys() & prof[b].keys())
            r = pearson([prof[a][t] for t in shared], [prof[b][t] for t in shared])
            A[idx[a]][idx[b]] = A[idx[b]][idx[a]] = r
    rowm = [mean(row) for row in A]
    gm = mean(rowm)
    C = [[A[i][j] - rowm[i] - rowm[j] + gm for j in range(n)] for i in range(n)]
    v = [rng.uniform(-1, 1) for _ in range(n)]
    lam = 0.0
    for _ in range(150):
        nv = [sum(C[i][j] * v[j] for j in range(n)) for i in range(n)]
        norm = math.sqrt(sum(x * x for x in nv)) or 1.0
        v = [x / norm for x in nv]
    lam = sum(v[i] * sum(C[i][j] * v[j] for j in range(n)) for i in range(n))
    total = math.sqrt(sum(C[i][j] ** 2 for i in range(n) for j in range(n))) or 1.0
    assign = {a: (1 if v[idx[a]] >= 0 else 0) for a in ids}
    return assign, abs(lam) / total


def run_level(bias_w):
    agg = defaultdict(list)
    for s in range(SEEDS):
        rng = random.Random(9000 + s)
        items, raters, ratings = build(rng, bias_w)
        truth = {i: items[i]["q"] for i in range(N_ITEMS)}
        anchors = list(range(N_ANCHORS))
        held = list(range(N_ANCHORS, N_CONTESTED))
        tier = {r["id"]: r["tier"] for r in raters}

        flat = {i: st.mean(c.values()) for i, c in ratings.items()}
        agg["harm_flat"].append(pearson([flat[i] for i in held], [truth[i] for i in held]))

        assign, strength = spectral(raters, ratings, rng)
        agg["detect_strength"].append(strength)
        # align cluster 1 with competent majority-vote for accuracy readout
        ids = [r["id"] for r in raters]
        c1_comp = mean([1 if tier[a] == "competent" else 0
                        for a in ids if assign[a] == 1] or [0])
        c0_comp = mean([1 if tier[a] == "competent" else 0
                        for a in ids if assign[a] == 0] or [0])
        if c0_comp > c1_comp:
            assign = {a: 1 - x for a, x in assign.items()}
        acc = mean([1 if (assign[a] == 1) == (tier[a] == "competent") else 0 for a in ids])
        agg["detect_acc"].append(max(acc, 1 - acc))

        def cmean(cl):
            out = {}
            for i, cell in ratings.items():
                vs = [v for a, v in cell.items() if assign[a] == cl]
                if vs:
                    out[i] = st.mean(vs)
            return out
        m1, m0 = cmean(1), cmean(0)
        # adjudication win-rate with j anchors (right cluster = the one whose
        # members are mostly competent... but with soft divides clusters are
        # mixed; "right" = the cluster whose mean tracks truth better on ALL
        # contested items, the thing adjudication is trying to guess from j)
        d1_full = mean([abs(m1[i] - truth[i]) for i in held if i in m1])
        d0_full = mean([abs(m0[i] - truth[i]) for i in held if i in m0])
        right = 1 if d1_full <= d0_full else 0
        for j in (1, 3):
            wins = 0
            for _ in range(60):
                js = rng.sample(anchors, j)
                d1 = mean([abs(m1[i] - truth[i]) for i in js if i in m1])
                d0 = mean([abs(m0[i] - truth[i]) for i in js if i in m0])
                wins += 1 if (1 if d1 <= d0 else 0) == right else 0
            agg[f"adj_{j}"].append(wins / 60)
        # end-to-end fix: 2-anchor adjudicated winning-cluster mean
        js = rng.sample(anchors, 2)
        d1 = mean([abs(m1[i] - truth[i]) for i in js if i in m1])
        d0 = mean([abs(m0[i] - truth[i]) for i in js if i in m0])
        win = m1 if d1 <= d0 else m0
        agg["fix_cluster"].append(pearson([win[i] for i in held if i in win],
                                          [truth[i] for i in held if i in win]))
        # probes: classify each rater from their 3 most-separating items
        sep = sorted(range(N_ITEMS),
                     key=lambda i: -abs(m1.get(i, CENTER) - m0.get(i, CENTER)))
        hits = 0
        for a in ids:
            probes = sep[:3]
            dc = mean([abs(ratings[i][a] - m1[i]) for i in probes])
            db = mean([abs(ratings[i][a] - m0[i]) for i in probes])
            hits += 1 if (1 if dc < db else 0) == assign[a] else 0
        agg["probe_acc"].append(hits / len(ids))
        # calibration from biased raters only (nc=0 analogue)
        cons = {}
        maps = {}
        for a in ids:
            if tier[a] != "biased":
                continue
            pts = [(ratings[i][a], truth[i]) for i in anchors]
            maps[a] = fit_affine([p[0] for p in pts], [p[1] for p in pts])
        for i in held:
            num = den = 0.0
            for a, mp in maps.items():
                sl, b, sd = mp
                w = 1.0 / (sd * sd + 0.05) if sd is not None else 1.0
                num += w * clip5(sl * ratings[i][a] + b)
                den += w
            cons[i] = num / den
        agg["calib_nc0"].append(pearson([cons[i] for i in held], [truth[i] for i in held]))
    return {k: (mean(v), st.pstdev(v)) for k, v in agg.items()}


print(f"{N_BIASED} biased + {N_COMP} competent x {N_ITEMS} items "
      f"({N_CONTESTED} contested, {N_ANCHORS} anchors, {N_CONTESTED - N_ANCHORS} held-out); "
      f"{SEEDS} seeds/level\n")
print(f"{'bias_w':>6} {'harm(flat)':>10} {'detect_str':>10} {'det_acc':>8} "
      f"{'adj@1':>6} {'adj@3':>6} {'probe':>6} {'fix(clust)':>10} {'calib_nc0':>9}")
for bw in (0.0, 0.2, 0.35, 0.5, 0.65, 0.85):
    r = run_level(bw)
    print(f"{bw:>6.2f} {r['harm_flat'][0]:>10.2f} {r['detect_strength'][0]:>10.2f} "
          f"{r['detect_acc'][0]:>8.2f} {r['adj_1'][0]:>6.2f} {r['adj_3'][0]:>6.2f} "
          f"{r['probe_acc'][0]:>6.2f} {r['fix_cluster'][0]:>10.2f} {r['calib_nc0'][0]:>9.2f}")

print("""
Reading: harm(flat) high = nothing needs fixing at that softness. The trigger
design works if detect_strength falls together with harm's disappearance (fire
the machinery only when it's both needed and detectable). adj@j = probability
j anchors pick the truth-tracking cluster. calib_nc0 = calibration squeezing
truth out of the biased 24 alone. fix(clust) = 2-anchor end-to-end repair.""")
