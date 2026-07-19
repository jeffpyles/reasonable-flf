# Model-tiering test — results (two case shapes: covid + black holes)

*Run on **both** FLF case shapes — covid (genuinely contested) and black holes (confident-answer) —
so the findings are tested for generalization, not read off one graph. Reproduce:
`python3 covid-graph/harness/analyze_tiering.py` and `python3 blackholes-graph/harness/analyze_tiering.py`.
The covid results are below; the black-holes results and the two-case synthesis are at the end.*

## Setup

- **Reference arm:** 4 Sonnet lens-raters (evidential / Bayesian / skeptic / domain), bloc `b1`.
- **Cheap arm:** 16 Haiku lens-raters — the *same 4 lenses × 4 seeds*, bloc `cheap`. Only the model
  differs; personas, task, and graph are identical. Subsampled stratified-by-lens for N=4/8/16
  (N/4 seeds per lens, so all four lenses stay represented — depth varies, diversity held constant).
- 109 covid nodes, blind Agreement ratings.

## Results

| cheap-arm N | r(mean vs Sonnet) | r(dispersion vs Sonnet) | MAE(mean) /5 |
|---|---|---|---|
| 4  | 0.806 | 0.118 | 0.368 |
| 8  | 0.831 | 0.080 | 0.338 |
| 16 | 0.848 | 0.057 | 0.313 |

**Verdict (the two top-level answers, node Agreement mean):**

| | Sonnet ref | Haiku-16 |
|---|---|---|
| zoonotic spillover (n001) | 3.67 | 3.17 |
| research incident (n002) | 1.80 | 2.38 |
| margin (n001 − n002) | **+1.87** | **+0.79** |

Ordering **preserved** (both rank zoonotic above lab-leak) — but the margin compressed by more than
half.

## What this says (and doesn't)

1. **Verdict survives the cheap swarm — direction, not confidence.** Haiku gets the right answer
   (zoonotic > lab-leak) but regresses *both* answers toward the middle (zoonotic down 0.50,
   lab-leak up 0.58). Cheap raters are more wishy-washy; they'll tell you *which* way a contested
   question leans, but they understate *how decisively*.
2. **Mean-agreement is moderate (~0.85) and improves only slowly with N.** The cheap swarm captures
   the broad structure of the expert means but with real error (MAE ~0.31/5) and central
   compression. Notably this is **below** the eggs pre-analysis (~0.90) — consistent with covid
   being a harder, more contested domain where the capability gap bites more.
3. **Dispersion barely reproduces (r≈0.06–0.19), and volume doesn't help.** The Haiku swarm's
   crux-spread does not track the expert panel's. **But the follow-up below revises *why*** — it is
   not mainly that Haiku is incapable; it is that the dispersion signal is intrinsically noisy even
   for experts (see "Resolving the dispersion question"). The robust claim: a cheap swarm does not
   *cleanly* recover the crux map — but neither does a second expert panel.

**This originally carried a caveat** — the 4-Sonnet reference's own dispersion estimate is noisy, so
we could only make the conditional claim. **That caveat is now resolved** (next section), and it
changes the conclusion.

## Resolving the dispersion question (denser reference)

We added **8 more Sonnet lens-raters** (2 more seeds × 4 lenses → 12 Sonnet total) on a fixed 69-node
covid subset (54 contested-by-design nodes + 15 settled anchors), and measured the dispersion signal's
own reliability. Reproduce: `python3 covid-graph/harness/analyze_dispersion_reference.py`.

| (contested-only, 54 nodes) | value |
|---|---|
| Sonnet 6v6 dispersion split-half (independent halves) | **0.36** (→ full-12 reliability ~0.53) |
| Haiku 8v8 dispersion split-half | 0.43 (→ full-16 reliability ~0.60) |
| Haiku-16 vs Sonnet-**12** dispersion r (observed) | **0.15** |
| Haiku-16 vs Sonnet-**4** dispersion r (old reference) | 0.13 |
| attenuation-corrected true Haiku-vs-Sonnet r (approx) | **~0.27** |

Three findings, and they revise #3 above:

- **The expert dispersion "ceiling" is low.** Two *independent* 6-Sonnet panels reproduce their own
  crux map at only **r≈0.36**; the full 12-Sonnet estimate has reliability ~0.53. So "which nodes are
  most contested, read off rating spread" is an **intrinsically noisy signal even for experts** — a
  genuine, humbling caveat on the "dispersion localizes the cruxes" value proposition.
- **A better reference barely moved the number** (0.13 → 0.15). So the original near-zero was *not*
  mainly a small-reference artifact — improving the ruler revealed no hidden strong signal. The low
  correlation is real, and it is dominated by the signal's intrinsic noise, not by a Haiku-specific
  incapacity.
- **Judged against the low ceiling, the cheap shortfall is modest.** Corrected for attenuation, the
  true Haiku-vs-Sonnet dispersion correlation is ~0.27 — cheap raters *do* partially track where
  experts disagree, at roughly half the experts' own self-reliability. The raw 0.06 badly overstated
  the gap.

**Net revision.** The earlier strong claim — "cheap can't do dispersion; that's what experts are
for" — is weakened on both ends: cheap raters aren't as bad as 0.06 looked, and experts themselves
don't reproduce the crux map cleanly. So the durable cheap-model penalty is the **confidence/mean
compression on contested questions** (finding #4), *not* dispersion-reproduction; and the bigger
lesson is a caveat on the signal itself — **dispersion/crux-localization is low-reliability for
everyone**, which anyone building on rating-spread should know. (The attenuation correction is
approximate at these low reliabilities; treat ~0.27 as "modest positive," not a point estimate.)

## The architecture this implies (FLF dim 4)

Not "cheap replaces expensive," and not "expensive everywhere" — a **hybrid**:

- **Cheap swarm (Haiku ×~8) for scale, the verdict, and a serviceable mean** — at a fraction of the
  cost. This is where "quality scales with quantity of cheap scrutiny" holds.
- **A few strong raters where *confidence* must be trusted** — on genuinely contested questions,
  cheap raters regress the verdict toward the middle (finding #4). Reserve the expensive model for
  reading *how decisively* the evidence leans on the hard questions, where that compression bites.
- **Do not over-invest either tier in the dispersion/crux map** — after the denser-reference study,
  we know that signal is low-reliability *for everyone* (expert self-reliability ~0.36–0.53), so
  neither more cheap raters nor a small expert panel recovers it cleanly. Treat rating-spread as a
  weak, noisy hint about where the cruxes are, not a precise map — and lean on the *structural*
  crux markers (antithesis sets, friction flags) that the build already produces deterministically.

That's the honest scalability story, revised by the data: cheap agents scale breadth and get the
verdict; a little expensive scrutiny buys trustworthy *confidence* on hard questions; and the
crux-localization-by-dispersion that we'd hoped distinguished the graph is itself noisy — the
structural markers, not the rating variance, are the reliable "where's it contested" signal.

## Second case: black holes (confident-answer shape)

Built from a WebSearch-sourced feedstock (fetch was blocked in every environment we tried; a fresh
instance assembled 17 sources / 46 claims across all five strands via WebSearch, provenance-checked
but not verbatim-quoted — see `DEEP-RESEARCH-BRIEF.md` / `REPORT.md`). 69 nodes, same tiered setup
(4 Sonnet ref + 16 Haiku, 4 lenses × 4 seeds).

| cheap-arm N | r(mean vs Sonnet) | r(dispersion vs Sonnet) | MAE(mean) /5 |
|---|---|---|---|
| 4  | 0.845 | 0.217 | 0.285 |
| 8  | 0.874 | 0.183 | 0.262 |
| 16 | 0.884 | 0.192 | 0.240 |

Verdict: safe answer (n001) **4.92 Sonnet / 4.63 Haiku**; catastrophe (n002) **0.38 / 0.48**. Margin
**+4.55 → +4.15**. Ordering preserved; compression tiny.

## Two-case synthesis — what generalizes

| | covid (contested) | black holes (confident) |
|---|---|---|
| mean-agreement r (N=16) | 0.85 | 0.88 |
| MAE (N=16) /5 | 0.31 | 0.24 |
| dispersion r (N=16) | 0.06 | 0.19 |
| verdict margin Sonnet → Haiku | +1.87 → +0.79 | +4.55 → +4.15 |
| **compression of the margin** | **~58%** | **~9%** |

Three findings hold on **both** shapes, and one new nuance emerges:

1. **Verdict survives the cheap swarm on both** — direction preserved every time.
2. **Cheap raters track the expert mean better on the *confident* case** (r 0.88 vs 0.85, MAE 0.24 vs
   0.31). Less genuine ambiguity → less room for a weaker rater to diverge.
3. **Dispersion reproduces poorly on both (0.06 / 0.19) — but the denser-reference study shows *why*,
   and it isn't mainly the cheap model.** The crux-by-dispersion signal is low-reliability *for
   everyone*: independent expert panels reproduce their own dispersion map at only r≈0.36, and a
   better reference barely moved the cheap-vs-expert number (0.13→0.15; corrected ~0.27). So the
   revised claim is *not* "a cheap swarm can't do what experts can" — it's that **rating-spread is a
   noisy crux signal regardless of model tier**; the reliable "where's it contested" markers are the
   *structural* ones (antithesis sets, friction flags), not the rating variance.
4. **The confidence-compression scales with contestedness** — the durable cheap-model penalty. Cheap
   raters regress the verdict toward the middle, but that only bites when the truth is *both* far
   from the middle and genuinely uncertain: covid's margin collapses ~58%, black holes' ~9%. So a
   cheap swarm's *confidence* is trustworthy exactly when the question is easy and untrustworthy
   exactly when it's hard — a concrete reason to spend a little expensive scrutiny on the contested
   regions specifically.

The hybrid conclusion (cheap for scale/verdict, a small expensive panel for the dispersion/crux map)
is therefore not a one-graph artifact — it holds across a genuinely-contested and a confident-answer
case, with the added rule that the cheaper the model, the more you should distrust its *confidence*
on the hard questions specifically.

## Note on the black-holes deep research

The graded-verify workflow itself was **validated** on a live run (0 provenance over-drops, mean
support 4.96/5, no synthesis truncation) — the fix works. Fetch, however, was blocked in every
environment (HTTP 403 on all hosts incl. example.com), so the feedstock was assembled via WebSearch
rather than full-text fetch: source existence/attribution verified, verbatim quotes not asserted,
support scores calibrated down accordingly. Adequate for the third case shape (generalization +
tiering); a full-fetch re-verification of the sources is the natural round-out when web access
returns, and would upgrade the black-holes baseline toward covid's full-fetch rigor.
