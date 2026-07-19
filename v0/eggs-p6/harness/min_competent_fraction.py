#!/usr/bin/env python3
"""Minimum competent fraction at which the recipe (contested anchors + high trust
+ superlinear weighting) still de-biases the consensus.

Monte-Carlo subsample the eggs-p6 population at varying competent fractions, apply
the FIXED recipe to each subsample, and record whether the biased consensus flips
to truth — and how ROBUSTLY (variance across draws + how concentrated the winning
weight becomes; a fraction that "works" only by collapsing the consensus onto one
rater is fragile, not working).

Recipe held fixed: contested anchors, anchor-trust blend=0.9, weight-power gamma=6.
Item sets (biased cluster, contested anchors) are fixed from the full population so
the competent FRACTION is the only variable.
"""
import json, math, statistics as st, sys, random
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
from reasonable import store, fold  # noqa

PRIOR, K = 0.15, 8.0
BLEND, GAMMA = 0.9, 6.0
RNG = random.Random(6060)

roster = json.loads((HERE / "roster.json").read_text())
tier = {a["id"]: a["tier"] for a in roster["agents"]}
p6 = fold.fold(store.read_events("eggs-p6"))
items_full = {}
for t, dm in p6["ratings"].items():
    if "A" in dm and t.startswith("n"):
        cell = {a: v for a, v in dm["A"].items() if v != "abstain" and a in tier}
        if cell:
            items_full[t] = cell
p5 = fold.fold(store.read_events("eggs-p5"))
r5 = json.loads((HERE.parent.parent / "eggs-p5/harness/roster.json").read_text())
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


flat = {t: st.mean(items_full[t].values()) for t in items_full}
biased_cluster = sorted([t for t in items_full if t in truth], key=lambda t: -abs(flat[t]-truth[t]))[:18]
anchors = sorted([t for t in biased_cluster if t in truth], key=lambda t: ostd[t])[:10]
anchor_set = set(anchors)
held_out = [t for t in biased_cluster if t not in anchor_set]
all_biased = [a for a in tier if tier[a] == "biased"]
all_comp = [a for a in tier if tier[a] == "competent"]


def recipe_holdout_corr(raters):
    """Run the fixed recipe on a subsample; return (held-out biased corr, top-weight-share)."""
    R = set(raters)
    items = {t: {a: v for a, v in c.items() if a in R} for t, c in items_full.items()}
    items = {t: c for t, c in items.items() if len(c) >= 5}
    n_given = {a: sum(1 for t in items if a in items[t]) for a in raters}
    anch = {}
    for a in raters:
        pts = [abs(items[t][a]-truth[t])/5 for t in anchors if t in items and a in items[t]]
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
    w = {a: PRIOR for a in raters}
    for _ in range(30):
        cons = wcons(w)
        by = defaultdict(list)
        for t, c in items.items():
            for a, v in c.items():
                by[a].append((v, cons[t]))
        disc = {a: pear([p[0] for p in pr], [p[1] for p in pr]) for a, pr in by.items() if len(pr) >= 5}
        neww = {}
        for a in raters:
            d = max(0.0, disc.get(a, 0.0))
            an = anch.get(a)
            raw = (BLEND*an + (1-BLEND)*d) if an is not None else d
            conf = n_given[a]/(n_given[a]+K)
            neww[a] = PRIOR + conf*(raw-PRIOR)
        if max(abs(neww[a]-w[a]) for a in raters) < 1e-4:
            w = neww; break
        w = neww
    cons = wcons(w)
    keys = [t for t in held_out if t in truth and t in cons]
    corr = pear([cons[t] for t in keys], [truth[t] for t in keys])
    wp = {a: w[a]**GAMMA for a in raters}
    tot = sum(wp.values()) or 1
    top_share = max(wp.values())/tot
    return corr, top_share


from itertools import combinations
print(f"recipe: contested anchors, trust={BLEND}, gamma={GAMMA}; held-out biased items: {len(held_out)}")
print(f"\n{'n_bias':>6}{'n_comp':>7}{'comp_frac':>10}{'holdout_corr(mean±sd)':>24}{'success%':>9}{'top_wt%':>8}")
rows = []
for nb in (16, 12, 9, 6, 4, 3):
    for nc in (1, 2, 3, 4):
        frac = nc/(nb+nc)
        comp_combos = list(combinations(all_comp, nc))
        corrs, tops = [], []
        for cc in comp_combos:
            # up to 6 biased draws per competent combo
            draws = 6 if nb < 16 else 4
            for _ in range(draws):
                bs = RNG.sample(all_biased, nb)
                corr, top = recipe_holdout_corr(list(cc)+bs)
                if not math.isnan(corr):
                    corrs.append(corr); tops.append(top)
        if not corrs:
            continue
        succ = sum(1 for c in corrs if c > 0.5)/len(corrs)
        rows.append((frac, nb, nc, st.mean(corrs), st.pstdev(corrs) if len(corrs) > 1 else 0, succ, st.mean(tops)))
for frac, nb, nc, m, sd, succ, top in sorted(rows):
    print(f"{nb:>6}{nc:>7}{frac:>10.2f}{m:>16.2f} ± {sd:>4.2f}{succ*100:>8.0f}%{top*100:>7.0f}%")
print("\nsuccess% = draws with held-out corr > 0.5 (recipe de-biased the held-out items).")
print("top_wt% = share of total weight on the single highest-weighted rater (high => fragile,")
print("consensus collapsed onto one voice). Minimum VIABLE fraction = where success% is high")
print("AND spread is low AND top_wt% isn't near 100%.")
