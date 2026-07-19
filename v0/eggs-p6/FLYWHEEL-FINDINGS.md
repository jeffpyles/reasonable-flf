# eggs-p6 — does the flywheel turn on a BIASED population? The three-part answer

**Setup.** 20 raters — 16 "cholesterol-hawk" Haiku sharing a directional, outdated
dietary-cholesterol-is-dangerous model + 4 evidence-tracking Sonnet — each rated all 79 node claims
(saturated). Independent truth = eggs-p5's 8 experts' mean per node (a panel not in this population).
Competence of a p6 rater = correlation of their ratings with that truth.

**The bias is real and shared, not noise** (this is what eggs-p5 lacked): biased raters' mean competence
is **0.01** (uncorrelated with truth), competent raters' is **0.89**. On the biased cluster the flat
consensus is *anti*-correlated with truth (−0.65). Finally, a consensus the flywheel has real work to fix.

## The arms (True_R-weighted fixed-point, measured against expert truth)

| arm | cons~truth (all) | biased cluster | held-out biased | rep~comp | weight comp/bias |
|---|:--:|:--:|:--:|:--:|:--:|
| A flat | 0.21 | −0.65 | −0.69 | −0.00 | 0.15 / 0.15 |
| B discrimination-only | 0.02 | −0.77 | −0.79 | **−0.85** | **0.01 / 0.75** |
| C disc + anchors (easy items) | 0.17 | −0.69 | −0.72 | −0.56 | 0.57 / 0.72 |
| D disc + anchors (contested items) | 0.20 | −0.66 | −0.84 | −0.17 | 0.58 / 0.60 |

**Anchor-trust × weight-power sweep (contested anchors):**

| anchor trust (blend) | weight power (γ) | rep~comp | held-out biased corr | weight comp/bias |
|:--:|:--:|:--:|:--:|:--:|
| 0.6 | 1 | −0.17 | −0.84 | 0.58/0.60 |
| 0.6 | 6 | −0.31 | −0.85 | 0.56/0.60 |
| **0.9** | 1 | **+0.92** | −0.81 | 0.82/0.53 |
| **0.9** | 3 | +0.93 | +0.21 | 0.86/0.51 |
| **0.9** | **6** | +0.94 | **+0.90** (MAE 0.44) | 0.89/0.47 |
| 0.99 | 6 | +0.91 | +0.90 | 0.89/0.51 |

## Three findings, each necessary

**1. Pure discrimination catastrophically FAILS on a biased population — it inverts.** Arm B drives
reputation to **−0.85** vs competence: it downweights the competent minority to near-zero (0.01) and
*upweights* the biased majority (0.75), because discrimination scores agreement with the (biased)
consensus and the competent — being right — anti-correlate with it. The result is a consensus *worse*
than no weighting at all (0.02 vs flat 0.21). **Discrimination cannot self-start from a biased crowd; it
entrenches the bias.** This is the self-reference trap, confirmed at full strength — and it's exactly why
eggs-p5 (a merely *noisy* crowd) couldn't show it: you need shared bias for the trap to bite.

**2. External anchors are REQUIRED to break the self-reference — and placement + trust matter.** Anchors
(a few items with externally-known answers) de-bias reputation, but only if they're (a) placed on the
**contested cluster where the bias bites** — easy/uncontested anchors (arm C) leave reputation at −0.56,
because biased and competent raters both match uncontroversial truths — and (b) **trusted heavily**
(anchor-weight 0.9, not 0.6). With contested anchors at high trust, reputation flips to **+0.92** — it
now correctly ranks the competent above the biased. A handful of well-placed anchors calibrates
reputation *globally* (the held-out biased items were never handed over).

**3. Correct reputation is still NOT enough — linear weighting can't beat a numerical supermajority.**
This is the surprise. Even at rep~comp **+0.92** (per-rater weights competent 0.82 vs biased 0.53),
**linear** weighting (γ=1) leaves the consensus biased (held-out −0.81), because 16 biased × 0.53 still
outweighs 4 competent × 0.82 by ~2:1 in mass. Fixing *who is trusted* does not fix the *aggregate* when
the trusted-correct are a small minority. Only **superlinear weighting** — concentrating weight on the
top-reputation raters (γ≥3, decisively γ=6) — flips the consensus to truth (held-out **+0.90**, MAE 0.44).

## The recipe, and the design consequence

To make a competent minority overturn a biased supermajority you need **all three together**:
**contested anchors + high anchor-trust + superlinear (or gated) weighting.** Drop any one and the bias
wins. Concretely for the reputation design:

- **Linear True_R-weighted aggregation (the current spec) is insufficient against bias.** It should be
  **superlinear** — weight by `True_R^γ` (γ≈3–6), a softmax over reputation, or a hard reputation gate —
  so a trusted minority can actually move a contested item. Note γ=6 concentrates almost all weight on the
  top raters, so "superlinear weighting" and "route/gate the pool" converge on the same principle:
  **influence must concentrate on the competent, not spread across the crowd.** This is the same lesson as
  the BTS reverse-sweep (there's an optimal quality-concentration, not "one-rater-one-vote").
- **Anchors are not optional for a biased domain, and they must sit on the contested questions.** A
  reputation system with no external ground-truth reference cannot distinguish a correct minority from a
  biased majority — it will always entrench whatever the majority believes.

## Minimum competent fraction — it's really a minimum COUNT

Monte-Carlo subsampling the population at varying competent fractions, applying the fixed recipe
(contested anchors, trust 0.9, γ=6) to each and measuring how reliably it flips the held-out biased
items (`harness/min_competent_fraction.py`):

| competent frac | comp / biased | held-out corr (mean±sd) | success rate | top-rater weight share |
|:--:|:--:|:--:|:--:|:--:|
| 0.06 | 1 / 16 | 0.56 ± 0.24 | **50%** | 57% |
| 0.08 | 1 / 12 | 0.78 ± 0.13 | 100% | 69% |
| 0.10 | 1 / 9 | 0.83 ± 0.10 | 100% | 79% |
| **0.11** | **2 / 16** | 0.88 ± 0.08 | 100% | 41% |
| 0.16 | 3 / 16 | 0.90 ± 0.04 | 100% | 30% |
| 0.20 | 4 / 16 | 0.90 ± 0.00 | 100% | 24% |

**The binding constraint is the absolute COUNT of competent raters, not the fraction.** With a *single*
competent rater the recipe is fragile: at 6% it's a coin-flip (50% success, ±0.24), and even where it
"works" (8–10%) it does so only by collapsing ~60–80% of the weight onto that one voice — a dictatorship,
not a consensus, and hostage to whether that rater happens to be good. With **2 competent raters** (~11%
fraction) it becomes reliable (100% success, variance drops to ±0.08, weight share falls to ~40% as the
two corroborate each other through the anchors); with **3** it's robust and well-distributed (±0.04,
top share ~30%).

**So the practical floor is ~2–3 reputation-verified raters per contested item, not a fraction.**
Superlinear weighting makes even a ~10% minority able to win — but a lone winner is fragile, because
nothing distinguishes "competent" from "lucky" without corroboration. The design rule this implies for
routing: guarantee a **minimum count** (≈3) of high-reputation raters on each contested item, and prefer
distributed competent weight over a single dominant voice (cap the top-rater weight share).

## Honest caveats

- One run, one bias type (cholesterol alarmism), one minority fraction (4/20 = 20%). The γ needed scales
  with how outnumbered the competent are; 20% competent needed γ≈6. A less lopsided population needs less.
- Anchors used the eggs-p5 expert panel as "known truth"; real anchors need genuinely externally-verifiable
  answers, and enough of them, covering the contested space.
- High anchor-trust (0.9) makes reputation lean heavily on anchor agreement — robust only if anchors are
  plentiful and correct. Sparse or wrong anchors would mis-calibrate.
- This is offline re-aggregation on one saturated round; it captures the compounding + concentration legs,
  not longitudinal dynamics over many rounds with churn.

## Where it leaves the reputation design

The flywheel *can* turn on a biased population — but not on discrimination alone, and not with linear
weighting. The validated recipe is **contested external anchors + heavily-trusted + superlinear/gated
aggregation.** This retires the hope that discrimination self-bootstraps, and elevates anchors and
superlinear weighting from "nice to have" to load-bearing requirements for any domain where the crowd can
share a systematic error. (Analysis + arms reproducible via `harness/analyze_p6.py`.)
