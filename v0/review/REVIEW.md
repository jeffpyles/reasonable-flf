# Fresh-eyes review of the reputation-scoring investigation

*A critical read of the whole branch (specs, code, data, findings), plus four new offline
experiments (`review/*.py`, all runnable from the repo root, stdlib only). Written 2026-07-10.*

**TL;DR.** The core negative results are solid, reproducible, and honestly caveated — the
tyranny-of-the-median finding in particular is real and well-established. But several headline
*positive* numbers are softer than they read: the eggs-p6 "+0.92 reputation recovery" is partly
true-by-construction, the recipe it validates has a catastrophic and unmeasured failure mode
(3+ wrong anchors out of 10 → confidently wrong consensus, worse than no reputation at all),
and the eggs-p4 Spearman table is computed against a competence label that eggs-p5's own
analysis showed is partly anti-informative. Two diagnosed-but-untested fixes were testable on
data already in hand; I tested them: the per-item surprisingly-popular reformulation **cannot**
rescue the p5 dataset (the elicitation, not the scoring shape, is the binding constraint), and
per-rater **bias-correction** (calibrate raters against anchors and invert their error) matches
the exclusion recipe's accuracy while degrading gracefully where it collapses. Finally, there
is a family of ideas the investigation hasn't touched — most importantly using the *argument
structure itself* (coherence scoring), constructed reasoning-anchors for the R dimension,
viewpoint clustering before anchoring, and any adversarial/strategic analysis at all.

---

## 1. What I verified

All headline analyses reproduce byte-for-byte from the committed logs:

- `rescore.py`: live True_R −0.64 vs competence, experts at 10th–17th pctile; discrimination
  flips to +0.11 / 77th. ✓
- `analyze_p6.py`: disc-only −0.85; contested anchors @0.9 trust → rep~comp +0.92; γ=6 needed
  to flip held-out consensus (+0.90). ✓
- `test_flywheel.py`: crowd competence range 0.61–0.97, no flywheel headroom on a merely-noisy
  crowd; care label vs actual competence = **−0.33**. ✓
- `bts_score.py` / `bts_density_sweep.py` / `validate_bts.py`: as documented. ✓

The engineering discipline is genuinely good: append-only logs, deterministic folds, every
finding a runnable script, honest caveat sections. The critiques below are about
interpretation and coverage, not correctness of the arithmetic.

---

## 2. Where the existing analyses are weaker than they read

### 2.1 eggs-p6's rep~comp +0.92 is close to true-by-construction
Anchor score = agreement-with-oracle-truth on 10 contested items. Competence = correlation-
with-oracle-truth on all 79 items. With anchor-trust 0.9, Raw_R *is* a noisy subsample of the
competence measure — a +0.92 correlation between a quantity and a superset of itself is not
surprising and shouldn't be read as "the mechanism found the experts." The *non-trivial*
content of eggs-p6 is real but narrower: (a) generalization to the 8 held-out biased items,
and (b) the γ result (correct reputation + linear weighting still loses to mass). Those are
the findings; the +0.92 is nearly an identity. Also note the held-out evaluation set is **8
items** — a correlation over 8 points deserves an uncertainty bar before "held-out +0.90"
becomes a design pillar (bootstrap it, or replicate on a second bias type).

### 2.2 The recipe's knobs were tuned and evaluated on the same data
blend=0.9, γ=6, anchors=10 were selected by sweeping *on the same log* whose held-out numbers
are reported as the result. Mild but real overfitting risk: the honest statement is "there
exist knob values that work on this population," not "0.9/6 is the recipe." The γ needed is
already known to scale with minority odds (the caveats say so); a pre-registered replication
on a second bias type / composition is the missing confirmation.

### 2.3 NEW RESULT — the recipe is catastrophically fragile to wrong anchors
`review/anchor_error_sensitivity.py`. Corrupt k of the 10 contested anchors with the *biased
crowd's own value* (the realistic failure: an anchor editor who shares the popular error):

| k bad anchors | held-out corr (worst-case) | random-subset mean |
|:--:|:--:|:--:|
| 0 | +0.90 | +0.90 |
| 2 | +0.88 | +0.89 |
| 3 | **+0.69** | **+0.27 ± 0.51** |
| 4 | **−0.71** | −0.36 ± 0.47 |
| 5 | −0.82 | −0.82 |

It's a cliff, not a slope — and past the cliff the system is *confidently wrong* (worse than
flat aggregation, because γ=6 concentrates all influence on whoever matches the wrong
anchors). High trust × superlinear weighting is a force multiplier for anchor quality **in
both directions**. Since FLYWHEEL-FINDINGS elevates anchors to "load-bearing requirement,"
the anchor-integrity problem (who audits anchors, how many independent sources per anchor,
what's the wrongness budget) is now the top open design question, ahead of any scoring-rule
work. ~70–80% anchor correctness is the empirical floor on this dataset.

### 2.4 The eggs-p4 headline Spearmans are computed against a partly-invalid label
`test_flywheel.py` (eggs-p5) established that the prompted care label is **anti-correlated
(−0.33) with measured competence** within the crowd. But the rescore table's headline numbers
(−0.64, −0.54, +0.11 …) use exactly that care ranking as "hidden competence" for 52 of 60
raters. The tier separation (expert pctile 0.10 → 0.77) survives because expert/crowd is the
dominant contrast, but the Spearman *magnitudes* are not interpretable — discrimination's
"+0.11" understates it (the spec already knows: +0.53 when measured properly), and the
alignment rules' inversions are likely *overstated* in magnitude for the same reason. Cheap
fix: re-run `rescore.py` scoring competence as corr-with-p5-expert-truth on the node-A subset
(the oracle exists for all 79 nodes), and update the table. The qualitative story will hold;
the numbers will become citable.

### 2.5 Oracle and "competent tier" share a model family
In p6, "truth" = mean of 8 *Sonnet* experts (p5) and the competent minority = 4 *Sonnet*
raters, while the biased majority is prompted-biased *Haiku*. Some of the 0.89 "competence"
is plausibly shared model priors/style rather than truth-tracking — the deck is stacked in
the direction the experiment wants. Worth one run where the oracle comes from a different
family (or humans) before "competence = corr with oracle" is trusted as far as it's being
trusted.

### 2.6 Smaller technical notes
- `assess.py` alignment scores each rater against an aggregate that **includes their own
  rating** (and their True_R inflates their own pull on it) — a mild rich-get-richer artifact;
  LOO would be cleaner. Same self-inclusion in `analyze_p6.py`'s discrimination-vs-weighted-
  consensus (with γ=6 the top rater partially correlates with themselves).
- Discrimination as raw Pearson has no evidence-shrinkage: a rater with 5 lucky ratings can
  outscore one with 100 at slightly lower r. Fisher-z shrinkage or feeding r through the
  existing conf machinery as the *raw* input fixes it (the live plan presumably does the
  latter — make it explicit).
- `n_assessments` counts volume regardless of difficulty → confidence is farmable by rating
  many easy items (matters once adversaries exist; see §4.4).
- BTS bins (2.0, 3.5) are arbitrary and interact badly with central-tendency crowds (the mid
  bin swallows everything). Any future BTS work should treat binning as a swept knob or go
  continuous.

---

## 3. Two diagnosed fixes were testable on data in hand — now tested

### 3.1 Per-item surprisingly-popular does NOT rescue eggs-p5 (`review/sp_per_item.py`)
BTS-RUN-FINDINGS cause #3 blames the per-rater multi-bucket info average and names the
per-item SP decision as the right shape — but never scores it, though 1,653 rating+prediction
pairs sit on disk. Scored: on the full saturated p5 data, **only 3 of 79 items have a
non-trivial SP decision at all** (SP bin ≠ plurality bin); expert percentile under SP scoring
is 0.21–0.23, *below* bts_full's 0.40. The predictions are so hedged and self-anchored that
actual-vs-predicted ratios barely ever cross. Implication: **the scoring-shape fix alone is
dead on this dataset — elicitation quality is the binding constraint.** The "cheapest next
test" in BTS-RUN-FINDINGS (concentrated pool + per-item SP + first-class elicitation) should
be re-ordered: without first-class, incentivized, *specific* predictions ("predict the naive
reader," not "predict everyone"), there is nothing for any SP formulation to score. This
strengthens the case for spending the next run's budget elsewhere (anchors/coherence) and
keeping BTS parked.

### 3.2 Bias-CORRECTION matches bias-EXCLUSION and is far more robust (`review/bias_correction.py`)
The recipe treats biased raters as noise to zero out (γ=6 ≈ gating). But a shared directional
bias is *information* — a predictably-miscalibrated instrument can be inverted. Fit each
rater an affine map truth≈a·rating+b on the same 10 anchors (ridge toward identity), apply
to all their ratings, then aggregate with a **plain unweighted mean** — no reputation, no
fixed point, no γ:

| arm | held-out corr | held-out MAE | all-79 corr |
|---|:--:|:--:|:--:|
| flat baseline | −0.84 | 1.96 | 0.21 |
| affine-corrected, uniform mean | +0.90 | 0.81 | 0.49 |
| corrected + inverse-residual-variance wts | **+0.91** | 0.60 | **0.88** |
| recipe (trust .9, γ=6) reference | +0.90 | **0.44** | — |

And under the same worst-case anchor corruption that collapses the recipe to −0.82,
correction+invvar degrades gracefully: **+0.87 at k=5**. Intuition: exclusion bets everything
on identifying the few good raters (anchors wrong → bet wrong → γ amplifies the disaster);
correction extracts signal from *all* raters and a bad anchor only degrades the calibration
noise. It also sidesteps the minimum-competent-count constraint — corrected biased raters
corroborate each other, so the "≥2–3 verified raters per item" floor softens. The recipe's
MAE is still better on clean anchors (0.44 vs 0.60), suggesting the production answer is a
**hybrid: calibrate everyone, then weight moderately (γ≈1–2) by post-calibration residual** —
most of the accuracy, much less of the fragility, and less winner-take-all gaming surface
than γ=6. This deserves to be a first-class arm in any follow-up run.

### 3.3 Structural coherence is unmeasurable in current data — a design gap (`review/coherence_check.py`)
See §4.1 for the idea. On eggs-p4 (the only log with node-A *and* edge-A from the same
raters), exactly **17 (rater, ground, edge, dependent) self-triples exist across all 60
raters** (one rater has 3; no one else has >1). Sortition assigns items independently, so it
never co-locates a rater on an edge plus both endpoints, and p5/p6 collected node-A only. If
coherence scoring is wanted, assignment must hand out **connected subgraphs** (edge +
endpoints as one unit). That's a one-line change to `gen_assign.py` for the next run.

---

## 4. Ideas the investigation hasn't considered

Ordered by (my estimate of) value ÷ cost.

### 4.1 Use the graph. Structural-coherence scoring (novel, crowd- and oracle-independent)
Every rule tried so far treats ratings as a flat rater×item matrix — the argument *structure*
is unused. Under v1.2 semantics (node-A ≈ P(claim), edge-A ≈ P(support|ground)), a single
rater's ratings across a connected region carry internal consistency constraints (roughly:
p(dependent) shouldn't sit far below p(ground)·p(edge) when that's the main ground — a
Dutch-book test). Incoherence is a **carelessness signal that needs no consensus, no anchors,
and no oracle** — the only signal in the whole space with that property, and it's unique to
argument mapping (flat crowdsourcing has no structure to check against). It can't confirm
competence (a coherent crank exists — necessary, not sufficient), but as a *filter* it's
exactly what the failed "care" label wanted to be, and it's strategy-resistant in an
interesting way: faking coherence requires actually doing the reasoning. Blocked only by the
assignment-design gap in §3.3.

### 4.2 Constructed reasoning-anchors: the R dimension is anchorable by fiat
Open question 3 (where do anchors come from without an oracle?) assumes anchors must be
*truth* anchors on contested empirical claims — the hardest kind to source. But the p3/p4
mechanism data says experts distinguish themselves mostly on *inference quality* (weak-
inference items: argument-from-ignorance, replication≠causation), i.e. on **R-type judgments,
where correct answers can be manufactured**. Plant synthetic items with known-bad reasoning
(a clean base-rate fallacy, a valid syllogism, a subtly circular argument) — the crowdsourcing
literature's "gold questions," but for reasoning. Cheap to generate, objectively answerable,
domain-transferable, refreshable to resist leakage. Then reputation-from-R-anchors transfers
to weight on A-dim aggregation. This reframes the anchor-supply problem from "resolve
contested truth" (expensive, political) to "author logic puzzles" (cheap, verifiable) — and
per §2.3, anchor *correctness* is the one thing the system cannot compromise on, which favors
exactly the anchors whose answers are provable. Testable in the very next run: seed ~10
constructed R-anchors, check reputation-from-R-anchors recovers the p6 competent minority.

### 4.3 Cluster viewpoints first, then spend anchors on adjudication
eggs-p6's population is literally bimodal, and everything downstream treats that as a
per-rater calibration problem. Unsupervised structure comes first: cluster raters by rating-
profile similarity (or fit a 2-component latent model — the multi-truth Dawid-Skene family).
The clusters are discoverable *without any oracle*; anchors are then needed only to decide
**which cluster to trust** — an O(#clusters) anchor budget instead of O(#raters), likely
2–3 anchors instead of 10, which matters enormously given §2.3's fragility cliff. Bonus: the
cluster structure itself is honest product output for genuinely contested questions ("two
schools of thought, here's each one's consensus") rather than a false single number — which
v1.4's dispersion-histogram amendment gestures at but reputation currently ignores. Also the
principled home for the rater-dependence problem: an LLM (or human) crowd is not independent
draws, and weighting N copies of the same viewpoint N× is double-counting; cluster-aware
aggregation (weight viewpoints, then raters within viewpoints) fixes the pathology that made
16-vs-4 mass beat correct reputation in the first place — γ=6 is a blunt instrument doing a
job clustering does surgically.

### 4.4 Nobody has modeled an adversary
Every persona across p3–p6 is good-faith; the one strategic note in the corpus is a single
line ("discrimination can be gamed by copying the consensus"). Before any of this ships:
- **Consensus-copiers** — score ~1.0 discrimination by parroting visible means. (Mitigations:
  score only pre-reveal ratings, or score against *later* raters' consensus — the temporal
  rule below.)
- **Confidence farmers** — `n/(n+K)` counts volume, not difficulty; rate easy items to max
  conf, spend the reputation on the contested item you care about.
- **Sybils** — every unknown account carries weight ≥ prior 0.15; 20 sock-puppets × 0.15
  outweigh 4 experts × 0.85 *under linear weighting*. Notable un-noted synergy: superlinear γ
  crushes sybils (0.15^6 ≈ 0) — a second argument for γ that the docs never make.
- **Mutual-admiration rings** — the authoring input (rep-weighted mean R of your items) plus
  circular aggregation is the textbook EigenTrust collusion surface; the standard fix
  (propagate trust only from a pre-trusted seed set) is, once again, anchors.
A p7 run (or even a pure simulation on p4 logs: inject synthetic copier/sybil/ring raters,
verify each rule's response) would be cheap and would move this work from "finds competence"
to "finds competence and can't be trivially farmed" — a different, and shippable, claim.

### 4.5 Temporal scoring is sitting untested on data that already has rounds
FINDINGS.md candidate #2 ("score against the eventual settled value") was never tried, yet
eggs-p4 has three barriered rounds: score round-1 ratings against the round-3 (or final,
anchor-corrected) aggregate. Rewards *early-correct* over conformist, is copy-resistant
(there's nothing to copy yet when you commit), and needs zero new elicitation. One afternoon
of offline analysis; if the p4 log is too settled for movement (n023 never moved), it still
quantifies exactly that.

### 4.6 One scalar True_R conflates judgments the grid already separates
v1.3 carefully types Agreement by target (truth vs fit vs support), and the R/C/A axes ask
different questions — but reputation collapses everything into one number used to weight all
of it. A rater sharp on logic (R) need not be right on facts (A-truth), and anchor-earned
factual authority shouldn't automatically amplify their votes on framing/values questions
(quiet technocratic capture). At minimum split **R-rep** from **A-rep** (the data to test
whether they even correlate exists in p4); longer-term, per-domain decay is the standard
answer. Cross-run identity is also unexplored: the same 60 agent IDs exist in p4 and p5 —
does p4-earned discrimination reputation *predict* p5 competence? That's the "does reputation
transfer" question, free.

### 4.7 Prior art worth mining before building more bespoke machinery
The anchor recipe is (unknowingly?) reinventing **test equating with anchor items** from
psychometrics — IRT linking, differential-item-functioning detection (≈ the contested-cluster
insight) — a mature literature with answers to "how many anchors, where, how robust."
Likewise **multi-task peer prediction** (Correlated Agreement, Shnayder et al. 2016; DMI,
Kong 2020) gets strategy-proofness *without* meta-prediction elicitation — exactly the gap
between discrimination (cheap, gameable) and BTS (proper, elicitation-starved) — though all
of them still assume the majority signal is informative, so they complement rather than
replace anchors. And the γ-vs-collusion tradeoff is EigenTrust's pre-trusted-peers problem.

---

## 5. What I'd actually do next (revised priority list)

1. **Re-baseline eggs-p4 against oracle competence** (§2.4) so the canonical table is citable.
   Half a day.
2. **Wire discrimination into `assess.py`** as planned (spec open-question 1) — still right,
   with Fisher-z/conf shrinkage and LOO consensus (§2.6) — but gate it: discrimination is now
   known to invert on biased crowds, so it ships only alongside an anchor input, never alone.
3. **Make the hybrid calibrate-then-weight aggregator a first-class arm** (§3.2) and re-run
   the p6 analysis + min-count analysis under it. It matched the recipe at a fraction of the
   fragility; if it holds up it *replaces* γ=6 as the default and demotes γ to a knob.
4. **Anchor-integrity design** (§2.3): error budget ~20–30%, redundancy/audit story, and the
   two supply-side answers — constructed R-anchors (§4.2) and cluster-then-adjudicate (§4.3)
   — prototyped offline on p6 data first (clustering needs no new run).
5. **Next agent run (p7) = adversarial + coherence run**, not another BTS run: connected-
   subgraph assignment (unlocks coherence scoring, §4.1/§3.3), seeded constructed R-anchors,
   and injected copier/sybil/ring personas (§4.4). BTS stays parked until prediction
   elicitation can be first-class (§3.1 shows nothing else will move it).
6. **Longitudinal flywheel** (spec open-question 5) stays valuable and is strengthened by
   doing it with the hybrid aggregator + planted anchors from day one.

The one-sentence version: the project has correctly killed alignment, correctly identified
discrimination + anchors + concentration as the live recipe — but the recipe's real risk
surface is **anchor integrity and strategic behavior**, both currently unexamined, and the
two most promising unexplored signals (**bias-correction** and **argument-structure
coherence**) both reduce how much weight the anchors have to carry.
