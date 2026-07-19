#!/usr/bin/env python3
"""E2 — The measurement ceiling: how RELIABLE is per-rater competence as a
trait, and what rating budget does a trustworthy reputation actually require?

Any reputation rule estimates a latent per-rater trait from k ratings. Before
comparing rules, measure the ceiling: the split-half reliability of competence
(corr of own ratings with oracle truth) itself. Method: split each rater's OWN
rated items into two random halves, compute competence on each half, correlate
the two estimates across raters, repeat over many splits. Spearman-Brown then
converts the half-length reliability into (a) the per-item reliability r1,
(b) reliability at any budget k, and (c) the budget needed to hit a target
reliability -- the cold-start numbers.

Two regimes measured:
  - eggs-p5 crowd (52 good-faith Haiku, ~20 node-A items each): a HOMOGENEOUS
    good-faith crowd -- differences are diligence/noise, no shared divide.
  - eggs-p6 (16 biased + 4 competent, 79 items each): a population split by a
    systematic DISPOSITION.

Also re-reads E1's near-zero p4->p5 stability against the measured ceiling
(attenuation: max observable transfer = sqrt(rel_p4 * rel_p5)), and reports the
per-run mean-competence gap on matched items (a run-protocol effect, not a
persona effect).
"""
import random
import statistics as st
from collections import defaultdict
from common import (node_a_matrix, load_roster, p5_oracle, pearson, mean)

RNG = random.Random(20260710)
truth, _ = p5_oracle()


def per_rater_items(items, truth):
    by = defaultdict(dict)
    for t, cell in items.items():
        if t in truth:
            for a, v in cell.items():
                by[a][t] = v
    return by


def split_half(by_agent, n_splits=200, min_half=4):
    """Random own-item split halves. Returns (mean corr between halves,
    sd, mean items per half)."""
    rs, half_sizes = [], []
    for _ in range(n_splits):
        c1, c2 = {}, {}
        for a, sub in by_agent.items():
            ts = list(sub)
            if len(ts) < 2 * min_half:
                continue
            RNG.shuffle(ts)
            h = len(ts) // 2
            t1, t2 = ts[:h], ts[h:2 * h]
            c1[a] = pearson([sub[t] for t in t1], [truth[t] for t in t1])
            c2[a] = pearson([sub[t] for t in t2], [truth[t] for t in t2])
            half_sizes.append(h)
        both = [a for a in c1 if a in c2]
        if len(both) >= 10:
            rs.append(pearson([c1[a] for a in both], [c2[a] for a in both]))
    return mean(rs), (st.pstdev(rs) if len(rs) > 1 else 0.0), mean(half_sizes)


def sb_r1(r_L, L):
    """Invert Spearman-Brown: per-item reliability from length-L reliability."""
    return r_L / (L - (L - 1) * r_L)


def sb_at(r1, k):
    return k * r1 / (1 + (k - 1) * r1)


def budget_for(r1, target):
    """Items needed for reliability >= target."""
    if r1 <= 0:
        return float("inf")
    return (target / (1 - target)) * (1 - r1) / r1


print("=" * 78)
for name, run, tier_filter in (("p5 crowd — homogeneous good-faith", "eggs-p5", "crowd"),
                               ("p6 — disposition-split population", "eggs-p6", None)):
    roster = load_roster(run)
    ids = {a for a, d in roster.items() if tier_filter is None or d["tier"] == tier_filter}
    items = node_a_matrix(run, restrict_ids=ids)
    by = per_rater_items(items, truth)
    # competence spread (full data)
    comp = {a: pearson([v for v in sub.values()], [truth[t] for t in sub])
            for a, sub in by.items() if len(sub) >= 8}
    r_half, sd, L = split_half(by)
    r1 = sb_r1(r_half, L)
    print(f"{name}")
    print(f"  competence: mean {mean(comp.values()):.2f}, sd {st.pstdev(list(comp.values())):.2f} "
          f"(n={len(comp)} raters)")
    print(f"  split-half r (L≈{L:.0f} items/half) = {r_half:.3f} ± {sd:.3f}   "
          f"per-item r1 = {r1:.4f}")
    print(f"  reliability at k:  " + "  ".join(
        f"k={k}:{sb_at(r1, k):.2f}" for k in (5, 10, 20, 45, 80, 160)))
    print(f"  budget for reliability 0.5 / 0.7 / 0.9:  "
          f"{budget_for(r1, .5):.0f} / {budget_for(r1, .7):.0f} / {budget_for(r1, .9):.0f} items")
    print(f"  -> ceiling on ANY rule's corr-with-competence at k=20: "
          f"{sb_at(r1, 20) ** 0.5:.2f}")
    print("-" * 78)

print("""
Reading E1's transfer null against this ceiling:
  p4 competence was measured on ~13 items, p5 on ~20. Max observable p4->p5
  correlation = sqrt(rel_13 * rel_20). In the homogeneous regime that ceiling
  is itself small, so E1's ~0 is consistent with a weakly-stable trait measured
  far below its required budget -- NOT proof the trait is absent. The p6-style
  disposition, by contrast, is measurable in a handful of items.

Run-protocol effect (from E1's matched-items test): the SAME personas on the
SAME nodes tracked truth at 0.52 in the p4 run vs 0.89 in the p5 run. Candidate
causes (not separable in this data): p4 rated mid-construction with visible
prior ratings/comments (social anchoring), p4's mixed target types vs p5's
focused node pass, legacy p3 context. Whichever it is, PROTOCOL moved crowd
accuracy far more than any persona difference -- an elicitation-design lever
bigger than any scoring rule examined so far.
""")
