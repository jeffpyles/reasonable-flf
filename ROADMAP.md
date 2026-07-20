# Roadmap — what comes next

*The near-term work plan as of 2026-07-19. The finding-by-finding engineering detail behind Section 1
is the dated tier list [`v0/ROADMAP-NEXT-VERSION.md`](v0/ROADMAP-NEXT-VERSION.md); the systems as
they stand are [`MECHANISMS.md`](MECHANISMS.md); the destination is [`VISION.md`](VISION.md).*

## 1. Close the measured defense gaps

The red-team runs told us exactly what to build next; most of it is detection the research has
already prototyped. (Detail and cost estimates per item: `v0/ROADMAP-NEXT-VERSION.md`.)

- **Wire in the manufactured-certainty guardrail.** The hardest attack we found — collapsing a
  genuinely open question into false near-settlement — has a working detector, validated offline
  against every committed attack sweep while staying quiet on honest baselines. It is not yet in
  the default assessment pipeline. This is the top engineering item, and until it lands we state it
  as not-done rather than imply otherwise.
- **Second-stage coordination detection.** Camp analysis finds the suspicious *side* with full
  recall but sweeps honest same-side raters in with the bloc (~0.5 precision). The isolating
  signal — coordinated extremity and tightness, measured at a 3.3× gap between attackers and honest
  raters — exists in analysis code and needs to become a calibrated two-stage filter, so belief is
  never mistaken for a bloc.
- **Denser, rotating, hard-to-predict anchors.** The one attacker that beats calibration is the
  sleeper who is honest exactly where the anchors are. Its entire edge is knowing the anchor set;
  secret, rotating anchors over the contested frontier — including the *leading* side's cruxes —
  degrade it back toward the attacks we already defeat.
- **A properly adversarial red team.** Every attacker so far was static and one-shot — a floor on
  attack strength, not a ceiling. An adaptive attacker that observes reputation and adjusts, and a
  sleeper that jitters its lies to resist clustering, are the honest next stress tests, along with
  replicating the small-n findings (like the refusal asymmetry) across more questions and models
  before leaning on them.

## 2. Strengthen the arguments themselves

The claims in today's graphs are AI-drafted scaffolding built to exercise the machinery; making them
genuinely compelling is its own workstream — both at the level of individual claims and their
phrasings, and in the argumentative structure of the graph. The goal is a build pipeline that
produces strong, correctly-placed arguments *directly*: the right model tier and combination of
agents, with prompts and harnesses good enough that a stronger model rarely has to make a corrective
pass — while keeping the system no more expensive to run than it needs to be. Argument quality and
build economics are the two ends of that dial, and finding where they meet is the work.

## 3. Run the missing experiments

The research validated the parts; three experiments would validate the whole.

- **A human-rated slice.** Nearly every result in the research chain is model-on-model — simulated
  rater panels, with one thin external check. Re-rating a slice of an existing graph with human
  panels is the single most valuable missing experiment: it either transfers the headline results
  to people or tells us where they bend.
- **An end-to-end longitudinal run.** Build → structure-check → rate → contest → ghost → re-rate,
  over many rounds, with real turnover of contributors and claims. The individual mechanisms are
  each validated; the full flywheel has never been exercised live as one loop, and loops fail in
  ways their parts don't.
- **The third shape, fully stressed.** The black-holes graph (strong consensus with a vocal edge)
  is built and assessed, but the oracle/honest/adversarial passes that eggs and COVID went through
  have not been ported to it. Completing it closes the three-shape generalizability claim with
  stress-testing, not just construction.

## 4. Put humans in the loop

Everything so far was AI-built and AI-rated by necessity of the prototype window. The next stage
makes the system live for people.

- **The write side of the viewer.** The viewer today is read-only; the engine's full write and
  rating surface exists only as a CLI. Collecting live ratings — and then live claims — through the
  viewer is what turns the artifact from a demonstration into an instrument.
- **A centaur system.** Human contributors added into the build and rating loops alongside the
  agents. In the current state of AI we expect the mixed system to be stronger than AI alone —
  humans supplying judgment, taste, and ground truth; agents supplying assembly, maintenance, and
  tireless first-pass coverage.
- **Open the graph in stages.** Not a public launch, but concentric rings. First, on the order of
  a hundred hand-picked contributors working one important question — project- or
  civilization-relevant by design: *what forms of knowledge should a system like this prohibit as
  too dangerous to be improved on publicly? Is AI existential risk real? How should governments
  regulate AI?* Then fold what that cohort teaches us back into the mechanisms, open to a larger
  group, and repeat. Each ring is both a real deployment and the next experiment — and the
  questions are chosen so even the small early runs produce maps worth having.
- **The panel-composition matrix.** Run parallel instances of the *same* question varying who
  builds and who rates: human-only, AI-only, and mixed, on each axis independently. Because the
  format, anchors, and assessment configuration are shared, the instances are comparable cell by
  cell — which turns the platform into a measurement instrument three ways at once:
  - a running **benchmark of what different kinds of minds contribute** to knowledge-building,
    question by question — including how long the centaur advantage over AI-only actually holds;
  - a **merged-graph test** — whether the union of human and AI contributions is stronger than
    either alone, as we expect;
  - a standing **open-vs-curated comparison** — where an open crowd's assessment diverges from a
    curated panel's on identical structure is precisely where open assessment cannot yet be
    trusted, mapped rather than argued about.

## 5. Test against checkable knowledge

The unanswerable domains are the destination, but domains where reality can referee are where trust
is earned and measured.

- **Hard math as a case shape.** Can the format faithfully structure the reasoning of a complex
  math problem — statements, lemmas, proof obligations, known partial results — and can panels
  assess it coherently? Formal verification gives these graphs something no other domain has:
  machine-checkable ground truth, i.e. perfect, free anchors.
- **Uplift on open problems.** The stronger version of the test: does the shared structure give
  measurable uplift to frontier models collaborating on difficult open math/CS/physics questions —
  compared with the same models working without the map? This doubles as the cleanest version of
  the benchmark in Section 4, on questions where the score is objective.

## 6. Toward the one graph

Further out, and stated as direction rather than plan (the full case is
[`VISION.md`](VISION.md) §6):

- **Connect the case graphs** at their shared underpinnings — statistics, epistemology, risk — as
  the seed of the single public graph the separate prototypes stand in for.
- **Ingest the existing conversation.** The points in every major argument already exist, scattered
  and unevaluated; agent-assisted ingestion of essays, papers, and threads into structure is how
  coverage compounds without waiting for people to argue in a new format.
- **Probability nodes and personal maps.** Collective forecasts with honest spread on the shared
  graph; personal belief overlays that locate the exact node where two people's reasoning first
  diverges.

---

