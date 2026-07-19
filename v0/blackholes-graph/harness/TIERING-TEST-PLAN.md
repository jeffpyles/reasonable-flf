# Black-holes run + model-tiering test — pre-registered plan

*Written before the run so the design is fixed in advance. This run does three jobs at once:
(1) the **third FLF case shape** (LHC black-hole safety — a "confident answer" with a vocal
contrarian minority), completing generalization across all three cases; (2) the first run with our
two process improvements — a **fixed deep-research verify prompt** and **deliberate model
selection**; and (3) a **pre-registered model-tiering experiment** that turns "use cheaper agents?"
into a measured result (FLF dim-4 scalability evidence).*

## The question

**"Could a high-energy particle collider (the LHC) create a black hole that destroys Earth?"**
Mainstream physics is confidently *no* (Hawking radiation; the cosmic-ray safety argument — nature
has run this experiment for billions of years), with a documented fear/contrarian minority (the
2008 Wagner/Sancho lawsuits). This is the "confident-answer" shape — deliberately *low*
contestedness, unlike covid. That matters for the test design (see §3).

Existing assets to reuse/supersede: `sources/blackholes/` (index.json, BRIEFING.md) and two small
earlier graphs (`swarm-blackholes/`, `swarm-blackholes-2/`, ~23 nodes each, different harness). We
build fresh from deep-research feedstock, mirroring `covid-graph/`.

---

## 1. Process improvements to implement this run

### 1a. Fixed deep-research verify prompt (the highest-leverage change; it's free)

The covid run's verify step inverted the scientific consensus — a *structural* failure of using an
adversarial binary **filter** as a truth **weigher** (see `covid-graph/COMPARISON.md` §1). Fix the
verify prompt, not the model:

- **Separate two judgments.** (a) *Faithfulness*: is the claim actually supported by its quote/source?
  (b) *Soundness*: if it's an inference, is the inference well-grounded? Score these independently.
- **Score 0–5, not refute/confirm.** A binary vote discards the settled fact inside a
  fact-plus-inference bundle; a graded score keeps it.
- **Normalize claim grammar before judging.** An attribution ("the paper argues X") and an
  object-claim ("X is true") must be judged on the same footing — otherwise near-unrefutable
  meta-claims survive and refutable facts die (the covid grammar-asymmetry artifact).
- **Drop "default to refute if uncertain."** In a contested field a rebuttal is always findable;
  that rule deletes every confident claim on both sides. Replace with "score what the evidence
  supports; uncertainty → a middling score, not a kill."
- Keep the adversarial search for **provenance** (is this a real source? a hallucinated quote?) —
  that is what adversarial verification is *good* at. Use it to filter junk, not to weigh merit.

### 1b. Deliberate model selection (grounded in the covid natural experiment)

The covid run proved the money isn't where the value is: **Opus 4.8 on the badly-designed verify
task inverted the consensus; Sonnet 5 on the well-designed build/rate tasks produced good output.**
Task design substitutes for model tier. Default assignment for this run:

| Role | Model / effort | Why |
|---|---|---|
| Deep research: scope/search/fetch | Sonnet, low–med | bounded; capability not load-bearing |
| Deep research: verify | Sonnet, med | with the fixed prompt, the design carries it |
| Deep research: synthesis | Sonnet/strong, high | whole-corpus view |
| Build: bulk extraction | Sonnet, high (held) | **held fixed to isolate the rating-tier axis** |
| Build: friction + coherence pass | strong, high | category-error / correlated-evidence judgment |
| **Rating: the test variable** | Haiku vs Sonnet | see §2 |

Build model is **held at Sonnet** so this run changes only *one* axis (rating tier). Build-tiering
(can Haiku authors extract/structure/friction-flag?) is a separate, later experiment.

---

## 2. The model-tiering test (pre-registered)

### What we already know — eggs-p5 pre-analysis (52 Haiku "crowd" + 8 Sonnet "expert", 79 shared items)

- **Mean tracks cheaply and plateaus fast.** r(cheap-swarm mean, expert-panel mean): K=1 → 0.86,
  K=3 → 0.90, K=5 → 0.90, K=8 → 0.906, plateau ~0.909 by K=20. **~6–8 cheap raters recover ~all of
  the expert mean.** Ceiling ≈ 0.91 (a small irreducible expert premium volume doesn't close).
- **Dispersion does NOT reproduce.** r(cheap-stdev, expert-stdev) = **0.26**. The cheap swarm gets
  the average right but *where it's contested* wrong — and dispersion is our headline signal.
- Caveat baked into these numbers: the eggs crowd was deliberately **biased**, so "cheap" is
  conflated with "biased" (crowd mean carried a −0.16 bias). And dispersion is a second moment,
  noisy at N≈8 from either population — the 0.26 may be partly sample-size, not capability.

### Hypotheses

- **H1 (mean):** ~6–8 honest Haiku raters reproduce the Sonnet panel's per-item mean at r ≥ 0.88.
- **H2 (dispersion):** cheap raters under-reproduce the dispersion map at small N, but it **improves
  with N** (volume closes a second-moment estimation gap). Test the curve, don't assume the 0.26.
- **H3 (hybrid is cost-optimal):** cheap swarm for the mean/verdict + a small strong pass for
  dispersion/friction beats either pure tier on quality-per-token.
- **H4 (verdict robustness):** the cheap arm ranks the top-level answers in the same order as the
  expensive panel (the "is it safe?" verdict is preserved).

### Design — one graph, several rating arms (change only the rating tier)

- **Build once, at Sonnet** (held). Personas identical across arms — vary *only* the model.
- **Reference arm E:** 4 honest lens-personas {evidential, Bayesian, provenance-skeptic, technical}
  × **Sonnet, high** (same as covid).
- **Cheap arms C-N:** the *same 4 lens-personas* × **Haiku, low**, instantiated at **N = 4, 8, 16**
  (personas × independent seeds; vary the prompt by seed index for independent draws). Same personas
  + same task + different model = clean capability isolation, and the N-sweep tests H2 directly.
- **Honest cheap raters only** — no assigned bias — to decontaminate the eggs bias/​capability
  confound. (A separate biased-cheap arm could be added later to study crowds, but not here.)

### Dispersion cross-check on the EXISTING covid graph (important)

Black holes is a *confident-answer* case → **low contestedness → thin dispersion signal**, which is
exactly the wrong place to test dispersion-reproduction. So run the **dispersion criterion on the
covid-graph**, which is already built, genuinely contested, and already has the 4-Sonnet reference:
add Haiku arms (N = 4, 8, 16) to the existing `covid-graph` and measure r(cheap-stdev, Sonnet-stdev)
vs N there. No rebuild — just extra rating rounds on the graph we have. This gives H2 a real test on
contested data while black holes supplies the generalization + verdict-robustness (H1, H4) evidence.

### Acceptance criteria (measured separately — they come apart)

1. **Mean-agreement:** r(cheap-mean, expert-mean) per item, per N. Pass H1 at r ≥ 0.88.
2. **Dispersion-reproduction:** r(cheap-stdev, expert-stdev) as a function of N (on covid). Report
   the curve; H2 passes if it rises materially with N.
3. **Verdict-preservation:** cheap arm's ranking of the top answers == expert arm's. (H4)
4. **Cost:** tokens per arm → quality-per-token frontier; identifies the H3 hybrid sweet spot.

### Held fixed / varied

- **Held:** build model (Sonnet), personas, the graph itself, effort *within* an arm, aggregation.
- **Varied:** rating model tier (Haiku vs Sonnet), N (4/8/16).

---

## 3. Caveats that are themselves instructions

- **Use honest cheap raters**, not biased ones — else we can't separate "cheap fails" from "biased
  fails" (the eggs confound).
- **Test dispersion on covid, not black holes** — the confident-answer case is too settled to
  exercise the dispersion criterion; use it for the mean/verdict criteria and generalization.
- **Build-tiering is NOT tested here** (build held at Sonnet). One axis at a time.
- **Exchange rates won't transfer exactly** across domains; the *structure* of the finding (mean
  cheap, dispersion needs volume-or-experts) is what we expect to generalize.
- If H2 holds (volume closes dispersion), the headline becomes a clean dim-4 win: **assessment
  quality scales with quantity of cheap scrutiny, not with model spend.** If H2 fails, the headline
  is the hybrid (H3): cheap means + a small expensive dispersion pass.

---

## 4. Next-session execution checklist

- [ ] `blackholes-graph/config.json` (question above, `rating_mode_only: false` for build)
- [ ] Deep research on the question **with the fixed verify prompt** (§1a) → `harness/REPORT.md`
      + `harness/sources.json` (mirror the covid recovery format)
- [ ] Build harness: reuse `covid-graph/harness/workflow_build.js`; black-holes cluster personas
      (theory/Hawking-radiation · cosmic-ray-safety-argument · collider-mechanics ·
      risk-analysis/​contrarian-minority · synth-closer); **Sonnet authors**; add the strong
      friction pass
- [ ] Tiered assess harness: arm E (Sonnet×4) + arms C-4/8/16 (Haiku); same lens-personas
- [ ] Covid dispersion cross-check: Haiku arms (4/8/16) on existing `covid-graph`
- [ ] `analyze_tiering.py`: mean-agreement, dispersion-vs-N, verdict-preservation, tokens/arm
- [ ] Fold results into `FINDINGS-SYNTHESIS.md` (dim-4 scalability result)

*No runs yet — this is the pre-registration. Execute next session when the token window is fresh.*
