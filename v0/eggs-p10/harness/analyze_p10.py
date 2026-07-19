#!/usr/bin/env python3
"""eggs-p10 analysis — de-confound DISPOSITION from MODEL, and validate the
Fable+Opus panel anchors against the p5 expert oracle.

Balanced 2x2 (biased/neutral x haiku/sonnet, 7 each). Reuses coldstart-lab.
Sections:
  0. 2x2 accuracy table: disposition main effect, model main effect, interaction.
     (Does capability partly protect against the bias? Does the bias survive on
     the stronger model?)
  1. Camp detection DE-CONFOUND — the headline. Multi-restart spectral split
     (p7 method), then: does the recovered axis track DISPOSITION (cutting
     across models) or MODEL (cutting across dispositions)? The balanced design
     makes this separable for the first time.
  2. Adjudication + calibration, run twice: with anchors derived from the p5
     expert panel vs with the Fable+Opus PANEL anchors (eggs-p8-deliberation/
     anchors.json). Does the independent, no-Sonnet panel reference give equal
     or better held-out repair? (validates the panel-anchor mechanism live.)
  3. Ranking speed per cell (E2 split-half).

Run: python3 eggs-p10/harness/analyze_p8.py    (from repo root, after the run)
"""
import json
import math
import random
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "coldstart-lab"))
from common import (node_a_matrix, load_roster, p5_oracle, oracle_competence,  # noqa
                    fit_affine, clip5, pearson, mean)

RNG = random.Random(20260714)
truth, ostd = p5_oracle()
roster = load_roster("eggs-p10")
disp = {a: d["disposition"] for a, d in roster.items()}
modl = {a: d["model_tier"] for a, d in roster.items()}

items = node_a_matrix("eggs-p10", restrict_ids=set(roster))
if not items:
    print("No eggs-p10 ratings yet — run workflow_p8.js first.")
    sys.exit(0)
comp = oracle_competence(items, truth, min_items=8)
raters = sorted(a for a in roster if a in comp)


# ---------- 0. 2x2 accuracy ----------
print("=== 0. 2x2 ACCURACY (oracle = p5 experts) — disposition x model ===")
cell = defaultdict(list)
for a in raters:
    cell[(disp[a], modl[a])].append(comp[a])
print(f"{'':<10}{'haiku':>10}{'sonnet':>10}{'row mean':>10}")
for d in ("biased", "neutral"):
    hs = cell[(d, "haiku")]; ss = cell[(d, "sonnet")]
    rowm = mean(hs + ss)
    print(f"{d:<10}{mean(hs):>10.2f}{mean(ss):>10.2f}{rowm:>10.2f}")
colh = mean(cell[("biased", "haiku")] + cell[("neutral", "haiku")])
cols = mean(cell[("biased", "sonnet")] + cell[("neutral", "sonnet")])
print(f"{'col mean':<10}{colh:>10.2f}{cols:>10.2f}")
disp_eff = (mean(cell[("neutral", "haiku")] + cell[("neutral", "sonnet")])
            - mean(cell[("biased", "haiku")] + cell[("biased", "sonnet")]))
mod_eff = cols - colh
inter = ((mean(cell[("neutral", "sonnet")]) - mean(cell[("biased", "sonnet")]))
         - (mean(cell[("neutral", "haiku")]) - mean(cell[("biased", "haiku")])))
print(f"\ndisposition main effect (neutral-biased): {disp_eff:+.2f}")
print(f"model main effect (sonnet-haiku):        {mod_eff:+.2f}")
print(f"interaction (does capability blunt bias): {inter:+.2f}  "
      f"(>0 = neutrality helps sonnet more; bias survives capability if biased_sonnet still low)")
print(f"  biased_sonnet accuracy {mean(cell[('biased','sonnet')]):.2f} vs "
      f"neutral_sonnet {mean(cell[('neutral','sonnet')]):.2f} — "
      f"{'capability does NOT erase the prompted bias' if mean(cell[('biased','sonnet')]) < mean(cell[('neutral','sonnet')]) - 0.1 else 'bias mostly absent on sonnet'}")


# ---------- 1. camp detection de-confound ----------
def agreement_matrix(items, raters):
    prof = {a: {t: items[t][a] for t in items if a in items[t]} for a in raters}
    M = {}
    for i, a in enumerate(raters):
        for b in raters[i + 1:]:
            sh = [t for t in prof[a] if t in prof[b]]
            if len(sh) >= 8:
                M[(a, b)] = M[(b, a)] = pearson([prof[a][t] for t in sh], [prof[b][t] for t in sh])
    return M


def spectral(raters, M, seed, iters=400):
    n = len(raters); idx = {a: i for i, a in enumerate(raters)}
    A = [[0.0] * n for _ in range(n)]
    for (a, b), r in M.items():
        A[idx[a]][idx[b]] = r
    rowm = [mean(row) for row in A]; gm = mean(rowm)
    C = [[A[i][j] - rowm[i] - rowm[j] + gm for j in range(n)] for i in range(n)]
    rng = random.Random(seed); v = [rng.uniform(-1, 1) for _ in range(n)]
    for _ in range(iters):
        nv = [sum(C[i][j] * v[j] for j in range(n)) for i in range(n)]
        nm = math.sqrt(sum(x * x for x in nv)) or 1.0; v = [x / nm for x in nv]
    lam = sum(v[i] * sum(C[i][j] * v[j] for j in range(n)) for i in range(n))
    tot = math.sqrt(sum(C[i][j] ** 2 for i in range(n) for j in range(n))) or 1.0
    return {a: (1 if v[idx[a]] >= 0 else 0) for a in raters}, abs(lam) / tot


print("\n=== 1. CAMP DETECTION DE-CONFOUND (the headline) ===")
M = agreement_matrix(items, raters)
strengths, assigns = [], []
for s in range(40):
    asg, strg = spectral(raters, M, 1000 + s)
    # orient cluster 1 = higher-accuracy side
    if mean([comp[a] for a in raters if asg[a] == 1]) < mean([comp[a] for a in raters if asg[a] == 0]):
        asg = {a: 1 - v for a, v in asg.items()}
    assigns.append(asg); strengths.append(strg)
assign = {a: (1 if mean([asg[a] for asg in assigns]) >= 0.5 else 0) for a in raters}
disp_match = mean([1 if (assign[a] == 1) == (disp[a] == "neutral") else 0 for a in raters])
mod_match = mean([1 if (assign[a] == 1) == (modl[a] == "sonnet") else 0 for a in raters])
print(f"split strength {mean(strengths):.2f}; clusters "
      f"{sum(assign.values())}/{len(raters) - sum(assign.values())}")
print(f"  axis vs DISPOSITION (biased|neutral): {max(disp_match, 1 - disp_match):.2f}")
print(f"  axis vs MODEL (haiku|sonnet):         {max(mod_match, 1 - mod_match):.2f}")
# per-cell: how does each of the 4 cells split across the two clusters?
print("  cluster-1 share per cell (1 = all in the high-accuracy cluster):")
for d in ("biased", "neutral"):
    for m in ("haiku", "sonnet"):
        ids = [a for a in raters if disp[a] == d and modl[a] == m]
        print(f"    {d:<8} {m:<7}: {mean([assign[a] for a in ids]):.2f}  (n={len(ids)})")
print("  -> if the split follows DISPOSITION, both haiku+sonnet biased cells sit in cluster 0")
print("     and both neutral cells in cluster 1; if it follows MODEL, the rows split by column.")


# ---------- 2. adjudication/calibration: p5 anchors vs panel anchors ----------
flat = {t: mean(items[t].values()) for t in items}
contested = sorted([t for t in items if t in truth], key=lambda t: -abs(flat[t] - truth[t]))[:18]


def calibrate(pool, anchors, anchor_truth):
    maps = {}
    for a in pool:
        pts = [(items[t][a], anchor_truth[t]) for t in anchors if a in items.get(t, {}) and t in anchor_truth]
        maps[a] = fit_affine([p[0] for p in pts], [p[1] for p in pts])
    cons = {}
    for t, c in items.items():
        num = den = 0.0
        for a, v in c.items():
            if a not in maps:
                continue
            s, b, sd = maps[a]
            w = 1.0 / (sd * sd + 0.05) if sd is not None else 1.0
            num += w * clip5(s * v + b); den += w
        if den:
            cons[t] = num / den
    return cons


def corr_on(keys, cons):
    keys = [t for t in keys if t in truth and t in cons]
    return pearson([cons[t] for t in keys], [truth[t] for t in keys])


print("\n=== 2. ADJUDICATION/CALIBRATION — p5-panel anchors vs Fable+Opus panel anchors ===")
# reference set A: p5-panel-derived (tightest expert stdev on the contested cluster)
p5_anchors = sorted(contested, key=lambda t: ostd[t])[:10]
p5_at = {t: truth[t] for t in p5_anchors}
# reference set B: the Fable+Opus panel anchors (anchor_grade only), if present
panel_path = ROOT / "eggs-p8-deliberation" / "anchors.json"
panel = json.loads(panel_path.read_text()) if panel_path.exists() else None

for label, anchors, at in ([("p5-panel (10)", p5_anchors, p5_at)] +
                           ([("Fable+Opus panel", [a["id"] for a in panel if a["anchor_grade"]],
                              {a["id"]: a["consensus_value"] for a in panel if a["anchor_grade"]})]
                            if panel else [])):
    held = [t for t in contested if t not in set(anchors)]
    cons = calibrate(raters, anchors, at)
    biased_only = calibrate([a for a in raters if disp[a] == "biased"], anchors, at)
    print(f"  {label:<18} n_anchors={len(anchors):>2}  held-out({len(held)}) repair: "
          f"flat {corr_on(held, flat):+.2f} -> calib-full {corr_on(held, cons):+.2f}  "
          f"calib-biased-only {corr_on(held, biased_only):+.2f}")
if panel:
    # panel-vs-p5 agreement on the shared anchor-grade nodes (the validity check headline)
    shared = [a for a in panel if a["id"] in truth]
    print(f"\n  PANEL VALIDITY vs p5 oracle over {len(shared)} deliberated nodes:")
    pv = [a["consensus_value"] for a in shared]; ev = [truth[a["id"]] for a in shared]
    print(f"    corr(panel, p5) {pearson(pv, ev):+.2f}  mean|panel-p5| {mean([abs(x-y) for x,y in zip(pv,ev)]):.2f}")
    ag = [a for a in shared if a["anchor_grade"]]
    print(f"    anchor-grade: {len(ag)}/{len(shared)}; value-questions flagged: "
          f"{sum(1 for a in shared if a['is_value_question'])}")
else:
    print("\n  (Fable+Opus panel anchors not found — run the deliberation workflow + build anchors.json)")


# ---------- 3. ranking speed per cell ----------
print("\n=== 3. RANKING SPEED per cell (E2 split-half r1; ref p5 crowd 0.013, p6 0.107) ===")
by = defaultdict(dict)
for t, c in items.items():
    if t in truth:
        for a, v in c.items():
            if a in raters:
                by[a][t] = v


def split_half_r1(ids, n=200, mh=6):
    rs, Ls = [], []
    for _ in range(n):
        c1, c2 = {}, {}
        for a in ids:
            ts = list(by[a])
            if len(ts) < 2 * mh:
                continue
            RNG.shuffle(ts); h = len(ts) // 2
            c1[a] = pearson([by[a][t] for t in ts[:h]], [truth[t] for t in ts[:h]])
            c2[a] = pearson([by[a][t] for t in ts[h:2 * h]], [truth[t] for t in ts[h:2 * h]])
            Ls.append(h)
        both = [a for a in c1 if a in c2]
        if len(both) >= 6:
            rs.append(pearson([c1[a] for a in both], [c2[a] for a in both]))
    rL = mean(rs) if rs else float("nan"); L = mean(Ls) if Ls else 1
    return (rL / (L - (L - 1) * rL)) if rL == rL and L > 1 else float("nan")


for label, ids in (("all 28", raters),
                   ("haiku (14)", [a for a in raters if modl[a] == "haiku"]),
                   ("sonnet (14)", [a for a in raters if modl[a] == "sonnet"])):
    print(f"  {label:<12} per-item r1 {split_half_r1(ids):.3f}")
print("\nDone. See eggs-p10/FINDINGS.md for the synthesis.")
