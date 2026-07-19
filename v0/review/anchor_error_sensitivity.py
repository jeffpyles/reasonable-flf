#!/usr/bin/env python3
"""How robust is the eggs-p6 recipe (contested anchors, trust=0.9, gamma=6) to
WRONG anchors?

FLYWHEEL-FINDINGS.md's recipe leans on anchor agreement for 90% of Raw_R and
then raises weights to the 6th power. Its own caveat says "sparse or wrong
anchors would mis-calibrate" -- but nobody measured the dose-response. This is
the single biggest practical risk of the recipe: in the real world anchors are
chosen by fallible editors, and the most tempting anchor errors are exactly the
majority's bias (an editor who shares the crowd's error "anchors" the wrong
answer).

We corrupt k of the 10 contested anchors, two ways:
  - "biased"  : the anchor's truth is replaced by the FLAT (biased-crowd)
                consensus value -- the realistic failure, an anchor that
                enshrines the popular error.
  - "inverted": truth -> 5 - truth (a maximally wrong anchor).

Then re-run the exact analyze_p6.py recipe and report held-out corr + reputation
~competence as k rises. Deterministic; corrupts the k anchors with LOWEST oracle
stdev first (the ones the recipe trusts most, worst case) -- and also reports a
random-subset average for a fairer view.
"""
import json, math, statistics as st, sys, random
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from reasonable import store, fold  # noqa

PRIOR, K = 0.15, 8.0
BLEND, GAMMA = 0.9, 6.0

roster = json.loads((HERE.parent / "eggs-p6/harness/roster.json").read_text())
tier = {a["id"]: a["tier"] for a in roster["agents"]}
p6 = fold.fold(store.read_events("eggs-p6"))
items = {}
for t, dm in p6["ratings"].items():
    if "A" in dm and t.startswith("n"):
        cell = {a: v for a, v in dm["A"].items() if v != "abstain" and a in tier}
        if cell:
            items[t] = cell
p5 = fold.fold(store.read_events("eggs-p5"))
r5 = json.loads((HERE.parent / "eggs-p5/harness/roster.json").read_text())
etier = {a["id"]: a["tier"] for a in r5["agents"]}
truth, ostd = {}, {}
for t, dm in p5["ratings"].items():
    if "A" in dm:
        ev = [v for a, v in dm["A"].items() if etier.get(a) == "expert" and v != "abstain"]
        if len(ev) >= 3:
            truth[t] = st.mean(ev); ostd[t] = st.pstdev(ev)


def pear(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy) if dx and dy else 0.0


ids = sorted(a for a in tier if any(a in items[t] for t in items))
comp = {}
for a in ids:
    pts = [(items[t][a], truth[t]) for t in items if a in items[t] and t in truth]
    if len(pts) >= 5:
        comp[a] = pear([p[0] for p in pts], [p[1] for p in pts])

flat = {t: st.mean(items[t].values()) for t in items}
biased_cluster = sorted([t for t in items if t in truth], key=lambda t: -abs(flat[t]-truth[t]))[:18]
anchors = sorted([t for t in biased_cluster if t in truth], key=lambda t: ostd[t])[:10]
held_out = [t for t in biased_cluster if t not in set(anchors)]
n_given = {a: sum(1 for t in items if a in items[t]) for a in ids}


def run_recipe(anchor_truth):
    anch = {}
    for a in ids:
        pts = [abs(items[t][a]-anchor_truth[t])/5 for t in anchors if a in items[t]]
        anch[a] = (1-sum(pts)/len(pts)) if pts else None

    def wcons(w):
        out = {}
        for t, c in items.items():
            num = den = 0.0
            for a, v in c.items():
                wa = w.get(a, PRIOR) ** GAMMA
                num += wa*v; den += wa
            out[t] = num/den if den else st.mean(c.values())
        return out
    w = {a: PRIOR for a in ids}
    for _ in range(30):
        cons = wcons(w)
        by = defaultdict(list)
        for t, c in items.items():
            for a, v in c.items():
                by[a].append((v, cons[t]))
        disc = {a: pear([p[0] for p in pr], [p[1] for p in pr]) for a, pr in by.items() if len(pr) >= 5}
        neww = {}
        for a in ids:
            d = max(0.0, disc.get(a, 0.0))
            an = anch.get(a)
            raw = (BLEND*an + (1-BLEND)*d) if an is not None else d
            conf = n_given[a]/(n_given[a]+K)
            neww[a] = PRIOR + conf*(raw-PRIOR)
        if max(abs(neww[a]-w[a]) for a in ids) < 1e-4:
            w = neww; break
        w = neww
    cons = wcons(w)
    keys = [t for t in held_out if t in truth]
    ho = pear([cons[t] for t in keys], [truth[t] for t in keys])
    comp_ids = [a for a in ids if a in comp]
    rc = pear([comp[a] for a in comp_ids], [w[a] for a in comp_ids])
    wc = st.mean([w[a] for a in ids if tier[a] == "competent"])
    wb = st.mean([w[a] for a in ids if tier[a] == "biased"])
    return ho, rc, wc, wb


def corrupted(k, mode, subset):
    at = dict((t, truth[t]) for t in anchors)
    for t in subset[:k]:
        at[t] = flat[t] if mode == "biased" else (5.0 - truth[t])
    return at


RNG = random.Random(20260710)
print(f"recipe: trust={BLEND}, gamma={GAMMA}; 10 contested anchors, {len(held_out)} held-out biased items")
print("corruption 'biased' = anchor truth replaced by the biased-crowd flat consensus (the realistic failure)\n")
print(f"{'k_bad':>5} {'mode':>9} {'held-out corr':>14} {'rep~comp':>9} {'w comp/bias':>12}   (worst-case: most-trusted anchors corrupted first)")
for mode in ("biased", "inverted"):
    for k in (0, 1, 2, 3, 4, 5):
        ho, rc, wc, wb = run_recipe(corrupted(k, mode, anchors))
        print(f"{k:>5} {mode:>9} {ho:>14.2f} {rc:>9.2f} {wc:>7.2f}/{wb:.2f}")
    print()

print("random-subset average (10 draws per k), 'biased' mode:")
print(f"{'k_bad':>5} {'held-out corr mean±sd':>22} {'rep~comp mean':>14}")
for k in (1, 2, 3, 4, 5):
    hos, rcs = [], []
    for _ in range(10):
        sub = RNG.sample(anchors, len(anchors))
        ho, rc, _, _ = run_recipe(corrupted(k, "biased", sub))
        hos.append(ho); rcs.append(rc)
    print(f"{k:>5} {st.mean(hos):>15.2f} ± {st.pstdev(hos):>4.2f} {st.mean(rcs):>14.2f}")
