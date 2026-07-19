#!/usr/bin/env python3
"""E1 — Re-baseline the eggs-p4 rule comparison against ORACLE competence,
and test whether rating competence is a STABLE, TRANSFERABLE trait (p4 -> p5).

Why: the canonical rescore.py table measures every rule against the roster's
care labels, but test_flywheel.py later showed the care label anti-correlates
(-0.33) with actually-measured competence. So the canonical numbers are not
citable. Here competence := corr(rater's node-A ratings, eggs-p5 8-expert
oracle) -- measurable for p4 raters because p4's 79 node ids are identical to
p5's (verified: 79/79 shared, 0 text mismatches).

Caveat handled explicitly: the p4 experts s01..s08 are the SAME personas as the
p5 oracle panel (different run), so expert oracle-competence is persona-
correlated. The headline Spearman is therefore reported CROWD-ONLY (52 Haiku,
personas disjoint from the oracle), with the full-population number and expert
percentile shown alongside for continuity with the old table.

Also answers (same machinery, same script):
  - TRAIT STABILITY: does a p4 rater's oracle-competence predict the SAME
    agent's p5 oracle-competence? (Same persona ids ran both runs.) If yes,
    "reasonableness" is a stable measurable trait and reputation is worth
    accumulating and transferring across graphs; if no, per-rater weighting is
    chasing noise.
  - SIGNAL TRANSFER: does a reputation score computed on p4 (alignment /
    discrimination) predict p5 competence? That's the deployable version
    (the mechanism never sees competence, only scores).
"""
import statistics as st
from common import (node_a_matrix, full_matrix, load_roster, p5_oracle,
                    oracle_competence, align_score, disc_score,
                    pearson, spearman, pctile, mean)

r4 = load_roster("eggs-p4")
r5 = load_roster("eggs-p5")
tier4 = {a: d["tier"] for a, d in r4.items()}
truth, _ = p5_oracle()

# --- oracle competence for p4 raters (node-A only; median 13 items/rater) ---
p4_nodes = node_a_matrix("eggs-p4", restrict_ids=set(tier4))
comp4 = oracle_competence(p4_nodes, truth, min_items=5)

# --- rule scores on the FULL p4 matrix (307 items), as rescore.py scored them ---
p4_full = full_matrix("eggs-p4", restrict_ids=set(tier4))
scores = {
    "align": align_score(p4_full),
    "disc": disc_score(p4_full),
}

print(f"p4 raters with oracle competence (>=5 node-A items co-covered): {len(comp4)}")
crowd = [a for a in comp4 if tier4[a] == "crowd"]
experts = [a for a in comp4 if tier4[a] == "expert"]
print(f"oracle competence: crowd mean {mean([comp4[a] for a in crowd]):.2f} "
      f"(range {min(comp4[a] for a in crowd):.2f}..{max(comp4[a] for a in crowd):.2f}), "
      f"experts (persona-correlated w/ oracle) {mean([comp4[a] for a in experts]):.2f}\n")

print("RE-BASELINED TABLE — each p4 rule score vs ORACLE competence")
print(f"{'rule':<8} {'spearman CROWD-only':>20} {'spearman all-60':>16} {'expert median pctile':>21}")
for name, sc in scores.items():
    both_c = [a for a in crowd if a in sc]
    both_all = [a for a in comp4 if a in sc]
    sp_c = spearman([sc[a] for a in both_c], [comp4[a] for a in both_c])
    sp_a = spearman([sc[a] for a in both_all], [comp4[a] for a in both_all])
    pop = {a: sc[a] for a in tier4 if a in sc}
    vals = list(pop.values())
    ep = st.median([pctile(pop[a], vals) for a in pop if tier4[a] == "expert"])
    print(f"{name:<8} {sp_c:>20.3f} {sp_a:>16.3f} {ep:>21.3f}")
print("\n(old care-label table said: align -0.54, disc +0.11 -- compare crowd-only column)")

# --- trait stability p4 -> p5 ---
p5_nodes = node_a_matrix("eggs-p5", restrict_ids=set(r5))
comp5 = oracle_competence(p5_nodes, truth, min_items=5)
common_crowd = [a for a in crowd if a in comp5]
print(f"\nTRAIT STABILITY — same 52 crowd personas, two independent runs")
print(f"corr(p4 competence, p5 competence), crowd-only, n={len(common_crowd)}: "
      f"pearson {pearson([comp4[a] for a in common_crowd], [comp5[a] for a in common_crowd]):+.3f}  "
      f"spearman {spearman([comp4[a] for a in common_crowd], [comp5[a] for a in common_crowd]):+.3f}")
print("(p4 competence is measured on only ~13 sortition items/rater; p5 on all 79 —")
print(" attenuation from p4 measurement noise bounds this from above; see E2 ceiling.)")

print(f"\nSIGNAL TRANSFER — score earned on p4 predicting p5 competence (crowd-only)")
for name, sc in scores.items():
    both = [a for a in common_crowd if a in sc]
    print(f"p4 {name:<6} -> p5 competence: spearman "
          f"{spearman([sc[a] for a in both], [comp5[a] for a in both]):+.3f}  (n={len(both)})")

# also: p5-internal scores -> p5 competence, as the within-run reference point
p5_all = full_matrix("eggs-p5", restrict_ids={a for a in r5 if r5[a]['tier'] == 'crowd'})
disc5 = disc_score(p5_all)
both = [a for a in common_crowd if a in disc5]
print(f"p5 disc   -> p5 competence (within-run reference): spearman "
      f"{spearman([disc5[a] for a in both], [comp5[a] for a in both]):+.3f}  (n={len(both)})")
