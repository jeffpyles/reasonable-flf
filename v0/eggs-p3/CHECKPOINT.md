# eggs-p3 — Stage-2 checkpoint: does True_R sort competence? (the eggs-p2 gap, now testable)

Sortition run, 17 raters incl. 4 honest-but-systematically-miscalibrated (mx-*). Hidden tiers were
never shown to the mechanism. 988 events. True_R by tier:

| tier (hidden) | mean True_R | range | mean raw_r (alignment) |
|---|---|---|---|
| Sonnet expert (rex) | **0.785** | 0.77–0.79 | 0.891 |
| Haiku hi-care (hg) | 0.809 | 0.78–0.85 | 0.927 |
| Haiku mid-care (mg) | 0.828 | 0.82–0.84 | 0.925 |
| Haiku lo/hasty (lg) | 0.810 | 0.78–0.84 | 0.905 |
| **Miscalibrated (mx)** | **0.755** | 0.71–0.78 | 0.866 |

Bottom two overall: mx-boost (0.713), mx-noise (0.750). Top: hg-1, lg-1, mg-3 (~0.84).

## Two findings, one reassuring and one that challenges a core assumption

**(1) Systematic miscalibration IS penalized — directionally correct (✓, weak).** The MISCAL tier is
the lowest (0.755 vs honest ~0.81), and the two *worst-calibrated* — mx-boost (a directional
contrarian who rejects the strong LDL-causality consensus) and mx-noise (no discrimination) — are
the bottom two accounts. So the mechanism does push honest-but-wrong raters down. This is the thing
eggs-p2 couldn't test (its care-personas converged); it now tests, and passes in direction.

**(2) Experts do NOT rise to the top — alignment has a conformity bias (✗, important).** The Sonnet
experts land at 0.785 — *below* every honest Haiku tier and barely above the miscalibrated tier.
Cause is visible in raw_r: experts have the LOWEST alignment among honest raters (0.891 vs Haiku
0.905–0.927). Not because they're wrong — because they're **sharper**: they gave weak inference
edges 1.5–2.0 (argument-from-ignorance, replication≠causation) and flagged a real clarity bug in
n030, while blunter raters clustered those items near 3. The consensus is the average of blunt
ratings, so a discriminating expert who is *correct but different* reads as *less aligned*.
**Alignment-to-consensus rewards proximity to the average rater, not correctness.** This is the
Entry-27 contrarian tension resurfacing for expertise itself, and it is more troubling than the
eggs-p2 result: there, universal convergence hid it; here, a realistic spread exposes it.

## Consequence: a strong claim pulled to contested
The same dynamic pulled a strongly-evidenced claim, **n023** (honest consensus ~4.4), down to
**A=3.44, CONTESTED (stdev 1.05)** — three miscalibrated raters (mx-boost 1.5, mx-contra low) landed
in its cohort and True_R didn't down-weight them enough to protect it. So a realistic population +
cold-start reputation can make even a strong claim read as contested: a genuine cooperative-function
finding about how much the reputation weighting can (and can't yet) do for aggregate quality.

## Honest caveats on reading this
- **Cold start, single run.** Reputation is designed to accrue over many items/time with the
  True_R weighting iterating (Entry 21 flat→weighted bootstrap). A one-shot run is the *worst case*
  for differentiation; the compression (all 0.71–0.85) is partly that.
- **Blunt-majority population.** 12 of 17 raters are Haiku (hi/mid/lo); the consensus they set is
  blunt, which is *why* the 3 sharp experts read as outliers. A population with more experts would
  sharpen the consensus and the experts would align with it. The conformity bias is real but its
  severity here is amplified by the expert-minority composition — which is itself realistic (experts
  are rare) and therefore a real concern, not only an artifact.

## Bottom line
The rerun's competence test gives a split verdict: the mechanism **catches gross miscalibration** but
**does not reward expertise** — its alignment metric has a tyranny-of-the-median pathology that
penalizes the sharpest raters exactly when they are most useful. This is the most important thing
either run has surfaced about the reputation design, and it points at a concrete fix direction
(reward *information* / calibration, not raw agreement — proper-scoring-rules) before the alignment
channel can be trusted to find experts.

> Note: the reputation finding above — that alignment-to-consensus penalizes expertise — is a
> **cooperative** finding: it holds for a population of entirely good-faith raters, and is exactly
> the kind of thing the reputation system exists to get right.
