# Roadmap — what comes next

*The work plan as of 2026-07-22, in two horizons: **near-term** work with concrete next steps, and
the **long-term** direction it aims at, held more humbly. The finding-by-finding engineering detail
behind the first near-term item is the dated tier list
[`v0/ROADMAP-NEXT-VERSION.md`](v0/ROADMAP-NEXT-VERSION.md); the systems as they stand are
[`MECHANISMS.md`](MECHANISMS.md); the destination is [`VISION.md`](VISION.md).*

---

# Near-term

The work with clear next steps — hardening what exists, and taking it live for the first real users.

## 1. Close the measured defense gaps

The red-team runs told us what to build next; most of it is detection the research has already
prototyped.

- **Wire in the manufactured-certainty guardrail.** The hardest attack we found — collapsing a
  genuinely open question into false near-settlement — has a working detector, validated offline
  against every committed attack sweep while staying quiet on honest baselines. It is not yet in
  the default assessment pipeline.
- **Second-stage coordination detection.** Camp analysis finds the suspicious side with full
  recall but sweeps honest same-side raters in with the suspicious bloc (~0.5 precision). The
  isolating signal — coordinated extremity and tightness, measured at a 3.3× gap between attackers
  and honest raters — exists in analysis code and needs to become a calibrated two-stage filter,
  so belief is never mistaken for a coordinated attack bloc.
- **Denser, rotating, hard-to-predict anchors.** The one attacker that beats calibration is the
  sleeper who is honest exactly where the anchors are. Its edge is knowing the anchor set; secret,
  rotating anchors over the contested frontier degrade it back toward the attacks we already
  defeat.
- **A properly adversarial red team.** Every attacker so far was static and one-shot — a floor on
  attack strength, not a ceiling. An adaptive attacker that observes reputation and adjusts, and a
  sleeper that jitters its lies to resist clustering, are the next stress tests, along with
  replicating the small-n findings (like the refusal asymmetry) across more questions and models
  before leaning on them.

## 2. Strengthen the arguments, and expand the graph's usefulness

The claims in today's graphs are AI-drafted scaffolding built to exercise the machinery; making
them genuinely compelling is its own workstream — both at the level of individual claims and their
phrasings, and in the argumentative structure of the graph. The goal is a build pipeline that
produces strong, correctly-placed arguments directly: the right model tier and combination of
agents, with prompts and harnesses, to elicit output that a stronger model rarely has to make a
corrective pass over — while keeping the system no more expensive to run than it needs to be.

- **Maximize the clarity and readability of the graph**, improving on the ordering of nodes into
  coherent chains of argument and their rendering into visually legible structures rather than
  dense rat nests.
- **Refinements to the grammar**: what types of nodes & edges & other affordances the site allows
  in order to clearly express arguments. Such as conditional, forward model-building — "if we did
  X, the world would be Y" — which is most of what "what should we do?" questions actually consist
  of. The grammar's firewall between is and ought rightly forbids deriving a fact from a value,
  but it also leaves nowhere to build out the *descriptive* consequences of a proposed action. The
  proposed fix is a scenario construct type: designate an action-state as assumed, build and
  assess its consequence-tree conditionally, and let it export explicit conditionals ("if X, then
  Y") that can then legally ground an ought — the value firewall stays fully intact. Rival
  scenarios for rival policies let the map show exactly where two proposed futures diverge, which
  is where the real policy crux usually hides.
- **Probability and prediction nodes.** A node type that asks "how likely is X?", answered by each
  rater with their own number, so the map carries a collective forecast — a reputation-weighted
  headline with the unweighted average beside it, plus the honest range and any distinct camps.
  This connects the map to forecasting and prediction markets, whose prices and scoring can enter
  as inputs or as calibration anchors for exactly these nodes — and it answers a shortcoming of
  prediction markets as a tool of public knowledge, that they make public people's *likelihood* of
  X happening but not their *reasoning*.
- A metric for the cumulative assessed strength of a given chain through the graph from a given
  ground to a given conclusion, which lets you see how strong a given argument is — and compare it
  to the strength of an alternative argument.
- **Personal belief structures.** A user highlights their own beliefs — which nodes they agree
  with, and their own probabilities — on the shared graph, and is notified when the ground under
  one of their beliefs materially shifts. Two such personal maps can be compared to find the exact
  node where two people's reasoning first diverges — the last place they agreed, which is the only
  useful place for them to argue. Pulls in the chain-strength metric from above to compare the
  quality of the relative belief structures, nudging people away from weaker arguments toward
  stronger ones.
- **Answers on demand ("ask the graph").** Most readers will never walk the graph in depth, just
  as most people never read academic papers. The likely main landing page for most readers is a
  plain, Google-style question box: an AI answers in a few readable paragraphs, drawing on the
  assessed graph — chain strengths, path comparisons, live contested-points — and linking each
  load-bearing point to the place on the map where it is worked out in full. The deep work of AIs
  and a small fraction of humans underwrites the answer; the answer is how everyone else touches
  it. Search-engine simplicity, argument-map depth and consensus.

## 3. Extend the system outward

- **An end-to-end longitudinal run.** Build → structure-check → rate → contest → ghost → re-rate,
  over many rounds, with real turnover of contributors and claims. The individual mechanisms are
  each validated; the full flywheel has never been exercised live as one loop, and loops fail in
  ways their parts don't.
- **A centaur system.** Human contributors added into the build and rating loops alongside the
  agents. In the current state of AI we expect the mixed system to be stronger than AI alone —
  humans supplying judgment, taste, and ground truth; agents supplying assembly, maintenance, and
  tireless first-pass coverage.
- **The write side of the viewer.** The viewer today is read-only; the engine's full write and
  rating surface exists only as a CLI. Collecting live ratings — and then live claims — through
  the viewer opens it up to human contributors.
- **Open the graph to contributors in stages, on select scoped questions.** Not a public launch,
  but concentric rings. First, on the order of tens of hand-picked contributors working one
  project- or civilization-relevant question: eg, what forms of knowledge should a system like
  this prohibit as too dangerous to be discussed publicly? Is AI existential risk real? How should
  governments regulate AI? Then fold what that cohort teaches us back into the mechanisms, open to
  a larger group, and repeat. Each ring is both a real deployment and the next experiment — and
  the questions are chosen so even the small early runs produce maps worth having.
- **The panel-composition matrix.** Run parallel instances of the same question varying who builds
  and who rates: human-only, AI-only, and mixed, on each axis independently. Because the format,
  anchors, and assessment configuration are shared, the instances are comparable cell by cell —
  which turns the platform into a measurement instrument three ways at once:
  - a merged-graph test — whether the union of human and AI contributions is stronger than either
    alone, as we expect;
  - a running benchmark of what different kinds of minds contribute to knowledge-building,
    question by question — including how long the centaur advantage over AI-only actually holds;
  - a standing open-vs-curated comparison — where an open crowd's assessment diverges from a
    curated panel's on identical structure gives us guidance on where our mechanisms' open
    assessment cannot yet be trusted, or on where our panel's can't.

---

# Long-term

The intended direction, to be worked out as we go. Everything below is conditional on the
assessment layer demonstrating a level of reliability and trust it has not yet earned — the
near-term work above is what would earn it.

## 4. Test against checkable knowledge

The unanswerable domains are a major destination, but domains where reality can referee are
equally important, and also an arena that offers rapid feedback for improvement.

- **Hard math as a case shape.** Can the format faithfully structure the reasoning of a complex
  math problem — statements, lemmas, proof obligations, known partial results — and can panels
  assess it coherently? Formal verification gives these graphs something no other domain has:
  machine-checkable ground truth, i.e. perfect, free anchors.
- **Uplift on open problems.** The stronger version of the test: does the shared structure give
  measurable uplift to models collaborating on difficult open math/CS/physics questions — compared
  with the same models working without the map? This doubles as the cleanest version of the
  benchmark in Section 3, on questions where the score is objective.

**Addendum: We ran a small test on the above question since posting the initial submission, and
after a disproof of the Jacobian Conjecture was announced, with mixed results: A five-round
Sonnet-agent run on the Conjecture (with a CAS verifier and blind panels) produced a
machine-anchored research map — and a pre-registered control found that, given the shared
verifier, a plain prose notebook matched the graph on epistemic discipline, with the graph winning
only navigability. The verifier carried most of the value at that scale; adversarial referee
panels caught overclaims in the graph that both the verifier and blind ratings passed;
improvements to the graph's affordances for math in particular were elicited.
[See the full report](math-experiment.html)**

## 5. Toward the one full graph

The submission's four separate graphs are a scoping artifact of building the prototype on short
time for the submission; the real object is a single connected public graph of ~all knowledge,
current and future [See the Vision](vision.html).

- **Connect the case graphs** at their shared underpinnings — statistics, epistemology, risk — as
  the seed of the single public graph the separate prototypes stand in for.
- **Add in the scoped rollout graphs**, with their guidance on whether there are areas of
  knowledge that the graph shouldn't touch. Aim some of the early buildout of the graph at the
  graph itself: how it should grow and operate, what makes it more effective and useful, etc.
- **Begin to ingest the whole of the existing human conversation.** The points in every major
  argument already exist, scattered and inconsistently evaluated; agent-assisted ingestion of
  essays, papers, and threads into structure is how coverage compounds without waiting for people
  to adopt a new format.

## 6. Civilizational roles the map could grow into

If the graph reaches full scale, and the usability and assessment layers reach the clarity,
completeness, and reliability these roles demand, the same machinery starts to compete with some
of the load-bearing institutions of public reason.

- **A venue for publishing studies, and for peer review.** A paper is an argument with evidence; a
  review is an assessment of it. Both already fit the grammar. The long aim is a place where a
  result, the case for and against it, its reviews, and the live state of the debate around it sit
  in one assessed, compounding structure — rather than scattered across journals, PDFs, and siloed
  review.
- **Assessment-based advertising.** The graph can be used to examine companies, their products and
  goals and behaviors, and come to a collective assessment of how much those are each approved of.
  If public assessment of what companies produce and how they behave becomes reliable, then
  organizations can be ranked by their approval, and the fact of their certification as high
  quality, good faith actors becomes a highly valuable signal — and the site can both license that
  certification for display across the rest of the world, and allow top-ranked orgs to advertise
  on the site itself (as guided by the users of the graph itself deciding what forms of
  advertisement are mutually rewarding and aligned).

  Organizational assessment also drives positive change, in both directions: orgs can see in clear
  public detail what the public doesn't like about them, and the case for why what the org is
  doing is good, actually, can be made in full. Where there are things that are widely agreed to
  be genuinely bad, the organization has clear incentive to improve them — and if they don't,
  that's feedback that gets rolled in to their ongoing assessment, and also guidance to
  competitors about how to outcompete them.
- **A democratic check on governance.** The statements above about organizational assessment's
  effects also apply to politicians and governmental organizations. Make the genuinely sound
  policy options on a contested question visible and comparable, and make it legible when a
  political move is rhetoric for gain rather than a reasonable or sensible position, and you drive
  positive change and limit the scope for bad actors. Detailed, shared public knowledge of what we
  collectively value and of what approaches have reasonable claims to deliver those values, with
  the arguments surrounding them had out in full, in public, brings serious accountability to
  anyone not acting accordingly.
