# Panel-anchor deliberation — can a frontier-model panel forge external-verification anchors?

*Validates the "deliberated-panel anchor" idea: where contested ground badly needs an anchor but
no ground-truth source exists, have a small panel of known-good-faith frontier models deliberate to
a consensus value + spread + anchor-grade verdict, and accept it as an anchor only when they
genuinely converge on an evidential question. Prototype panel: **Fable + Opus** (the full-site
version would use the then-current best, most-aligned, ideally cross-vendor models). Method: each
model rates blind and independently → each revises after seeing the other → a synthesis fixes the
range + a value-question flag, with the anchor verdict computed symmetrically in code. 13 nodes (10
tightest-expert-spread anchors + 3 loosest high-value contested), scored against the eggs-p5
8-expert panel. Harness: `eggs-p8-deliberation/harness/workflow_delib.js`; output: `anchors.json`.*

## Result — the mechanism validates on all three axes

**1. Convergent validity is near-perfect on the nodes we'd actually use.** Over the 11 anchor-grade
nodes, panel-vs-p5-oracle correlation is **+0.983**, mean absolute difference **0.13** on the 0–5
scale (max 0.46). On the full 13 it's +0.80 / 0.32, dragged only by the two value questions the
panel correctly refused to anchor. In other words: on evidential claims the two models converged on,
they reproduce the independent expert panel almost exactly.

**2. Confidence is calibrated — the panel knows when it shouldn't be an anchor.** Panel confidence
correlates **−0.39** with the experts' actual disagreement (more confident where experts agree), and
the panel's self-declared "reasonable range" width correlates **+0.42** with expert stdev (wider
where experts genuinely disagreed). Not perfect, but pointed the right way on both — enough for the
confidence gate to do real work rather than rubber-stamp.

**3. The value-question guard caught both value claims — including one the setup mislabeled.** The
panel flagged **n030** ("worth avoiding cheap precautions under uncertainty") and **n042** ("whether
eggs are *good for you* should be judged by weighing net nutrition…") as fundamentally normative and
set both `anchor_grade=false`, despite tight model agreement on each. n042 had been filed as a plain
"anchor" node by the selection script; the panel correctly recognized a *should*-claim with no
evidential fact of the matter. This is the guard working exactly as intended: high AI-consensus is
*not* sufficient for anchoring — the claim also has to be the kind of thing that has a truth.

The one large panel↔expert divergence (n030: panel 3.5 vs p5 1.21, the only case where the p5 mean
fell outside the panel's stated range) is itself a value question — precisely the case where an AI
panel and an expert panel can legitimately disagree and neither is "ground truth." That it shows up
*only* on a flagged, non-anchored node is reassuring, not worrying.

## What this buys the design

- **A third anchor-supply channel, now evidenced.** Alongside constructed reasoning-checks and
  resolve-by-time questions, deliberated-panel consensus can manufacture anchors on contested
  evidential ground — the place anchors are most valuable and hardest to source. Expensive per node
  (here ~5 frontier-model calls each), so reserved for high-value contested items, but that is the
  intended use.
- **Independence from the rater pool.** The panel is Sonnet-free, so for eggs-p8 these anchors are a
  reference that shares no model family with the Sonnet raters — converting a standing caveat
  ("oracle and competent tier are both Sonnet") into a genuinely independent check for the adjudication
  analysis. (Honest limit: Fable and Opus are both Anthropic, so vendor-level priors stay correlated;
  the production cross-vendor panel would go further.)
- **The "spread of reasonable opinion" output is first-class, not a byproduct.** A panel that returns
  "wide range, low confidence, not anchor-grade" has correctly *classified* a node as genuinely
  contested/uncertain — useful metadata in its own right, and the natural input to the v1.4 dispersion
  display.

## Guardrails carried forward
- Panel anchors must be **labeled as such and confidence-gated** (we accept only `gap ≤ 0.5`,
  `reasonable-range ≤ 1.5`, `not is_value_question`).
- **Value/ought questions never become truth-anchors**, however strongly the panel agrees — they stay
  in the "display the camps" regime. The guard caught 2/2 here, but it is a model judgment and should
  be spot-audited.
- Convergence is not correctness: two models sharing a blind spot would converge confidently and
  wrongly. The cross-vendor panel and periodic scoring against any available real ground truth are the
  mitigations; on this set the blind-spot risk did not materialize (0.13 mean error vs an independent
  panel), but it remains the mechanism's core hazard.

## Addendum — anchor PLACEMENT drives value even within this good panel set (offline, `placement_check.py`)

Thread 2's core, tested offline with the anchors in hand (the still-needed piece is forging anchors on
the target graph's *own* contested frontier — an agent run, deferred). Across 300 random 5-node
subsets of the 11 anchor-grade panel nodes, a subset's mean **p8-contestedness** (how far p8's flat
consensus sits from truth on those nodes — i.e. how squarely they land on p8's bias-bitten frontier)
predicts its calibration quality:

- corr(mean placement, calib-full held-out) **+0.69**; corr(mean placement, calib-biased-only) **+0.71**.
- Bottom-tertile placement (mean contestedness 0.39): calib-full +0.59, **biased-only −0.19 (inverts)**.
- Top-tertile placement (0.60): calib-full +0.71, biased-only +0.13.

So the FLYWHEEL "anchors must sit on the contested frontier" principle holds for *panel-forged*
anchors specifically, and it bites hardest in the nc=0 (no-competent-raters) regime, where
badly-placed anchors flip calibration negative. Implication: the p6-forged anchors worked on p8 only
because enough of them happened to land on p8's frontier; forging a panel directly on p8's own
top-contested nodes should do strictly better — the concrete prediction the deferred same-cluster
run will test.

## Reproduce
`anchors.json` is the committed output; re-run with `Workflow(workflow_delib.js, args={nodes:[…]})`.
Validation numbers: the block in `eggs-p8/harness/analyze_p8.py` §2 (panel-vs-p5) and the standalone
checks in this run.

## Addendum 2 — same-cluster forge on p8's OWN frontier (the deferred agent run)

Ran the deliberation on p8's own top-12 contested nodes (by |flat−truth|) and re-tested calibration
(`anchors_p8frontier.json`). Two findings, one confirming the prediction and one more useful:

**(a) Placement quality beats quantity — prediction confirmed, efficiently.** On a common held-out
set, the 5 same-cluster anchors match-or-beat the 11 p6-forged ones: calib-full **0.75 vs 0.73**,
calib-biased-only (nc=0) **0.63 vs 0.58** — with **fewer than half as many anchors**. Better-placed
anchors are more *efficient*; you need fewer of them. (Margins are small on tiny n — 11 held-out, 5
anchors — so read this as "same-cluster is at least as good with 5 as p6 with 11," directionally
confirming the placement principle, not a large effect.)

**(b) The raw "contested frontier" is contaminated — the real refinement.** Selecting the frontier by
max |flat−truth| netted only **5 anchor-grade of 12**: the panel correctly flagged **2 as value
questions** (n030 "avoid cheap risks", n043 "CVD should dominate the verdict") and rejected **5 more
on the range-width gate** as genuinely uncertain (n038, n002, n008, n039, n056 — the panel agreed on a
point value but judged the reasonable range too wide to anchor). So the nodes where the crowd is
farthest from truth are a *mix* of (i) bias-bitten evidential claims — anchorable; (ii) value
questions — no truth to anchor; (iii) genuinely-uncertain claims — not anchorable, hard for the panel
too. Only (i) yields anchors.

**Design refinement to "place anchors on the contested frontier":** it means the **bias-bitten
*evidential*** frontier, not raw max-divergence. The panel's own confidence + value-question gate
separates the three automatically (a real virtue), but the consequence is you must deliberate ~2× the
candidate nodes to net enough anchor-grade ones — or pre-filter candidates to non-value, tighter-
dispersion claims before spending the panel. **Convergent-validity caveat:** on the 5 that passed,
4 match the p5 oracle within ~0.2 but **n065 is off by 1.1** (the panel under-penalized an overstated
"BV 97%, highest among common foods" claim the oracle and the external check both docked harder) — a
reminder the gate is not infallible and an occasional wrong anchor slips through, which is exactly why
anchor error-tolerance (calibration ≥ γ-gating) and the thin external check stay load-bearing.
