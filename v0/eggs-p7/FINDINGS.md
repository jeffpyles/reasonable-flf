# eggs-p7 — the mild/graded divide on real agents: does the contested-region machinery hold when the divide is soft?

*A real-agent run designed to sit in coldstart-lab E9's "transition zone": a weak, overlapping
directional bias rather than eggs-p6's cliff. 28 agents rated all 79 node claims — 8
strong-lean + 8 slight-lean (Haiku) toward the dietary-cholesterol-is-dangerous view, 6 neutral
(3 Haiku + 3 Sonnet, same prompt), 6 evidence-tracker (Sonnet). Truth oracle = the eggs-p5
8-expert panel (identical node ids). Reproduce: `python3 eggs-p7/harness/analyze_p7.py`.*

> **Blindness caveat (important — read before trusting the accuracy numbers).** This run was
> *intended* blind but was **not cleanly blind**: the `get-node` command raters used returns the
> running `agreement.mean/n/stdev`, and the graph scaffold carried 136 eggs-p6 comments (30 stating
> explicit rating values), all visible to raters. The graph started at zero ratings so early raters
> were genuinely blind, and a seq-order anchoring test found **no detectable anchoring** to the
> running mean (early-half rater distance-to-final-mean 0.331 vs late-half 0.321), so the numbers
> are probably close to what a blind run would give — but this is a muddy-middle protocol, not a
> clean blind one, and it is **not** a valid data point for the blind-vs-social question. The leak
> is now fixed at the tool layer (`graph.py get-node --rating-mode`, ASSESSMENT-SPEC §7 amendment);
> the next run should use it.

---

## The divide landed where intended

*(All accuracy figures below carry the blindness caveat above — read as "intended-blind,
no measured anchoring," not "clean blind.")*

Per-tier accuracy (correlation of a rater's node ratings with oracle truth):

| tier | n | accuracy | 
|---|:--:|:--:|
| lean_strong | 8 | +0.54 |
| lean_slight | 8 | +0.63 |
| neutral | 6 | +0.78 |
| competent | 6 | +0.89 |

Monotone in intended bias, evidence-led-minus-lean gap **+0.25** — a real but *soft* divide (p6's
was +0.88). This is the regime the run was built to probe, and the graded prompt worked: even
Haiku modulated bias strength as instructed (strong < slight), which the earlier synthetic E9
couldn't confirm.

## Five results

**1. Plain averaging is robust to a soft divide — the heavy machinery earns little here.** The
flat (unweighted) consensus already tracks truth at **+0.86** on the held-out contested items,
despite 16 of 28 raters carrying the bias. This confirms E9's "flat is robust to partial bias"
on real agents: the dramatic p6-style rescue (−0.7 → +0.9) is a *strong-majority-bias*
phenomenon, not a soft-divide one. **Design consequence: the default site posture should be
simple averaging; the expensive contested-region machinery is for the strong-bias tail, not the
common case.**

**2. The global "population structure" statistic badly under-reads a real, recoverable divide.**
The spectral split-strength was **0.31 — barely above the p5 no-divide null (0.27)** — yet the
same clustering *recovers* the disposition split at **0.82 accuracy** and adjudication off it
works perfectly (result 4). So a near-null global strength reading does **not** mean "no camps."
This is the sharpest confirmation yet of E9's warning: **do not trigger the machinery off a
global structure score.** The per-item signal is the right trigger — contested items do show
higher rating stdev (0.51 vs 0.38 settled) and more two-humped shape (between/within-half 2.61
vs 2.27), the v1.4 histogram data. The margin is modest in the soft regime, so the trigger must
be *sensitive* (E9 already showed false-positive machinery is nearly harmless).

**3. Soft divides cost convergence, not correctness, in the clustering.** A single
power-iteration restart at 200 steps gave seed-dependent splits (one unlucky seed inverted the
adjudication to 0.09); at 400 steps with 40 restarts + majority-vote consensus the split is
fully stable (assignment stability 1.00, recovery 0.82 every restart). The soft divide makes the
top two eigenvalues close, so it needs more iterations than p6's sharp split — a cheap fix, but
a real "watch out" for the implementation: **always multi-restart the clustering; never trust
one seed.** (Confound to log honestly: the recovered axis tracks disposition 0.82 but also model
0.79 — they're entangled in this population. The neutral tier disambiguates: neutral-Haiku land
2/3 on the evidence-led side, so the axis is *primarily* disposition, not pure model.)

**4. Once clusters exist, one anchor adjudicates reliably even when the divide is soft.**
1-anchor camp-pick win rate **1.00** (2- and 3-anchor also 1.00), stable across all 40 clustering
restarts. The E5 result — cheap adjudication of a discovered divide — holds on real agents in the
hard regime, not just p6's easy one.

**5. Calibration (un-distortion) is the most robust aggregator, and works with no competent
raters.** Held-out contested repair (flat baseline +0.86):

| aggregator | held-out corr |
|---|:--:|
| flat baseline | +0.86 |
| calibrate FULL pool (28) | **+0.90** |
| winning-cluster mean (adjudicated) | +0.88 |
| calibrate LEAN-only (16, nc=0) | +0.76 |
| oracle competent-tier mean (6) | +0.71 |

Two notes. **(a)** Calibrating from the 16 lean raters *alone* — no competent raters in the pool
— still reaches **+0.76**: real soft bias is a recoverable *distortion* that retains rank
information, unlike E9's synthetic worst case where bias *erased* rank info and calibration
collapsed to ~0. So on realistic agents, calibration degrades gracefully. **(b)** The calibrated
crowd (+0.90) beats the raw 6-expert subset (+0.71) — with only 8 held-out items the small expert
panel is noisier than the un-distorted full crowd. Concentrating on a tiny "best" set is *not*
automatically better than calibrating everyone.

## The heterogeneity / ranking-speed question (E2 on a mixed population)

Split-half per-item reliability r1 (how fast raters can be finely ranked; higher = fewer ratings
needed):

| population | r1 | reference |
|---|:--:|:--:|
| eggs-p5 crowd (homogeneous Haiku) | 0.013 | ~77 ratings for 0.5-reliable rank |
| **eggs-p7 all 28 (mixed model + disposition)** | **0.052** | ~4× faster than p5 |
| eggs-p7 leans only (16) | 0.023 | |
| eggs-p7 evidence-led (12) | 0.035 | |
| eggs-p6 (strong disposition) | 0.107 | ~8 ratings |

**Heterogeneity roughly quadruples ranking efficiency** versus the homogeneous crowd — a diverse
real userbase should be rankable faster than the pessimistic p5 number suggested. And the cleanest
lever is model/capability: **neutral-prompt Haiku accuracy +0.68 vs neutral-prompt Sonnet +0.87** —
a 0.19 gap from model alone at identical disposition. Capability is a large, stable, fast-detectable
axis. This directly answers the earlier question: a site will separate "more vs less capable
raters" much faster than "which of two similar good-faith users is slightly better," because the
former is a real durable trait and the latter is mostly noise (the p5 lesson, unchanged).

## What this changes in the recommended design

- **Default simple, escalate on per-item bimodality.** Soft divides don't break averaging;
  reserve clustering/adjudication/calibration for items whose rating distribution goes two-humped.
  The global population-structure score is *not* a usable trigger (it read null on a real divide).
- **Agreement-character is the right first-class output** (your instinct): tight-unimodal =
  reliable (and consensus-anchor candidate), wide-unimodal = uncertain, two-humped = contested →
  fire the machinery. But tightness ≠ correctness (p6's hawks agreed tightly on wrong answers), so
  keep the two anchor kinds separate: auto-promoted consensus-anchors (tight + diverse) for
  measuring diligence, and scarce externally-verified adjudication-anchors placed on contested
  ground.
- **Prefer calibration as the aggregator in contested regions.** It was the most robust arm here,
  needs no competent minority, and degrades gracefully; cluster-adjudication is a close, cheaper-
  on-anchors second. Both beat weight-concentration.
- **Multi-restart any clustering.** Soft divides make single-seed spectral splits unreliable.
- **Heterogeneity is a feature for cold-start.** Real diversity speeds ranking; capability is the
  dominant fast axis. Measure r1 live (per E2) and set the trust-ramp K from it rather than
  hard-coding — a diverse population self-reports "you can trust ranks sooner."

## Honest limitations

- **Provenance:** a session-limit interruption led to two workflows running concurrently, so
  several lean agents were rated twice. Ratings supersede by latest-seq in the fold, so the final
  state is a clean 28×79 (verified), but the kept rating for those agents is their second blind
  pass. No evidence of bias from this, but recorded for the record.
- One domain, one bias direction, model-family-shared oracle (same caveats as p6). The
  disposition/model confound is real — a cleaner future run would cross bias × model fully (biased
  Sonnet, neutral Haiku at every level) to separate the axes.
- Held-out contested set is 8 items; treat the aggregator deltas (0.86→0.90) as directional. The
  soft-divide flat baseline being already-high means this run has little dynamic range to
  separate aggregators — its main news is the *trigger* and *ranking-speed* results, not a
  fine aggregator ranking.
- LLM personas likely understate human trait stability; the ~4× heterogeneity speed-up is a lower
  bound if real humans differ more durably than prompted Haiku.

## Suggested next

1. **Fully cross bias × model** (2×2+) to de-confound disposition from capability in camp detection.
2. **Per-item bimodality trigger, made precise**: calibrate a dip statistic against the flat-repair
   need across p5/p6/p7 so the site has a tuned "spin up the machinery" threshold.
3. **The protocol A/B** (blind vs social-visible) remains the highest-value untested lever from
   the coldstart synthesis — unaffected by any of the above.
