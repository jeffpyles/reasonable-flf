#!/usr/bin/env python3
"""Thread 2 (offline core) — does anchor PLACEMENT on the target graph's own
contested frontier drive calibration quality?

The FLYWHEEL result said anchors must sit on the contested cluster where the
bias bites; easy/uncontested anchors don't separate competent from biased. Our
Fable+Opus panel anchors were forged on eggs-p6's contested cluster and reused
on eggs-p8 (partial overlap). This tests the placement principle with the
anchors in hand, no new run: across many k-node subsets of the anchor-grade
panel nodes, does a subset's mean "p8-contested-ness" predict how well it
calibrates p8's biased raters on a held-out set?

If yes, it re-confirms placement matters AND tells us the still-needed agent
run (forge anchors on p8's OWN frontier) should pay off. Offline, committable.
"""
import json
import random
import sys
from itertools import combinations
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "coldstart-lab"))
from common import (node_a_matrix, load_roster, p5_oracle, oracle_competence,  # noqa
                    fit_affine, clip5, pearson, mean)

RNG = random.Random(20260714)
truth, ostd = p5_oracle()
roster = load_roster("eggs-p8")
disp = {a: d["disposition"] for a, d in roster.items()}
items = node_a_matrix("eggs-p8", restrict_ids=set(roster))
comp = oracle_competence(items, truth, min_items=8)
raters = sorted(a for a in roster if a in comp)
biased = [a for a in raters if disp[a] == "biased"]
flat = {t: mean(items[t].values()) for t in items}

panel = json.loads((ROOT / "eggs-p8-deliberation/anchors.json").read_text())
pnodes = [a["id"] for a in panel if a["anchor_grade"] and a["id"] in items and a["id"] in truth]
ptruth = {a["id"]: a["consensus_value"] for a in panel if a["anchor_grade"]}
# p8-contestedness of each panel node = how far p8's flat consensus is from truth there
contestedness = {t: abs(flat[t] - truth[t]) for t in pnodes}
# held-out = p8's contested cluster minus ALL panel nodes (fixed across subsets)
contested_all = sorted([t for t in items if t in truth], key=lambda t: -abs(flat[t] - truth[t]))[:18]
held = [t for t in contested_all if t not in set(pnodes)]

print(f"anchor-grade panel nodes usable on p8: {len(pnodes)}")
print(f"  p8-contestedness per node (|flat-truth|): "
      f"{sorted([round(contestedness[t],2) for t in pnodes], reverse=True)}")
print(f"held-out set (p8 contested minus panel nodes): {len(held)} items, "
      f"flat baseline corr {pearson([flat[t] for t in held], [truth[t] for t in held]):+.2f}\n")


def calibrate(pool, anchors):
    maps = {}
    for a in pool:
        pts = [(items[t][a], ptruth[t]) for t in anchors if a in items.get(t, {})]
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


def held_corr(cons):
    k = [t for t in held if t in cons]
    return pearson([cons[t] for t in k], [truth[t] for t in k])


# Across all k-subsets (k=5), relate subset mean-contestedness -> calibration quality
K = 5
subs = list(combinations(pnodes, K))
if len(subs) > 300:
    subs = RNG.sample(subs, 300)
rows = []
for anchors in subs:
    mc = mean([contestedness[t] for t in anchors])
    q_full = held_corr(calibrate(raters, anchors))
    q_bias = held_corr(calibrate(biased, anchors))
    rows.append((mc, q_full, q_bias))

mcs = [r[0] for r in rows]
print(f"across {len(rows)} random {K}-node anchor subsets:")
print(f"  corr(subset mean p8-contestedness, calib-full held-out quality)   = "
      f"{pearson(mcs, [r[1] for r in rows]):+.2f}")
print(f"  corr(subset mean p8-contestedness, calib-biased-only held-out qual) = "
      f"{pearson(mcs, [r[2] for r in rows]):+.2f}")

# tertile comparison: least- vs most-on-frontier subsets
rows.sort(key=lambda r: r[0])
lo = rows[:len(rows) // 3]; hi = rows[-len(rows) // 3:]
print(f"\n  bottom-tertile placement (mean contestedness {mean([r[0] for r in lo]):.2f}): "
      f"calib-full {mean([r[1] for r in lo]):+.2f}  biased-only {mean([r[2] for r in lo]):+.2f}")
print(f"  top-tertile placement   (mean contestedness {mean([r[0] for r in hi]):.2f}): "
      f"calib-full {mean([r[1] for r in hi]):+.2f}  biased-only {mean([r[2] for r in hi]):+.2f}")
print("\nIf top-tertile (better-placed) subsets calibrate clearly better, placement drives value even")
print("within an already-good panel set — confirming the still-needed run (forge anchors on p8's own")
print("contested frontier) should beat these p6-forged ones. Offline first cut at thread 2.")
