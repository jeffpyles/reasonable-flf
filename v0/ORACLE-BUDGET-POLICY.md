# Where to spend oracle-points — a triage policy for the assessment layer at scale

*Logged 2026-07-15. The full site maps millions of nodes; we cannot run an oracle panel over every node
and edge. Both of our reference-dependent defenses — per-rater **calibration** and the **verdict-certainty
guardrail** — can only act on nodes that carry an oracle reference. So oracle-points are the scarce
resource the whole assessment layer spends, and the adversarial runs (`eggs-adversarial/`,
`covid-adversarial/`) tell us where to spend them. This note is that policy.*

## The constraint
- The certainty guardrail fires on "decisiveness beyond what the oracle warrants." **No oracle value →
  no warrant → it is blind on that node.** Calibration is the same: an anchor with no oracle value can't
  un-distort anyone. Oracle coverage *is* the defense's footprint.
- Uniform coverage is impossible at scale, so coverage must be **triaged** by value.

## The key realization: the oracle does TWO jobs, on TWO different node sets
People conflate "the oracle." It has two roles with different node targets and different budgets:

| role | wants nodes that are… | job | how many |
|---|---|---|---|
| **calibration anchors** | checkable facts with tight cross-model agreement (low oracle sd) | fit each rater's transfer function; neutralize crude attacks | few — ~10 sufficed on eggs |
| **verdict / certainty reference** | the contested frontier — top answers + decisive cruxes | catch the sleeper / over-certainty capture the anchors don't cover | tiny for detection (see below) |

Spending the whole budget on the intuitive "oracle the facts" (calibration only) leaves the sleeper and
over-certainty attacks wide open, because those attacks live in the contested gaps the fact-anchors don't
touch. You must fund the second role explicitly.

## The efficiency finding: DETECTION is astonishingly cheap
In the guardrail test (`covid-adversarial/run_certainty_guard.py`) the sensitive signal — the one that
caught **both** sleepers — was the **verdict signal, keyed on just 2 oracle'd nodes** (the top answers
n001/n002). The frontier signal over all 12 cruxes was redundant and only added anything at 50–60%
attacker fractions. **Two well-chosen oracle points bought the sleeper detector.** This splits the budget:

- **Detection** ("is this verdict being captured or hardened past warrant?") → oracle the **verdict
  nodes** of contested questions. Tiny set, enormous leverage. First points go here.
- **Correction / attribution** ("which crux carried the lie, so we can down-weight it?") → oracle the
  **cruxes feeding a verdict**, spent only where detection already fired. More nodes, demand-driven.

## Why this is budgetable at all: the attack's objective picks the target for us
A capture attack *must* move the verdict — that is its objective — and the verdict is a tiny, identifiable,
high-value node set. So the place oracle-points are most efficient (the top answers) is exactly the place
the attacker is forced to appear. A sleeper lying in un-oracled peripheral cruxes only matters insofar as
its lies **propagate up** to the verdict — and the verdict is watched. You detect the *result* of a
capture even before you can attribute it.

## The policy: triage by cheap unsupervised signals, don't spread
Oracle-points follow a priority order driven by signals that cost **no oracle** to compute:

1. **Verdict nodes of contested questions** — nominated (in priority order) by a **belief-camp split /
   coordinated-bloc flag from spectral camp-detection** and by **structural** contestedness (antithesis
   membership, friction flags), then graph centrality/degree. Raw rating stdev is a **weak, demoted**
   nominator — it is only valid when dispersion is camp-driven (high between-camp variance) and is
   lens/offset noise otherwise (see `dispersion-regimes/`), so use the camp structure, not the spread.
   Oracled first, and **re-oracled on a rotation**.
2. **A sample of the decisive cruxes** feeding those verdicts — for correction, once detection fires.
3. **A thin, rotating layer of calibration anchors** on high-agreement facts — enough to fit transfer
   functions, no more (~10 per contested region was plenty on eggs).
4. **Everything else: no oracle** until a cheap signal promotes it. Uncontested, peripheral, or
   low-traffic nodes don't earn a point.

## Two riders from the runs
- **Rotate the oracled set.** The sleeper's entire edge is *knowing* the anchor/reference set; a secret,
  rotating oracle degrades a sleeper back toward the (defended) naive attack. Rotation is a defense, not
  just hygiene.
- **This is active learning, and it is the scalability story.** The graph's own disagreement structure
  nominates where truth-assessment is worth buying, so **oracle spend scales with contestedness, not with
  graph size.** The machinery is *not* bottlenecked on oracling everything — a direct answer to FLF
  dimension #4 (scalability): more compute and better models raise the ceiling, but the *coverage* budget
  is governed by how much of the graph is actually contested, which is a small, signal-identifiable slice.

## Honest limits
- The guardrail is only as good as the oracle reference — it flags hardening *beyond the reference*, not
  ground-truth over-confidence. Triage concentrates a finite, imperfect reference where it matters most; it
  does not make the reference correct.
- An adaptive attacker who can *infer* the rotating oracle set, or who spreads a capture across many
  low-traffic verdicts below the disagreement-trigger, is the untested next tier (see
  `ROADMAP-NEXT-VERSION.md` #5). Triage raises the attacker's cost; it does not close the problem.
