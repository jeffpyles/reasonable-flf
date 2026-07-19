# eggs-p4 re-score — can a proper scoring rule find the experts the live system buries?

**Setup:** the eggs-p4 event log is frozen. We re-scored the *identical* rater×item matrix
(307 (target,dim) items, 60 run agents + 17 legacy) under five reputation rules and compared each
to the **hidden competence labels the mechanism never saw** — tier (expert/crowd) and care
(high/mid/hasty) — via Spearman rank-correlation, plus the expert panel's median percentile. No new
agent run: `harness/rescore.py`, output `harness/rescore.json`.

## Results

| rule | what it rewards | expert median pctile | Spearman vs hidden competence |
|---|---|:--:|:--:|
| **true_r (live)** | agreement w/ True_R-weighted consensus **level** (+ authoring) | 0.167 | **−0.64** |
| align (baseline) | agreement w/ consensus **level** | 0.10 | −0.54 |
| align_debiased | level-agreement after removing each rater's constant offset | 0.067 | −0.57 |
| ds_reliability | Dawid-Skene: low **noise** around a reliability-weighted latent value | 0.075 | −0.55 |
| **discrimination** | tracking item-to-item **signal** (corr w/ leave-one-out item mean) | **0.766** | **+0.11** |

*Percentile: 0.10 = experts near the bottom, 0.90 = near the top. Spearman: +1 recovers competence
perfectly, 0 is blind, negative is inverted.*

## What this establishes

**1. The live reputation is not merely blind to competence — it is *inverted*.** Spearman −0.64
against the hidden care/expertise labels. The system's top-6 are all mid/high-care *crowd*
raters; the bottom cluster is the biostatistician, endocrinologist, nutrition-epidemiologist,
biochemist. This is the strongest single statement of the tyranny-of-the-median pathology yet.

**2. Every rule that scores agreement with the consensus *level* fails the same way.** Plain
alignment (−0.54), reliability-weighted Dawid-Skene (−0.55), and even bias-corrected alignment
(−0.57) all keep experts in the bottom ~7–17th percentile. Two sub-findings matter:

- **The penalty is not a calibration offset.** Removing each rater's *constant* bias
  (`align_debiased`) makes experts score *slightly worse*, not better. So experts are not simply
  "the people who rate everything 1.5 lower." Their disagreement is **item-specific**: they push
  down the *particular* weak inferences (argument-from-ignorance, replication≠causation) that the
  crowd overrates, item by item. You cannot fix this by letting raters carry a calibration offset.
- **Reliability-weighting doesn't escape the majority.** Dawid-Skene infers "truth" from the
  ratings, and with a 52-vs-8 blunt majority the latent value is crowd-centered; low-variance
  mid-clumpers then read as "reliable." This directly refutes the naive "just use a latent-truth
  model" fix — and confirms the FINDINGS.md caveat that True_R-weighted aggregation (which the live
  system already does) is structurally insufficient.

**3. Only scoring the *signal* recovers competence.** `discrimination` — how well a rater's
ratings track the item-to-item ordering (do they separate strong items from weak ones?) — is the
sole rule that flips the sign: experts rise from the 10th to the **77th percentile**, correlation
goes from −0.64 to **+0.11**, and for the first time the top of the leaderboard contains experts
(s04-endocrinologist is #1, s01-lipidologist top-6) while the bottom is entirely hasty/off-domain
crowd (food-safety, budget-shopper, culinary-culture).

## The mechanism, stated plainly

Experts and the careful crowd broadly **agree on the ordering** of claims (which are strong, which
are weak). Where experts diverge is on the **level** of the specific weak items — they mark a
fallacy 1.5 where the crowd says 3. Level-agreement scoring punishes exactly those divergences,
which are the experts' most valuable judgments. Signal-tracking scoring ignores the level and
rewards the ordering, which is where expertise actually shows up. **The fix direction is: stop
rewarding agreement with the consensus level; reward tracking the consensus signal (and, better,
being early-right about where the signal is going).**

## Honest limits

- **+0.11 is weak.** Signal-tracking separates careful-from-hasty better than expert-from-crowd —
  several high-care crowd raters discriminate well too. It moves the sign, not the mountain.
- **Still endogenous.** `discrimination` correlates a rater with the *crowd's* leave-one-out mean;
  it rewards tracking the crowd's ordering. It works here only because experts largely share that
  ordering. It cannot, on its own, crown a correct minority whose *ordering* the crowd rejects —
  the deep consensus-vs-truth (Semmelweis) problem is untouched.
- **Competence labels are our construction** (Sonnet=expert; care tags), a defensible proxy, not
  ground truth. "Model = expertise" conflates sharper reasoning with correctness.
- One DS variant tested; alternatives (robust/heavy-tailed noise, non-reliability-weighted latent
  value) could differ, but majority-capture is the expected qualitative outcome for any
  purely-endogenous latent-truth model under a blunt majority.

## Recommended next steps

1. **Add a signal-tracking reputation mode** to `assess.py` as a selectable alignment rule
   (score a rater by rank-correlation / covariance with the weighted consensus ordering, not by
   `1 − |v − mean|`). Cheap, and this analysis says it strictly improves competence-recovery. Left
   unimplemented pending your sign-off, since reputation is the one subsystem we deliberately kept.
2. **Break the endogeneity** to get past +0.11, two options worth prototyping:
   - **Anchor items with known answers** — plant a handful of claims whose reasonableness is
     externally verifiable (a clean fallacy, a textbook-correct inference) and score raters partly
     on those. External ground truth is the only thing that lets a correct minority outrank a
     blunt majority.
   - **Meta-prediction elicitation** — collect each rater's guess of how others will rate, enabling
     a true peer-prediction / Bayesian-Truth-Serum score (reward the "surprisingly common"). Needs
     a new elicitation field, but it is the principled proper-scoring answer.
