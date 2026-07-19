# Mechanisms — how assessment works today

*The current, running assessment systems, described in the present tense. This is deliberately
separate from the story of how we arrived at them — that story is condensed in
[RESEARCH-ARC.md](RESEARCH-ARC.md), told in full in
[FINDINGS-SYNTHESIS.md](v0/FINDINGS-SYNTHESIS.md), and the frozen technical contract
is [ASSESSMENT-SPEC.md](v0/ASSESSMENT-SPEC.md). Here, each mechanism gets: what it does, why it is
this way, where it lives in the code, and its honest status. For the philosophy, see
[VISION.md](VISION.md); for how graphs are structured at all, see the grammar section of
[PROJECT-OVERVIEW.md](v0/PROJECT-OVERVIEW.md).*

**Status key:** LIVE = running in the engine today · BUILT = implemented and tested offline, not yet
wired into the default pipeline · DESIGNED = specified but not implemented.

---

## 1. What gets rated, and on what scale — LIVE

Everything on the map is rated 0–5, but *what the number means* depends on what kind of thing is
being rated, because "do I agree?" is not one question:

- **Claims** (ordinary argument nodes) are rated on **Agreement** — how true/well-supported is this?
- **Evidence nodes** (facts anchored to a source outside the graph) are rated on **fidelity** — does
  the source really say this? The *quality* of the source (methodology, power, bias) is rated
  separately, on the evidence node's outgoing support edge.
- **Ought nodes** (value and action claims) are rated on **endorsement** — do you endorse this? —
  never on "truth," and never reputation-weighted (see §4).
- **Support edges** are rated **conditionally**: grant the FROM claim as true, then rate how strongly
  it supports the TO claim. This separates "is the premise right?" from "does the premise actually
  carry the conclusion?" — a distinction flat text constantly blurs.
- Separately from all of the above, every phrasing of a node is rated on **Reasonableness** (is it
  fairly and logically stated?) and **Clarity** — quality of expression, kept deliberately distinct
  from agreement so that disagreeing with a claim doesn't mean burying its best formulation.

Where: `v0/reasonable/ops.py`, `validate.py`; verb reference in `v0/AGENT-GUIDE.md` §9.

## 2. Blind rating — LIVE, enforced at the tool layer

While rating, a rater cannot see the current consensus, other ratings, comments, or the author's
reputation. This is not an option a dataset can politely request; presentation datasets carry a
no-opt-out flag and the read path masks the cues. It is the single biggest accuracy lever we
measured (truth-tracking rose from 0.52 with cues visible to 0.89 blind, in simulated-rater
testing), and it removes the oldest bias of live debate: rewarding whoever performs best in the
moment.

Where: masking in `v0/reasonable/queries.py`; the flag in dataset `config.json`.
Why we trust it: FINDINGS-SYNTHESIS (cue-visibility experiments).

## 3. Reputation — LIVE, spent narrowly

Raters earn a truth-reputation score, and reputation weights influence — but narrowly and
deliberately:

- Reputation is earned by **tracking reality where reality is checkable**: performance against
  anchor questions and against the anchor-corrected consensus — never by simple agreement with the
  raw crowd. (Agreement-with-the-crowd scoring was tested and retired: it systematically buries the
  sharpest raters and, on a biased crowd, rewards the bias.)
- One global number is not enough. A rater can be diligent in general and reliably wrong inside one
  contested divide, so disposition is assessed **per contested region**; only general diligence is
  global.
- Aggregation weights ratings by reputation through a fixed-point loop — except on **Ought nodes**,
  which are aggregated democratically, one person one vote. Reputation earned on facts buys no
  extra say over values.

Where: `v0/reasonable/assess.py` (True_R + weighted aggregation).
Why we trust it: FINDINGS-SYNTHESIS (the alignment/discrimination retirements; the per-region
result).

## 4. Anchors and bias-correction — LIVE, with a measured safety gate

A small set of **anchor questions** — items whose answers are independently well-established — lets
the system measure raters against reality instead of against each other. From a rater's anchor
performance the system learns their systematic bias (too harsh, too generous, compressed toward the
middle) and inverts it, weighting each corrected rater by how consistent they are.

The gate: on a cooperative, honest panel whose anchors all cluster near one value, this correction
has nothing to learn from and measurably *hurts* accuracy — so it **declines to fire** unless the
anchors span enough of the scale (a fixed spread threshold), falling back to the plain aggregate
byte-identically. Correction is for the hard case — a systematically biased or manipulated crowd —
and stays out of the way otherwise.

Where: `v0/reasonable/assessment.py` (calibration + the spread floor).
Why we trust it: FINDINGS-SYNTHESIS (dose-response robustness to a 60% coordinated bloc; the
cooperative-panel regression that motivated the gate).

## 5. Contested detection — LIVE, structural by design

"Where is this map genuinely contested?" is answered from **structure**, not from rating spread:

- A claim is contested when it has a live rival in an antithesis set whose support is comparable —
  a *structural* fact about the map.
- Independently, a spectral analysis of the rater-agreement matrix detects **belief camps** —
  factions who systematically rate the same items in opposite directions — with no oracle needed.
- Raw rating disagreement alone is deliberately *not* trusted as the trigger: we measured it to be
  unreliable for everyone, experts included, unless the disagreement is camp-driven (on genuinely
  split questions, most rating variance sits between camps; on ordinary panels it is mostly noise).

Where: `v0/reasonable/contested.py` (the shared verdict), `assessment.py` (`detect_camps`),
`lifecycle.py` (`structurally_contested`).
Why we trust it: FINDINGS-SYNTHESIS (the dispersion-reliability correction — one of the places we
retracted our own earlier claim).

## 6. The manufactured-certainty detector — BUILT, not yet wired in

The hardest attack we found is not flipping a verdict but **entrenching** one: a coordinated bloc
pushing the already-leading answer can't change the winner, so instead it collapses a genuinely
open question into false near-settlement, burying the legitimate minority. Standard accuracy
metrics are blind to it; only monitoring the verdict's *certainty* against what the evidence
warrants reveals it. A working detector exists and catches every committed attack variant offline
while staying quiet on honest baselines — but it is not yet integrated into the default assessment
pipeline. This is the top item on the engineering roadmap, and we state it as not-yet-done rather
than imply otherwise.

Where: detector + tests under `v0/covid-adversarial/`; roadmap in `v0/ROADMAP-NEXT-VERSION.md`.

## 7. Lifecycle states — LIVE, thresholds from measured reliability

Every rated item carries a state a reader can trust at a glance:

- **sealed / provisional** — too few ratings yet to lean on (below the coverage bar).
- **settled** — converged, uncontested, and covered: the panel agrees, whether the agreement is
  "this is strong" or "this is weak."
- **contested** — a live, structurally real disagreement (§5).

The coverage bar (`confirm`) is not a round number we liked: it was set from measured
**split-half reliability** — independent halves of the rater panel reproduce each other's per-node
scores at r ≥ 0.87 with 8 raters (0.96–0.98 at full panel size), so 8 is the bar on the
presentation graphs. Frozen, fully-rated presentation graphs also set a `static` flag so that
"settled" reflects convergence rather than an artifact of build order.

Where: `v0/reasonable/lifecycle.py`; the reliability analysis in `v0/v2-reliability/`.

## 8. Ghosts — LIVE

Refuted or superseded material is **demoted, never deleted**: greyed, sunk, retrievable, and
reversible, with the reason on the public record. Two protections matter: demotion on *truth*
grounds requires a claim to be confidently rejected on its own ratings (settled-low, not merely
unpopular), and **losing an antithesis contest is never grounds for ghosting** — a less-supported
rival is less supported, not wrong. That is the Semmelweis protection: the map must be a place
where a currently-minority truth can survive and keep its argument on the board.

Where: `v0/reasonable/contested.py` (ghost eligibility), the `supersede`/`--restore` verbs.

## 9. Type polls and the is/ought firewall — LIVE

A node's *kind* (claim / evidence / ought) is itself community-governed. Anyone can flag a node's
type; a dormant poll opens, and resolves by reputation-weighted vote at a quorum. Hume's rule is
enforced at the write boundary — an ought may not be used to ground a non-ought — so a whole class
of smuggled value-premises is rejected before entering the graph. And a poll that reaches quorum
but stays *split* is surfaced as a likely **is/ought conflation** ("eggs are bad" = a risk claim
plus a value claim), with guidance to decompose it into its Hume-safe parts. A positive "No, this
is not an ought" is kept as first-class data: considered-and-rejected is different from
never-examined.

Where: `v0/reasonable/typepoll.py`, `decompose.py`; the write-boundary check in `validate.py`.

## 10. Chain strength and comparison — LIVE

Support compounds along paths: a conclusion resting on a long chain of moderately-supported steps
is weaker than one resting on short strong ones, and the engine computes this explicitly. The
`compare` operation walks two rival claims back to their last shared premises and reports which is
better grounded from common ground, and by how much — turning "which side is stronger?" from
rhetoric into an inspectable calculation. (Layout and decluttering use a length-normalized version
of path strength so that deep, well-layered reasoning is rewarded rather than punished for having
more steps.)

Where: `v0/reasonable/chain.py`; the `chain` and `compare` verbs.

## 11. The substrate everything rests on — LIVE

Every graph is an **append-only event log** plus a snapshot derived from it by a deterministic
replay: same log + same configuration → byte-for-byte identical snapshot, verified by the test
suite. Nothing is ever rewritten; every mechanism above is a pure function of the public history.
This is what makes the assessment layer **late-binding**: anyone can re-run assessment over the
same shared structure under their own configuration — different anchors, different panel, different
thresholds — without touching the record. Trust the log, audit everything else.

Where: `v0/reasonable/store.py`, `fold.py`; contract in `v0/BUILD-SPEC.md`.

---

## What is deliberately *not* here

Retired mechanisms (agreement-based reputation, raw-consensus discrimination scoring, superlinear
weighting, Bayesian Truth Serum) and the experiments that killed or validated everything above.
That history is a first-class part of the project — several of this document's design choices exist
*because* an earlier version failed honestly in public — but it lives where history belongs:
[FINDINGS-SYNTHESIS.md](v0/FINDINGS-SYNTHESIS.md), with a reproduce index so every claim can be
re-run from committed data.
