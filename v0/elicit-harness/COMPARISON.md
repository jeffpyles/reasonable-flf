# Elicitation experiment — can a harness get a Sonnet build to the hand-built structure?

*2026-07-18. The elicitation analysis (`debate-graph-v2/README-STRUCTURE-PASS.md`) argued that the
structural pathologies in the v1 debate graph — a 13-ground hub, bundled nodes, loose antithesis
sets — were **harness-shaped, not model-shaped**: nothing in the hand rebuild required judgment a
Sonnet build agent lacks; what changed was the procedure. This experiment tests that claim by making
it runnable.*

## Setup

Three builds of the **same** debate question, scored on the **same** structural probes:

| build | how it was made |
|---|---|
| **v1 naive** | `debate-graph` — a Sonnet flow **without** the harness (the original) |
| **harnessed** | `elicit-harness/out-debate` — a Sonnet flow **with** the skeleton-first harness |
| **v2 hand** | `debate-graph-v2` — the structure built by hand (the target) |

The harness (`elicit_build.js`) builds from **unstructured source prose** (`SOURCE-BRIEF-debate.md`,
named entities left in) in four phases: **plan** the skeleton (theses + mirrored limbs) before any
leaf → **scaffold** roots+limbs → **populate** each limb in parallel under three authoring checks
(standalone, one-proposition, mandatory ≤8-word title) → wire **antitheses** under a both-true gate.

Metrics: deterministic (`compare.py`) + two uniform LLM probes (`elicit_probe.js`) run identically
over all three graphs — a per-node *two-assertion* probe (is the text bundled?) and a per-set
*both-true* probe (can the "rivals" both be true, i.e. not a real rivalry?).

## Results

| metric | v1 naive | harnessed | v2 hand |
|---|---:|---:|---:|
| nodes | 32 | 68 | 45 |
| **max in-degree** | **13** | **4** | 5 |
| **hubs (≥8 grounds)** | **1** | **0** | 0 |
| **titled** | **12%** | **100%** | 100% |
| question-shaped / orphans | 0 / 0 | 0 / 0 | 0 / 0 |
| **bundled-node rate** (probe) | **38%** | **29%** | **16%** |
| antithesis sets | 10 | 5 | 7 |
| **non-rivalry rate** (probe) | **80%** | **40%** | 43% |

*(The probe is a single Haiku judge and reads "bundled" strictly — it flags 16% even of the hand
build. Read the numbers **relatively**, not as absolutes; the judge is applied identically to all
three, so the ordering is the signal.)*

## What the harness fixed (skeleton-first is validated)

- **The hub is gone.** Max in-degree 13 → 4; zero hubs. The skeleton-first constraint — leaves may
  only attach to a limb, never to a root thesis — makes the star topology *structurally impossible*
  rather than something to lint-and-fix afterward. This is the single clearest win.
- **Titling is solved.** 12% → 100%, from the mandatory-title check alone.
- **Antithesis precision matches the hand build.** Non-rivalry rate 80% → 40%, essentially level
  with the hand build's 43%. The both-true gate does about as well as hand judgment at keeping
  challenge-answer pairs (which can both be true) *out* of antithesis sets — the exact discipline
  that took a manual pass to enforce in v1.
- **The mirrored architecture emerged on its own.** The planner independently produced the same
  form/object/viability/history limb structure, mirrored across the skeptic and builder roots, that
  the hand build arrived at — with no template describing it.

## What it did not fix (three named, cheap gaps — not a capability wall)

1. **Bundling concentrated in the *unchecked skeleton*.** The build's 29% bundled rate splits sharply
   by layer: **≈10% of the 52 leaves** are bundled, but **essentially every root and limb node is**
   (e.g. the "not viable" limb came out as *"formal mapping is inefficient **and** its user barely
   exists"*; a concessions limb crammed a no-track-record claim plus four separate concessions into
   one sentence). The reason is exact: the two-assertion and standalone checks run only in the
   **populate** phase, so the **planner's** skeleton nodes bypass them. **Fix:** run the same
   check on the plan/scaffold output — de-bundle each root/limb text before leaves attach. This
   alone should move the build from 29% toward the hand build's 16%.
2. **Antithesis recall gap.** The 5 sets the build made are (mostly) genuine rivals, but it made
   *fewer* than the hand build's 7 — it missed real rivalries, notably the viability pair (*"not
   viable in practice"* vs *"viable for a different audience"*). Cause: the planner only flagged 3 of
   4 mirrored limb pairs with a `mirror_of` key, and the antithesis agent was told to pair only the
   flagged ones. **Fix:** have the antithesis agent enumerate *all* cross-side limb pairs and
   within-limb leaf pairs itself, applying the both-true gate to each, rather than trusting the
   planner's mirror flags.
3. **Sprawl.** 68 nodes vs the hand build's 45 — the populate phase averaged ~4.7 leaves per limb
   with no cap and 11 limbs. **Fix:** cap leaves per limb (2-4) and let the planner merge thin limbs;
   the honest verdict node in eggs showed 2 limbs can carry 9 grounds cleanly.

A fourth, incidental friction the run surfaced: build agents repeatedly tried to create `evidence`
nodes and were rejected because the prose brief has **no source pack** (`--source` is required for
`evidence`). A production harness feeding real evidence needs the source pack wired in, or an
explicit "claims-only, no evidence kind" mode for briefs without sources.

## Verdict

The core claim of the elicitation analysis holds: **the v1→hand gap is mostly harness-shaped.** With
skeleton-first building, mandatory titles, and a both-true antithesis gate, a Sonnet flow clears the
two pathologies that most needed hand-fixing (the hub and untitled nodes) and matches the hand build
on antithesis precision — from unstructured prose, unaided. The residual gap to the hand build is
**three specific, cheap harness changes** (check the skeleton too; make antithesis recall the
agent's job; cap leaf sprawl), none of which require better models. The highest-leverage next fix is
#1 — extend the authoring checks from the leaves to the skeleton — because that is where 15 of the
20 bundled nodes live.

Reproduce: `python3 -m … ` → `Workflow elicit_build.js` (build) → `Workflow elicit_probe.js` (probe)
→ `python3 elicit-harness/compare.py` (deterministic). Raw probe verdicts in `probe-results.json`.

> **Read round 1's probe percentages with round 2's caveat below in mind.** A second identical probe
> run moved these bundled/non-rivalry numbers by 13–28 points (the hand build's "16% bundled" became
> 31%), so the round-1 probe deltas are **within measurement noise**. The claims that survive are the
> deterministic ones (the hub, titles, altitude) and the direct-inspection ones — not the probe %s.

---

## Round 2 — the fixes, and a measurement caveat that reframes the result

The three fixes from round 1 were applied to the harness (skeleton-refinement pass, agent-driven
antithesis recall, 4-leaf cap + claims-only mode) and re-run into `out-debate-fix`. Four-way now:

| metric | v1 naive | harness v1 | **harness fix** | v2 hand |
|---|---:|---:|---:|---:|
| nodes | 32 | 68 | **57** | 45 |
| max in-degree | 13 | 4 | 4 | 5 |
| hubs (≥8) | 1 | 0 | 0 | 0 |
| titled | 12% | 100% | 100% | 100% |
| antithesis sets | 10 | 5 | **12** | 7 |

### The measurement caveat (the most important thing this round found)

Before trusting any bundling/rivalry delta: **the LLM structural probe is too noisy to measure them.**
Run identically twice on the *same* graphs, it swung by ±13–28 points:

| graph (identical both runs) | bundled% | non-rivalry% |
|---|---|---|
| v1 naive | 38% → 25% | 80% → 80% |
| v2 hand | 16% → 31% | 43% → 71% |
| harness v1 | 29% → 43% | 40% → 60% |

A deterministic regex bundle-proxy (`compare.py`) is no better — *biased* rather than noisy: it flags
the **hand build highest** (51% vs the harness builds' ~39%), because it fires on legitimate
compound-but-single claims. So **neither cheap instrument measures semantic bundling reliably** — the
LLM judge is high-variance, the regex is systematically biased. This is the same lesson the project
already learned for *rating* quality (single cheap signals are unreliable; you need panels or
structural markers), now recurring for *build/QA* quality. Measuring structural quality at scale is
itself an open problem — a real finding, and a caution against reading any single probe number as fact.

### What survives the noise (and therefore what we can actually claim)

- **Robust, deterministic, probe-independent** (identical every run): skeleton-first kills the hub
  (in-degree 13→4, hubs 1→0) and mandatory titles hold (12%→100%) — in **both** harness runs. The
  sprawl cap worked: 68→57 nodes. These are the load-bearing wins and they don't depend on any judge.
- **Skeleton de-bundling (fix #1): confirmed by inspection, directionally by count.** The roots are
  unambiguously fixed — e.g. root n001 went from *"…misdescribes how disagreement is structured and
  generated **and** is not practically usable, **so** the whole endeavor is doomed"* to *"Structured
  argument-mapping will not meaningfully improve real-world reasoning on contested questions."* The
  within-run skeleton-bundled count (same judge, same pass, so the *relative* number is more
  trustworthy than cross-run absolutes) roughly halved: 14/16 → 7/16, while leaves stayed clean in
  both. **Residual:** the still-bundled limbs are the *enumerative* ones — a "concessions" limb that
  lists its four concessions, a "mechanisms" limb that lists four features — instead of naming the
  category as one proposition (the hand build's *"the conceded limitations bear against it"*). The
  refiner rewrote sentence-level bundles but didn't collapse enumerations.
- **Antithesis recall (fix #2): the missed rivals are now caught — with a redundancy cost.** Sets
  5→12: the recall step found exactly the genuine rivalries v1 missed (viability, demographic,
  history — confirmed by inspection). But it *over-generated by redundancy*: two near-duplicate
  value-crux sets, two overlapping viability sets, a couple of cross-wired pairs. The both-true gate
  doesn't catch this because a duplicate set is still a *valid* rivalry — redundancy is a different
  defect than non-rivalry, and needs its own guard.

### Net verdict and the follow-ups this round earned

Skeleton-first + mandatory titles are validated as robust, cheaply-measurable wins that close the
worst of the v1→hand gap. The bundling and antithesis checks help — de-bundled roots, recovered
rivals — but each earned a specific, un-run follow-up rather than a clean pass:

1. **Refiner should treat a limb as a category label, not a summary** — collapse enumerations
   ("concessions: A, B, C, D" → "the conceded limitations bear against it"), pushing the enumerated
   items down to leaves. This is the residual bundling.
2. **Antithesis phase needs a dedup / one-set-per-sub-question guard** — recall is now good;
   precision-by-redundancy is the new failure.
3. **Structural-quality QA needs a real instrument** — a probe *panel* (N judges, averaged, the
   project's own rating fix) or better deterministic topology, not a single cheap judge. Until then,
   the trustworthy comparison is the deterministic-topology metrics plus targeted inspection.

These are worth doing, but note they are refinements to a harness that *already* clears the two
pathologies that most needed hand-fixing. The v1→hand gap remains harness-shaped; the residual is now
two small guards and — the surprise of this round — a better ruler.
