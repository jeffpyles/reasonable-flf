# The research arc — how we arrived at the current assessment design

*The story in brief: what we tried, what failed, what survived, and where we retracted our own
claims. This is the executive version of [FINDINGS-SYNTHESIS.md](v0/FINDINGS-SYNTHESIS.md), which
holds the full account with a reproduce index — every result below re-runs from committed data.
The systems as they stand today are in [MECHANISMS.md](MECHANISMS.md). All results are from
simulated (AI) rater panels except where noted; that limit is discussed at the end.*

## The question

In a collaborative map, how do you find the raters who actually track the truth and give their
judgment its due weight — so that verdicts approach truth from a standing start, scale, survive
genuinely contested questions, and resist coordinated manipulation?

## Act 1 — the obvious ideas fail, and fail the same way

The natural first designs all score raters using only the community's own ratings. Every one of
them failed, and the post-mortems agree on the cause:

- **Rewarding agreement with the average** buries exactly the sharpest raters — a tyranny of the
  median. Statistically fancier variants that infer a "latent truth" from the same ratings inherit
  the same flaw.
- **Rewarding consensus-order tracking** (do you rank items the way the crowd does?) works on an
  honest crowd and *inverts* on a biased one — it hands its highest scores to whoever shares the
  bias.
- **Bayesian Truth Serum**, elegant in theory, depended on an asymmetry our real agent panels
  didn't exhibit; parked.

The common cause became the project's central lesson: **a rule that looks only inward can only
measure agreement with the crowd, so it inherits whatever the crowd gets systematically wrong.**

Two positive discoveries came out of the same period. **Blind rating** — hiding the consensus,
comments, and author reputation while rating — was the single biggest accuracy lever we measured
(truth-tracking 0.52 with cues visible → 0.89 blind), and it costs nothing. And fine-grained rater
quality is expensive to measure while a rater's broad *disposition* is cheap (roughly 8 ratings vs
~77) — so the system assesses dispositions quickly and lets fine rank accumulate slowly.

## Act 2 — a little external reality, and what attacks it

The escape from the inward-looking trap is a small set of **anchors**: questions with independently
well-established answers, used to measure raters against reality. From anchor performance the
system learns each rater's systematic bias and inverts it (calibration), weighting corrected raters
by consistency. Stress-tested with dose-response attack sweeps — a coordinated dishonest bloc grown
from 0% to 60% of the panel — this held: **calibration defeats naive, jittered, and sybil attacks
even from a 60% majority**, because the attackers lie on the anchors too, and the anchors give them
away.

Then we attacked it properly, and two results mark the honest edge of the defense:

- **The sleeper.** An attacker who answers the anchors honestly and lies only where no anchor
  exists looks like a model rater. Correction reaches exactly as far as anchor coverage — and
  giving high-reputation raters superlinear extra weight makes this attack *stronger*, which
  retired that idea too. The mitigation is detection: spectral belief-camp analysis flagged every
  attack variant we ran, including sleepers, even where correction failed.
- **The manufactured-certainty attack.** Replayed on a second, genuinely contested domain with
  *real* (not scripted) attacker agents, the hardest case emerged: a bloc pushing the
  already-leading answer can't flip the verdict, so instead it collapses a live question into false
  near-settlement, burying the legitimate minority. Standard accuracy metrics are blind to it — a
  lesson in itself: *the metric is part of the attack surface.* A detector that monitors verdict
  certainty against what the evidence warrants catches it offline; wiring it into the default
  pipeline is the top roadmap item. A small, unsettling observation from the same runs: the
  attack our real agents executed most willingly was the one that *entrenches* a mainstream
  consensus rather than the one that flips it.

Scale questions got their own answers: one global reputation number is structurally insufficient
(a diligent-but-biased rater earns global trust on easy items and spends it on the contested ones),
so disposition is assessed per contested region; anchors are worthless without *routing* raters to
them; and the scarce checking budget scales with the number of contested divides — not with users
or graph size.

## Act 3 — the retractions

Three places the evidence overturned our own published claims, kept in the record deliberately:

1. **Rating spread is not a reliable "contested" signal — for anyone.** We had inferred
   contestedness from rating variance. Denser reference panels showed even independent expert
   panels reproduce their own variance map poorly; spread is only meaningful when driven by real
   belief camps. The trigger was replaced with structural rivalry plus camp detection.
2. **Calibration has a floor, and it hurt an honest panel.** Wired into a cooperative panel whose
   anchors clustered near one value, calibration made accuracy *worse* — with nothing to learn
   from, the correction just dragged estimates toward the anchor mean. It now declines to fire
   below a measured anchor-spread threshold.
3. **The "cheap raters can't reproduce the crux map" claim was partly our own measurement
   artifact.** With a denser reference, cheap raters partially track it — and *nobody* tracks it
   cleanly (see retraction 1). What cheap panels durably lose is warranted *confidence* on hard
   questions, which argues for a hybrid: cheap swarms for scale, expensive scrutiny reserved for
   the contested regions.

A fourth self-check closed the loop: an independent adversarial audit of the whole research branch
confirmed the negative results reproduce exactly while flagging some headline positives as partly
true-by-construction — kept in the repository rather than buried.

## Where it stands

The surviving stack — blind rating, anchor calibration with its safety gate, per-region
reputation, structural contested detection with belief camps, and the certainty detector (built,
not yet wired in) — is live in the engine and described in [MECHANISMS.md](MECHANISMS.md). The
maturity threshold on the presentation graphs comes from measured split-half reliability (panels
reproduce each other's per-node scores at r ≥ 0.87 with 8 raters; 0.96–0.98 at full size).

The honest limits: nearly every result above is model-on-model — simulated rater panels, with one
thin external check against the documented real-world record — so a human-rated slice is the
single most valuable missing experiment. The full pipeline has not yet run live end-to-end over
many rounds. And every attacker so far was static; an adaptive red team would set a real ceiling.
Our overall confidence that the assembled machinery is robust for real deployment: **~60–65%** —
high on the tested mechanisms, lower on transfer to the messy real thing. The next experiments to
run are exactly the ones that would move that number.
