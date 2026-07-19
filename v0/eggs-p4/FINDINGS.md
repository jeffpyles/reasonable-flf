# eggs-p4 — high-volume cooperative run: does volume rescue expertise?

**One-line result:** No. Under high volume, three turns, grown confidence, and active
argument, the alignment-to-consensus reputation metric **still ranks the sharp minority
below the blunt majority** — the eggs-p3 tyranny-of-the-median pathology is *robust*, not a
cold-start artifact. This is the most important negative result the project has produced, and
it makes proper-scoring reputation a requirement, not a nice-to-have.

## The run

- **Population:** 60 cooperative agents added on top of the eggs-p3 graph — **52 Haiku "crowd"**
  (26 domain lenses × care levels × priors × rating styles; all good-faith, the realistic
  "hasty, context-weak" majority) and **8 Sonnet "experts"** (lipidologist, nutrition-
  epidemiologist, EBM/meta, endocrinologist, biochemist, biostatistician, guidelines-historian,
  synthesizer), prompted to rate sharply *and* to argue (comment / sharper phrasing / corrective
  ground) when they diverge.
- **3 rounds** with barriers (seed & rate → deepen & respond → converge & influence), per-round
  sortition (neediest-first), event-time reputation accruing across rounds.
- **Scale:** graph grew **60→79 nodes, 58→75 edges** (builders extracted ~19 new claims from the
  source), **~3,460 new rating events** (4,460 total in the log). Coverage: median depth **14**,
  43 items ≥15 ratings, all 60 agents actively rated. Every expert completed all three rounds
  (the workflow stalled mid-round-3 at 2-wide concurrency; the last 4 experts were run to
  completion separately — see Caveats).

## Headline: the expert-vs-crowd True_R gap, round by round

| round | expert True_R | crowd True_R | **gap (exp − crowd)** | expert raw_r (alignment) | crowd raw_r | expert mean conf |
|------:|:-------------:|:------------:|:---------------------:|:------------------------:|:-----------:|:----------------:|
| r1    | 0.663         | 0.690        | **−0.0271**           | 0.894                    | 0.933       | 0.689            |
| r2    | 0.776         | 0.791        | **−0.0156**           | 0.879                    | 0.917       | 0.859            |
| r3    | 0.809         | 0.830        | **−0.0218**           | 0.874                    | 0.920       | 0.911            |

**The gap never closes and never flips.** It narrowed r1→r2 (a flicker of hope that argument was
moving things) and then re-widened by r3. Across every round the experts sit *below* the crowd.

**Why (the mechanism, confirmed at scale):** expert **raw_r (alignment) is persistently lower**
(≈0.87–0.89 vs the crowd's 0.92–0.93) — not because experts are wrong, but because they are
**sharper**. They gave weak inferences (argument-from-ignorance, replication≠causation) low
scores and flagged phrasing/scoping problems where blunt raters clustered near 3. Consensus is
the average of the blunt majority, so a discriminating-but-correct rater reads as *less aligned*
and is down-weighted. **Alignment-to-consensus rewards proximity to the average rater, not
correctness.**

**Volume did not rescue it — this is the key advance over eggs-p3.** Expert confidence grew from
0.69 to **0.91** (they rated a lot; this is no longer a cold-start), yet the penalty *persisted*.
eggs-p3's charitable caveat ("compression is partly cold-start; more items would sharpen it") is
now falsified: more items, more turns, and near-max confidence left the sign unchanged.

## Where the experts land in the population

- **Expert median percentile ≈ 0.10 → 0.17 → 0.17** across rounds — the expert panel sits near the
  *bottom* of the 60-agent distribution the whole time.
- **At r3 the entire top-8 leaderboard is crowd (Haiku); the bottom-8 includes 3 of the 8 experts**
  (s06-biostatistician, s04-endocrinologist, s02-nutri-epi). The single most methodologically
  ruthless personas are the most penalized.

## Did argument move consensus? Barely, and not durably

The experts posted **52 comments** making their case on divergent items. Yet:
- **n023** — "MR + randomized LDL-lowering trials support LDL causality," a strongly-evidenced
  claim — sat at **mean 3.44, stdev 1.05, CONTESTED, unchanged across all three rounds** (the same
  claim that went contested in eggs-p3). Miscalibrated early raters pulled it down; neither the
  arguments nor the reputation weighting rescued it. Reputation is computed from rating-alignment,
  **not** from whether an argument persuaded — so a persuasive expert gains no standing for
  persuading, and a correct-but-outvoted expert stays outvoted.
- Aggregate lifecycle at r3: 15/79 nodes *settled*, 63 *provisional*, 1 *contested*. The graph
  matured but did not converge on the experts' sharper reads.

## Reputation variance is real but tiny — and inverted

True_R spread across all 60 agents: **stdev 0.019, range 0.783–0.862.** The mechanism compresses
everyone into a narrow band *and* orders that band the wrong way (crowd on top). So it is not that
reputation fails to discriminate — it discriminates weakly and in favor of blandness.

## What this does and does not show

**Shows (robustly):** the alignment channel has a structural tyranny-of-the-median bias that
survives volume, multiple turns, high confidence, and active argument. If we want reputation to
*find* expertise rather than *punish* it, alignment-to-consensus cannot be the scoring rule.

**Does not show / caveats (honest):**
- **Model is an imperfect proxy for expertise.** "Sonnet = expert" conflates sharper reasoning with
  correctness; a sharper rater is not always right. The finding is about *how the metric treats
  discriminating raters*, which is the relevant thing, but don't over-read it as "the metric
  suppresses truth" — it suppresses *distance from the mean rater*, which correlates with expertise
  here by construction.
- **Blunt-majority composition (52/8) amplifies severity.** Realistic (experts are rare), but a
  more expert-dense crowd would sharpen consensus and shrink the gap. The *sign* is the robust
  finding; the *magnitude* is composition-dependent.
- **Legacy eggs-p3 ratings remain in the log** and feed the consensus these raters are scored
  against (including p3's miscalibrated raters), making the target consensus somewhat blunter. The
  reputation comparison itself is computed only over the 60 new agents.
- **Single run; depth median 14** (short of the ≥15 aspiration — the mid-run stall plus a reduced
  per-round cap lowered coverage). Directional, not a precise effect-size estimate.
- **Methodology note:** the orchestration workflow died mid-round-3 (2-wide concurrency on a
  4-core box → ~7-hr run that stalled after ~7 hrs with 4 experts unrated). Those 4 experts were
  completed in a separate identical pass against the near-final graph, so they rated a slightly
  more-settled graph than the crowd did. If anything this *helps* the experts (more information,
  more settled targets) — and they still landed at the bottom, which strengthens the finding.

## The fix this points to

Replace (or supplement) alignment-to-consensus with a **proper scoring rule**: reward a rater for
*information / calibration* — being right about where the evidence lands and, ideally, predicting
the *settled* value or the informed-subset value — rather than for agreeing with the current
average. Candidate directions to prototype next:
1. **Peer-prediction / Bayesian-truth-serum** style scoring (reward raters who are "surprisingly
   common" among the informed, not merely common).
2. **Score against the eventual settled value**, not the live mean, so early-correct contrarians
   are rewarded when the graph catches up (ties into the Entry-27 era design).
3. **Weight the consensus itself by True_R before scoring alignment** (a stronger fixed-point) —
   but note this run already used True_R-weighted aggregation and it was insufficient, so this
   alone likely won't fix it.

The concrete next experiment: re-score this exact dataset (the eggs-p4 event log is fixed) under a
proper-scoring rule and check whether the expert panel moves from the bottom decile toward the top
— a clean, cheap A/B on real rating data with no new agent run required.
