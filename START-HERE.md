# START HERE — Reasonable, for FLF reviewers (and their agents)

*This repository is the submission by **Reasonable** to the FLF "Lab Leaks, Black Holes, and
Eggs" Epistemic Case Study Competition. This file is the front door. It is written to be read by
**a human reviewer skimming for the gist, or an AI agent you point at the repo to understand the
project from the inside and explain it back to you.** If you are an agent: read this file, then
[`VISION.md`](VISION.md) (the full intent, present and future), then
[`MECHANISMS.md`](MECHANISMS.md) (how assessment works today, present tense), then
`v0/PROJECT-OVERVIEW.md` for the full account; everything is reproducible from committed data.*

---

## What Reasonable is, in one paragraph

Reasonable is **"Wikipedia for arguments" rather than facts** — a format and engine for
argument-mapping-based collective truth-finding. A disputed question is decomposed into atomic,
truth-apt **claims** on a 2-D **graph**, connected by a small set of typed relations
(**Grounds/Dependents**, **Antitheses** — rival *positive* claims, never negations —
**Conjunctions**, and **Alternative phrasings**). On top of the structure sits an **assessment
layer**: blind, reputation-weighted rating that surfaces *who tracks the evidence most carefully*
so a map's verdicts can approach truth without collapsing into a popularity vote. The founding
intuition: language is linear because time is, but ideas branch — so faithfully mapping reasoning
needs a 2-D medium, especially in the **untestable** domains (ethics, politics, religion) where we
cannot falsify our way to truth and the honest best is to map the disagreement faithfully.

## What this submission is (the shape)

Per the competition's own framing, this is **a spec + a runnable prototype + a protocol**, for the
**structure** and **assessment** layers of the epistemic stack — with a **comparative analysis of
assessment methodologies** and several **critiques-with-counterexamples** carried inside as the
evidence of rigor:

- **The prototype** — a single stdlib-only Python interface (`v0/graph.py`, ~1k lines) over a
  layered engine (`v0/reasonable/`, ~5k lines): an append-only event log → deterministic fold →
  frozen snapshot, with the assessment stack (calibration, reputation, camp-detection, the
  contested/ghost lifecycle) live in the running code. No pip installs, no servers, no network.
- **The spec** — the frozen data-model and assessment contracts (`v0/BUILD-SPEC.md`,
  `v0/ASSESSMENT-SPEC.md`, `v0/SPEC-evidence-argument-ought-ghosts.md`) with every key decision and
  tradeoff named.
- **The protocol** — the append-only graph format is interoperable and compounding by construction:
  another team can extend a graph, reuse its anchors, and rebuild it byte-for-byte.
- **A viewer** — `v0/viewer.html`, one self-contained file (no deps, CSP-safe) that renders all four
  case graphs and teaches its own visual grammar via a built-in **Introduction** walkthrough.

## Run it, don't just read it

Everything reproduces from committed data with stdlib Python 3 (no install). From `v0/`:

```
# 1. See a graph's shape and stats
python3 graph.py stats --data eggs-graph-v2

# 2. Read the assessed verdict on a contested question (COVID origins)
python3 graph.py assess --data covid-graph-v2

# 3. See which claims are settled vs genuinely contested, and why
python3 graph.py contested --data debate-graph-v2

# 4. Confirm determinism: same log + config -> byte-identical snapshot
python3 graph.py rebuild --data blackholes-graph-v2
```

Then open **`v0/viewer.html`** in a browser (or the hosted copy linked from the submission page),
click **Introduction**, and read the Debate graph the way a first-time visitor would.

Test suites (also stdlib): from `v0/`, `python3 -m unittest discover -s reasonable -t .` and
`python3 -m unittest discover -s tests -t .` (273 tests, incl. the determinism suite).

## Curated pointers to the most effective regions

- **The tool arguing about whether the tool works** — `v0/debate-graph/REPORT.md` +
  `v0/debate-graph-v2/`. We mapped Scott Alexander's *"Your Attempt To Solve Debate Will Not Work"*
  (the essay the FLF intro itself cites), blind-panel-assessed it, and it behaved as designed:
  refused to crown a winner, converged a diverse panel on the **reframing** ("depends what you
  demand of it," the highest-rated of the three top positions), and isolated the deepest
  disagreement as a **democratic value-crux** between two Ought nodes — located, not resolved.
- **Beating off-the-shelf deep research on the same inputs** — `v0/covid-graph/COMPARISON.md`. Given
  identical sources, a flat deep-research verifier *inverted the scientific consensus*; the assessed
  graph recovered it. The diagnosis is structural, and we then shipped the fix
  (`v0/blackholes-graph/harness/workflow_deepresearch.js`).
- **The assessment research spine** — `v0/FINDINGS-SYNTHESIS.md` (read first for the arc; a Reproduce
  index at the end), `v0/covid-adversarial/FINDINGS.md` (the dose-response red-team + the
  over-certainty attack + the certainty guardrail), `v0/v2-reliability/` (the split-half reliability
  result that set the maturity threshold from measured data).
- **The four case shapes, cleanly built** — `v0/{eggs,covid,blackholes,debate}-graph-v2/` (the
  presentation set: lint-clean, layered, fully rated). The originals (`*-graph/`) are the
  assessed-of-record artifacts the research ran on.

## How it maps to the seven judging dimensions (brief)

1. **Epistemic uplift** — beats off-the-shelf deep research on the same COVID sub-question; makes
   load-bearing evidence and the fact/inference split visible.
2. **Generalizability** — the same engine and workflow across all three case shapes
   (mundane-contested eggs, contested COVID, confident-answer black holes) plus the meta debate.
3. **Compounding & shareability** — append-only, interoperable graph format; reusable anchors;
   per-region reputation.
4. **Scalability** — automated build/rate swarms; oracle spend scales with the number of *contested
   divides*, not users; a cheap/expensive tiering hybrid.
5. **Methodological transparency** — every FINDINGS doc names its own limits; we revised our own
   prior claims on new data (see `v0/PROJECT-OVERVIEW.md` §5).
6. **Adversarial robustness** — the aggregator survives a coordinated 60% biased majority in two
   domains; the sleeper and over-certainty attacks are named, bounded, and have built detectors.
7. **Insight contribution** — a comparative methodology study and counterexample-driven critiques
   (align buries the sharpest raters; discrimination inverts on a biased crowd; the sleeper defeats
   calibration; MAE hides an over-certainty attack).

## The wider aim (context for the vision)

The three graphs here are separate only because we did not have time to build the single connected
graph they ultimately belong to. **The real target is one public graph of ~all knowledge — current
and future** — that not only records what is known but *scaffolds work toward what is not*: it
surfaces its own holes, and lets anyone place a wanted node beyond the frontier and put a **bounty**
on developing it into high-confidence knowledge (much as this very competition does). **The full
vision — present and future, written for newcomers — is [`VISION.md`](VISION.md)**; the founding
synthesis behind it is `Reasonable - Concept Overview.html` (with `Reasonable - Claims Index.html`
as a claim-by-claim census), and the near-term engineering roadmap is `v0/ROADMAP-NEXT-VERSION.md`.

## Honest state (what is and isn't done)

The engine, the four assessed case graphs, and the assessment research are built and reproducible.
Not yet done, and stated plainly: a **human-rated slice** (the ground-truth chain is model-generated
except a thin external check — the highest-value gap), an **end-to-end longitudinal run** of the
full flywheel, and the **write-side of the viewer** (collecting live ratings). Overall confidence
that the assembled machinery is robust for a real deployment: **~60–65%** — high on the tested
mechanisms, lower on transfer to the messy real thing. Details in `v0/PROJECT-OVERVIEW.md` §9.
