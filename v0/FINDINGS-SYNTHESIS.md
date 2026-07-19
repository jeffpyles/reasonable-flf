# Assessment layer — the complete synthesis (state of the investigation, 2026-07-15; §12 added 2026-07-16; §13 added 2026-07-17)

*The single current map of the whole reputation/assessment investigation on this branch. The
historical origin is `archive/REPUTATION-SCORING-SPEC.md` (accurate as history through eggs-p6/BTS but written
before most of what follows); the per-experiment detail is in each `*/FINDINGS.md`. This document
supersedes the spec as the "where we are now" reference. Everything here is reproducible from committed
data + stdlib scripts (index at the end). Written for continuity, for the merge back to `main`, and as
the backbone of the FLF assessment-layer writeup.*

**The question.** In a collaborative argument-mapping site, how do you reliably find the reasonable,
truth-tracking raters and give their judgments due weight — so the map's verdicts approach truth, cold-
start from nothing, scale to millions, survive genuine contestedness, and resist coordinated
manipulation? This branch is the **assessment layer** (evaluate what to believe); ingestion and
structure are elsewhere. The core investigation is on an "Are eggs good for you?" argument graph (79
nodes), with an 8-Sonnet-expert panel (eggs-p5) as the truth oracle — itself validated against the
documented real-world record (see §7) — and is now **generalized to a second case shape**, a
SARS-CoV-2-origins graph with a cross-model oracle and real attacker agents (see §8b).

---

## 1. What we killed (robust negative results)

- **Alignment / level-agreement fails by design** — rewards proximity to the average rater, so it
  buries the sharpest raters (tyranny of the median). Robust to volume, rounds, argument, confidence.
  Every level-agreement variant (incl. bias-corrected, Dawid-Skene) inherits the majority's error.
- **Dawid-Skene / latent-truth models don't escape a blunt majority** — they infer "truth" from the
  same ratings, certifying low-variance mid-clumpers as reliable.
- **Discrimination (ordering-tracking) is the cheap win but self-referential** — recovers competence
  when a competent sub-population exists, but *inverts catastrophically on a biased crowd* (it scores
  agreement with the biased consensus). Cannot self-start from shared bias. Ship it only vs an
  *anchored* consensus, never the raw one.
- **Bayesian Truth Serum is not free** — principled, and it dominates in synthetic worlds, but on real
  agents the prediction-asymmetry it needs failed in aggregate, sortition starves its signal, and the
  per-rater info score rewards the majority bucket. Parked pending first-class prediction elicitation.
- **Winner-take-all (superlinear γ≈6) weighting is fragile and, under a sleeper attack, harmful** —
  it beats a biased majority on clean anchors but shatters on wrong anchors (review) and *amplifies*
  anchor-gaming sleepers (§8). Dominated; retired as a default.

Every failure is the same failure: **a purely internal rule can only measure agreement with the crowd,
so it inherits whatever the crowd gets systematically wrong.** The fix is a small dose of *external*
ground truth (anchors), spent frugally.

## 2. What works — the validated stack

1. **Blind rating, enforced at the tool layer.** Raters never see the consensus/comments while rating
   (`--rating-mode`, forced by a dataset config, no opt-out). The single biggest accuracy lever found
   (coldstart-lab E1: same personas tracked truth at 0.52 with cues visible vs 0.89 blind). ASSESSMENT-
   SPEC v1.5; enforced on all build/rate datasets.
2. **Discrimination vs the *anchored* consensus** as the ongoing rater signal — never vs the raw crowd
   (harmful in split populations).
3. **Calibration (un-distortion) as the aggregator** — fit each rater an affine map on external
   anchors, invert their systematic error, weight by inverse residual variance. Beats winner-take-all
   exclusion: works with *zero* competent raters, degrades gracefully under wrong anchors. **Gated on
   anchor spread** — the fit is unidentifiable when the anchors don't span the scale, so it now declines
   to clustered-anchor sets and falls back to raw (§13).
4. **Camp detection + adjudication for contested regions** — spectral split of the rater-agreement
   matrix finds viewpoint factions with no oracle; a handful of contested anchors adjudicate which
   faction tracks truth. Detection is cheaper and more robust than correction (§8).
5. **Panel anchors** — a diverse frontier-model panel deliberates to forge anchors where no ground
   truth exists (§6).
6. **A thin external-grounding check** — the one thing that catches biases the whole model generation
   shares (§7).

## 3. Cold-start & scale (coldstart-lab)

- **"Reasonableness" is two quantities with very different measurability.** Fine quality-rank among
  good-faith raters is nearly unmeasurable at realistic budgets (per-item reliability r1≈0.013 → ~77
  ratings for a 0.5-reliable estimate); a systematic *disposition* is cheap (r1≈0.107 → ~8 ratings).
  **Assess dispositions/tiers fast, accumulate fine rank slowly.** Chasing a fine global leaderboard
  at low n is measuring noise.
- **Shrinkage isn't a taste knob.** conf = n/(n+K) with **K = (1−r1)/r1**, estimable online from
  split-half reliability. Measured K≈8 for disposition signals, ≈76 for fine rank (the current default
  is ~10× too trusting for the latter).
- **Newcomer cold-start:** blind first pass → a 3–5-item routed **probe slice** (anchors + max-
  separation items) classifies disposition immediately and gives an anchor score → thereafter score by
  discrimination-vs-**anchored** consensus. Competent newcomers reach ~85th percentile in 4–6 ratings.
- **Scale:** anchors are worthless without **routing** — random assignment means almost no user ever
  rates enough anchors (sparse sim: contested consensus stays broken at every density); a ~20% routed
  probe slice flips it to 0.8–0.9 and reputation then propagates ~2 hops to unexposed users. Oracle
  budget scales with the number of *contested divides*, not users.
- **One global reputation scalar is structurally insufficient** — a diligent-but-biased user earns
  good global reputation on the 75% of uncontested items and rides it into the contested ones.
  Disposition must be assessed **per contested region**; only general diligence can be global.
- **The contested-item trigger is BELIEF-CAMP structure, not raw stdev** (E10, corrected by the
  dispersion-regimes cross-check). E10 found stdev tracks consensus error (+0.5 to +0.8) — but only
  because *there* the dispersion was **belief-camp-driven**. Raw dispersion is a valid contested signal
  only when the between-camp variance share is high (our covid belief-camps 82%, eggs-p8 32%); on a
  good-faith *lens* panel it is per-rater-offset noise (fermi covid 16%, AUC 0.42). The reliable
  primitive is the **correlation structure across raters** (spectral camp-detection), which raw stdev
  only proxies when camps dominate the spread. Now live: `reasonable/assessment.py` `detect_camps`
  (+ its `between_group_fraction` diagnostic) and `camp_contested`. See `dispersion-regimes/`.
- **Plain averaging is robust to a *soft* divide** — the heavy machinery is for the strong-majority-
  bias tail, not the common case.

## 4. Disposition vs capability, and the phase transition (eggs-p7 → p10)

Balanced 2×2 runs (disposition × model), pilot-tuned to bracket the transition zone:

- **Disposition dominates capability.** A biased *strong* model (Sonnet) is barely better than a biased
  weak one and *worse than a neutral weak one* — raw capability does not reason its way out of an
  entrenched prior. (p8: disposition main effect +0.36 vs model +0.11.)
- **Capability's protection against bias is DOSE-DEPENDENT** — a strong model erases a *faint* prior
  (p9) but not an *intermediate or moderate* one (p10, p8).
- **Camp detection tracks BELIEF, not capability — and the axis does not rotate.** Across the whole
  transition (p9 faint / p10 intermediate / p8 moderate; split strength 0.23 → 0.61 → 0.75), the
  recovered axis stays disposition (0.96) not model (0.54, chance). The feared failure mode — the
  machinery sorting by *how capable* rather than *what they believe* as the divide weakens — **does
  not occur.**
- **The transition is sharp, not mushy.** Whenever camp-detection reports a divide it is real and
  correctly belief-tracked; on a near-homogeneous population it correctly reports the null (no phantom
  factions). Split strength doubles as a monotone severity dial. This is the deployability result:
  the trigger doesn't false-fire, and when it fires it's right.

## 5. Aggregation against bias (eggs-p6, the origin recipe)

On a genuinely biased population, fixing the consensus needed three things together: **external
anchors placed on the contested frontier + trusted heavily + influence concentrated on the competent**
(superlinear or gated). Later work (§2.3, §8) replaced the fragile γ-concentration with **calibration**
and refined "contested frontier" to the **bias-bitten *evidential*** frontier (§6).

## 6. Panel anchors (eggs-p8-deliberation)

Where no ground-truth source exists, a diverse frontier-model panel (prototype: Fable+Opus) can forge
anchors: each rates blind & independently → revises after seeing the other → a synthesis fixes the
value, the reasonable range, and an anchor-grade verdict, **gated by a value-question guard**.

- **Validated:** on anchor-grade nodes the panel reproduces the independent expert oracle at r≈0.98
  (mean err 0.13); confidence is calibrated (tighter where experts agree); the value-question guard
  caught 2/2 normative claims (incl. one the selector mislabeled). Live on eggs-p8: the panel anchors
  match/beat the expert-derived ones and are **Sonnet-free** (independent of the raters).
- **Placement > quantity:** 5 well-placed anchors match 11 poorly-placed; and the naive "contested
  frontier" (max |crowd−truth|) is **contaminated** with value/uncertain claims — only ~40% are
  anchorable, so deliberate ~2× candidates and let the gate filter.
- **Panel size/composition (panel-size curve):** error falls as √(floor² + noise²/k) — a 1/√k variance
  gain into a **shared-bias floor**. Knee at k≈3–4 for a same-model panel; past that, **spend seats on
  model/vendor diversity (lowers the floor) not more same-model voices (polishes it).** Recommended:
  ~4–5 voices, different models, independently rated + one synthesis pass.

## 7. External grounding — does the model oracle track reality? (eggs-external-check)

The deepest caveat: every "truth" here is model-generated. Scored the Sonnet oracle against an external
reference built from the documented ~2024 record (guideline change, named meta-analyses, textbook
lipidology): **corr +0.95, mean err 0.11** over the 54 nodes where the record clearly speaks. So the
oracle is not free-floating — it tracks documented reality *in this domain*, which retroactively
strengthens every result scored against it. **But** two nodes diverge, both the same way — the models
*over-rate how "unsettled" a settled question is* — a plausibly whole-generation LLM bias invisible
from inside an all-model loop, and the reason a thin external/human check must never fully drop out.
Honest limit: the external reference is still LLM-applied (by Fable), on one well-documented domain;
human ratings / direct source extraction remain the genuine fix.

## 8. Adversarial robustness (eggs-adversarial) — defensive red-team

Offline dose-response: 42 real honest raters + coordinated attackers (naive = real p6 hawk vectors;
jittered/sleeper/sybil synthesized), attacker fraction swept 0→60%, scored with **verdict-level MAE**
(correlation is offset-invariant and *hides* a coordinated level-shift — a metric-choice lesson worth
its own line in any writeup).

- **No defense → captured near 40–50% attackers.**
- **Calibration robustly defeats naive/jittered/sybil even at a 60% majority** — they lie on the
  anchors too, so calibration inverts them. (Sybils are no worse than one attacker.)
- **The sleeper is the crux** — honest on anchors, lying only in the un-anchored gaps — it defeats
  calibration by ~30%, and **superlinear weighting makes it worse** (it concentrates trust on anchor-
  clean liars). *Calibration's reach = the anchors' coverage of the contested frontier.*
- **Detection is the 100%-recall backstop** — camp-detection flags every attack type, including
  sleepers, even where correction fails. Design consequence: **correction + detection + escalation**
  (route flagged blocs to human/verifier review), dense **rotating/secret** anchors, no naive weight-
  concentration, attack-aware metrics.

### 8b. Second domain — covid: real-agent adversarial, the over-certainty attack, the built guardrail

The whole eggs stack was ported to a **second case shape** — a 27-node SARS-CoV-2-origins graph (curated
debate, genuinely unresolved, genuinely camp-split at the top; `covid/`, `covid-adversarial/`). A
cross-model oracle panel (Sonnet×2/Opus/Fable) scored tightly (validates the panel approach on a 2nd
domain), 14 real honest raters formed genuine zoonosis/lab camps, and — the upgrade eggs could only fake
— the sleeper bloc was a **real blind LLM rating run**. Full write-up: `covid-adversarial/FINDINGS.md`.

- **Every eggs hypothesis reproduced on real agents:** calibration beats naive/jittered/sybil to 60%+;
  the sleeper defeats calibration and flips the verdict by ~20–30%; superlinear doesn't help; detection
  is 100%-recall. Generalization confirmed.
- **On a camp-split question, detection is necessary but insufficient (new).** Spectral detection flags
  the suspicious *side* at 100% recall but sweeps in the honest same-side camp (precision ~0.5). The
  isolating signal is **coordinated extremity** (attackers' crux |Δ|=2.2 vs honest lab-leaners 0.66) →
  the robust design is two-stage: find the side spectrally, then an extremity/tightness filter separates
  a manufactured bloc from an honest belief. (Deferred as a live component — ROADMAP #2.)
- **Refusal is directional (new).** Identical sleeper persona, only the goal verdict flipped: **2/8
  agents refused** to manufacture the *contested* (lab-leak) consensus, **0/8** refused the *mainstream*
  (zoonosis) one. The manipulation models most willingly execute is the one that **entrenches an existing
  consensus.** (Small-n, one question — suggestive, flagged as such.)
- **The over-certainty attack is the hardest case, and calibration can't stop it (new, load-bearing).**
  A bloc pushing the *already-leading* answer can't flip the verdict, so it manufactures false
  *certainty* — the calibrated verdict gap is driven from −0.27 past the oracle's warranted −1.20 to
  **−2.24**, collapsing a live question into fake near-settlement and burying the legitimate minority.
  This is the **Semmelweis / minority-truth-survival** failure (a `main` open thread). **Distance-to-
  oracle MAE hides it** (stays 0.3–0.6, because pushing toward consensus keeps cruxes near the oracle) —
  a second "the metric is a defense surface" lesson after correlation-hides-level-shift. **Net thesis:
  for a truth-finding layer the hardest adversarial case is consensus entrenchment, not verdict-flipping
  — and it's the attack real agents most willingly serve.**
- **Built defense: the verdict-certainty guardrail** (`covid-adversarial/certainty_guard.py`, tested
  offline against every committed sweep, no new agent runs). Flags decisiveness beyond the oracle's
  warrant using only the aggregate + oracle reference (no attacker knowledge). Quiet on the honest
  baseline, catches the lab flip as a FLIP at ~10–20%, and fires on the invisible-to-MAE zoo
  over-certainty sleeper at ~40%. The run's most novel finding as a *runnable* detector, not a described
  one. (Live-wiring deferred — ROADMAP #1.)

### 8c. Where to spend the oracle at scale (ORACLE-BUDGET-POLICY.md)
Both reference-dependent defenses (calibration, the guardrail) are blind on un-oracled nodes, so oracle
coverage is the scarce resource. The runs give the triage: the oracle does **two jobs on two node sets**
(calibration anchors on agreed facts; the certainty/verdict reference on the contested frontier), and
**detection is astonishingly cheap** — the guardrail's sensitive signal was carried by **2 oracle'd
verdict nodes**. So points go to **verdict nodes first** (detection), cruxes on demand (correction), a
thin **rotating** anchor layer, nothing on the uncontested tail — nominated by cheap unsupervised signals
(disagreement/stdev, camp-split, spectral flag, centrality). This is active learning: **oracle spend
scales with contestedness, not graph size** — the concrete scalability answer (FLF #4).

## 9. Honest confidence assessment

**~60–65% that the assembled machinery is "reasonably robust" for a real deployment** (nudged up from
~55–65% now that the second domain landed), splitting sharply: high (80%+) confidence in the *component
mechanisms on tested conditions*; lower (~40–45%) that it transfers to the messy real thing. The
load-bearing discounts: (a) **now two domains** (eggs + covid) but still LLM-persona raters on hand-built
graphs; (b) the ground-truth chain is still model-on-model except the external check; (c) the full
pipeline has never run end-to-end live over many rounds with churn (longitudinal integration untested);
(d) the adversarial results, while encouraging and now including **real attacker agents in both
directions**, are still static, worst-case-sleeper-aware, and short-horizon. What the covid run *added* to
confidence: the findings **generalized to a different case shape with real agents**, and it surfaced the
consensus-entrenchment / over-certainty attack (with a working detector) that the eggs run couldn't see —
a known-unknown converted to a known. What still most raises the number from here: a live end-to-end
longitudinal run, a human-rated slice (breaks model-on-model circularity), and an adaptive red-team.

## 10. Map to the FLF assessment desiderata

- *"Calibrating confidence for adversarial information environments"* → §8 (dose-response + defenses).
- *"Out-of-model error / limits of a single analyst"* → §7 (external check) + §6 (panel size/diversity).
- *"Flag correlated evidence treated as independent"* → the sybil result (§8) + rater-dependence note.
- *"Distinguish settled from performed settling"* → detection flags a coordinated bloc as a bloc; the
  extremity second-stage separates a bloc from an honest camp (§8b); and the **certainty guardrail**
  flags a genuinely-live question hardened into fake near-settlement (§8b — the over-certainty attack).
- *"Two-or-more methodologies on the same subquestions"* → §1–§2 is exactly that comparative analysis
  (alignment/DS/discrimination/BTS/calibration/anchors on the same eggs claims).
- *Minority-truth survival (Semmelweis)* → the over-certainty attack + the certainty guardrail (§8b)
  directly target burying a legitimate minority under manufactured consensus.
- Judging: *reason better?* (the whole stack) · *generalize?* (**done — eggs + covid, two case shapes,
  real attacker agents**, §8b) · *scale with compute?* (panel size curve; **oracle spend scales with
  contestedness not graph size**, §8c) · *adversarial robustness?* (§8/§8b, real agents, both directions,
  a built detector) · *compound?* (append-only graph, reusable anchors, per-region reputation).

## 11. Open threads
**Done since the last synthesis:** ✅ Covid graph + real-agent adversarial (both directions) + cross-model
oracle — second domain, generalization confirmed, the over-certainty attack + the built certainty
guardrail (§8b). The **engineering/defense roadmap** (live-wiring the guardrail, the extremity detector,
denser rotating anchors, adaptive red-team, third case shape) now lives in **`ROADMAP-NEXT-VERSION.md`**;
the scale policy in **`ORACLE-BUDGET-POLICY.md`** — both post-deadline. The remaining *research* threads:

1. **Human-rated slice** — the only thing that breaks model-on-model circularity (highest-value gap).
2. **End-to-end longitudinal run** — the assembled flywheel over many rounds with churn (oldest open Q).
3. **Mixed-model panel-size curve** — measure the diversity-vs-floor axis the same-model bootstrap could
   only reason about.
4. ✅ **The validated stack is live** — calibration + camp-detection + guardrail (`reasonable/
   assessment.py`, `graph.py assess`); the phase-2 contested trigger swapped to structural
   (`lifecycle.py`); and the True_R **rating input swapped from `align` to discrimination-vs-anchored**
   when anchors are configured (`assess.py`, ASSESSMENT-SPEC amendment) — the killed tyranny-of-median
   term is gone on anchored datasets, backward-compatible otherwise. And the **node-Agreement aggregate
   is now the calibrated consensus when anchored** (the validated aggregator, computed once, shared with
   discrimination); other dims keep True_R-weighting; anchor-free datasets byte-identical. **All three
   killed rules (align, raw-stdev trigger, True_R-weighted node aggregate) are now replaced in the
   running code, gated on anchors.** 25 tests. The whole validated stack — calibration (aggregator +
   reputation), camp-detection, structural trigger, certainty guardrail — is live; nothing validated
   remains offline-only.
5. **Human-facing cue-channel experiment** — DEFERRED to the Reading/Rating-UI phase (SITE-VARIANTS §).

## 12. Report-vs-graph, graded verify, and model-tiering (added 2026-07-16)

Three results from the deep-research-baseline line of work (`covid-graph/`, `blackholes-graph/`).

**12a. Report vs. assessed graph on the same sources — the over-refutation failure mode.** Fed the
*same* 24 sources / 80 claims to (i) an off-the-shelf deep-research harness and (ii) a graph-building
swarm. The flat pipeline's adversarial verifier **inverted the scientific consensus** — refuted six
central peer-reviewed pro-zoonotic findings (market env samples 0-3, two-lineages 0-3), confirmed
contrarian preprints 6-0/5-1 — while the assessed graph recovered it (zoonotic 3.68 / chain 0.46 vs
research-incident 1.80 / chain 0.12 — the original 4-rater comparison run; after the later
synthetic-origin build-out + hub de-star the live accumulated aggregate is 3.34 / 2.17, still favoring
zoonosis, see `covid-graph/COMPARISON.md`), affirmed the refuted facts (market samples 4.35/5), kept genuine
inferences contested (two-introductions 2.65), and localized the weak spots with three converging
signals (node dispersion, edge support, friction). **Diagnosis is structural, not ideological:** an
adversarial binary *filter* (right for junk) misfires as a truth-*weigher* — default-to-refute fires
on any confident claim in a contested field; claim-*grammar* decides survival (near-unrefutable
attributions/epistemic-limits claims live, refutable object-claims die); binary votes discard the fact
inside a fact+inference bundle. Artifact: `covid-graph/COMPARISON.md`.

**12b. Graded verify — the fix.** Verify now separates *faithfulness/provenance* (the only thing that
drops a claim) from a *0-5 merit score* (annotation, never kills), classifies claim type, and drops
default-to-refute. Live-validated: 0 provenance over-drops, mean support 4.96/5, no synthesis
truncation. `blackholes-graph/harness/workflow_deepresearch.js`.

**12c. Model-tiering — cheap swarms scale breadth, not the crux map.** 16 Haiku vs 4 Sonnet raters,
same lens-personas, 109 covid nodes. Cheap swarm: mean-agreement r≈0.85 (slow rise with N); verdict
**preserved in direction but margin compressed +1.87→+0.79** (central regression toward the middle);
**dispersion does NOT reproduce (r≈0.06) and does not improve with volume.** So the cost-optimal shape
is a **hybrid** — cheap Haiku swarm for scale and the verdict, a small expensive panel reserved for the
dispersion/crux map. Honest limit: the 4-rater Sonnet reference has a noisy dispersion estimate, so the
clean claim is the conditional one (*volume doesn't recover dispersion*); a denser 8-12 Sonnet
reference is the follow-up. `blackholes-graph/harness/TIERING-RESULTS.md`.

**12d. Tiering generalizes across case shapes (covid contested + black holes confident).** Re-ran the
whole tiering test on a built black-holes graph (69 nodes, confident-answer shape). All three findings
hold on both shapes: verdict preserved; cheap means track experts (r 0.88 confident vs 0.85 contested,
MAE lower on the confident case); dispersion fails on both (0.19 vs 0.06) and volume doesn't fix it.
New nuance: **cheap-rater confidence-compression scales with contestedness** — the verdict margin
compresses ~9% on the confident case (safe 4.9 vs 0.4) but ~58% on the contested one (3.7 vs 1.8). So
a cheap swarm's *confidence* is trustworthy exactly when the question is easy and untrustworthy exactly
when it's hard — reinforcing the hybrid (reserve the expensive panel for the contested regions). The
black-holes feedstock was WebSearch-sourced (fetch blocked everywhere), provenance-checked but not
verbatim-quoted — adequate for generalization/tiering, full-fetch re-verification is the round-out.
**All three FLF case shapes now built + assessed** (eggs mundane-contested, covid contested, black
holes confident-answer).

**12e. Dispersion is low-reliability even for experts (denser-reference resolution — revises 12c/12d).**
Added 8 more Sonnet lens-raters (12 total) on a 69-node covid subset to replace the noisy 4-rater
dispersion reference. Result: two *independent* 6-Sonnet panels reproduce their own crux map at only
**r≈0.36** (full-12 reliability ~0.53) — so "which nodes are most contested, read from rating spread"
is an intrinsically noisy signal *for everyone*, not just for cheap raters. A better reference barely
moved the cheap-vs-expert number (0.13→0.15; attenuation-corrected ~0.27). **Net revision:** the
earlier "cheap can't reproduce the crux map, that's what experts are for" is wrong on both ends —
cheap raters partially track it (~0.27, ~half the expert self-reliability) and experts don't
reproduce it cleanly either. The durable cheap-model penalty is the **verdict confidence-compression
on contested questions** (12d finding #4), not dispersion. And the reliable "where's it contested"
signal is the **structural** markers the build produces (antithesis sets, friction flags), *not* the
rating variance — a real caveat for anyone building on rating-spread. `analyze_dispersion_reference.py`.

## 13. Calibration identifiability guard — anchor-spread gating (added 2026-07-17)
Wiring the calibrated aggregator into **covid-graph** (a cooperative honest panel with a 27-node
oracle) *degraded* accuracy: held-out MAE-vs-oracle **0.82 raw → 1.28 calibrated** (55% worse). Root
cause is **unidentifiability, not mis-fit**: covid's confidently-oracle-able anchors are all settled
facts clustered high ([4.08, 4.70], spread 0.62), so the per-rater affine fit has no slope leverage on
the target and collapses every node toward the anchor-truth mean. Proven deeper than "extrapolates
down" — even **offset-only** calibration (slope forced to 1) stays worse than raw (1.08), because with
all anchors at one end you cannot distinguish an additive rater bias from scale compression from no
distortion; the correction is a guess. The existing ridge-toward-identity doesn't rescue it (it
regularizes on *regressor* spread; the ill-posedness is in *target* spread).

**Fix (shipped):** `calibrated_consensus` declines when anchor-truth spread < `MIN_ANCHOR_SPREAD` (2.0
on the 0–5 scale) — returns no consensus, and `assess.compute` falls back to the raw/True_R path
byte-identically (surfaced as `used_calibration: False`). Validated to separate the two regimes cleanly:
covid (spread **0.62**) declines and recovers to 0.82; the adversarial defense (eggs-p8, spread **3.28**
incl. a truth-1.4 low anchor) stays above the floor and still calibrates and still beats a biased mean.
So the earlier "calibration is the aggregator" result (§2.3, §8) holds **wherever anchors span the
scale**; on clustered-anchor cooperative graphs the raw aggregate was already good and is now preserved.
This also makes "anchors configured → calibrate" safe by construction and makes the flagship graphs'
anchor-free disposition automatic. `reasonable/assessment.py` (`MIN_ANCHOR_SPREAD`), `ASSESSMENT-SPEC.md`
§4 amendment; 4 guard tests in `reasonable/test_assessment.py`.

## 14. Reproduce (run from `v0/`, stdlib only)
```
# negative results & rule comparison
python3 eggs-p4/harness/rescore.py
# cold-start & scale
python3 coldstart-lab/e1_rebaseline.py … e10_trigger_tuning.py
# de-confound (disposition vs capability, transition)
python3 eggs-p8/harness/analyze_p8.py ; eggs-p9/… ; eggs-p10/harness/analyze_p10.py
# panel anchors + placement + size curve
python3 eggs-p8-deliberation/placement_check.py ; eggs-external-check/panel_size_curve.py
# external grounding
python3 eggs-external-check/external_grounding.py
# adversarial dose-response (eggs)
python3 eggs-adversarial/adversarial_doseresponse.py
# covid (2nd domain): dose-response both directions + the certainty guardrail
python3 covid-adversarial/covid_doseresponse.py lab
python3 covid-adversarial/covid_doseresponse.py zoo
python3 covid-adversarial/run_certainty_guard.py
# report-vs-graph comparison + model-tiering (2026-07-16)
python3 covid-graph/harness/analyze_comparison.py
python3 covid-graph/harness/analyze_tiering.py
python3 blackholes-graph/harness/pretest_exchange_rate.py
```
Per-experiment detail: each `*/FINDINGS.md` (esp. `covid-adversarial/FINDINGS.md`). Core machinery:
`reasonable/` + `graph.py`. Rater rules: `AGENT-GUIDE.md`. Frozen contract + amendments:
`ASSESSMENT-SPEC.md`. Next-version roadmap: `ROADMAP-NEXT-VERSION.md`. Scale policy:
`ORACLE-BUDGET-POLICY.md`. Vision: `SITE-VARIANTS-CONCEPT.md`.
