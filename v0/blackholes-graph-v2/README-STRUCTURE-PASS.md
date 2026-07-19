# blackholes-graph-v2 — structural-pass rebuild of the black-holes graph

*2026-07-18. The argument-structure pass applied to the "could the LHC make a black hole that
destroys Earth?" graph. An **experimental** parallel of `blackholes-graph/` (the original is
untouched), rebuilt from scratch by a committed, reproducible `build.py`. The graph was already
structurally healthy (0 malformed sets, 0 orphans, clean rival sets); its one pathology was the
safety-thesis **hub** — n001 carried 12 direct grounds. This pass is minimal and surgical, and
carries every evidence node and interpretive claim **verbatim** (no fabricated physics).*

Reproduce: `python3 blackholes-graph-v2/build.py` (from `v0/`) — wipes and rebuilds this directory,
then replays the original Sonnet panel's Agreement ratings from `../blackholes-graph/events.jsonl`.

## What changed — one thing

**De-starred the safety thesis (n001: 12 grounds → 5 limbs).** The safety case already contained
natural aggregator claims, so the de-star **reused four existing nodes as limbs** and created only
**one** new limb, applying the harness-learned discipline that a limb text is a category-level claim,
not an enumeration:

| limb | role | new? |
|---|---|---|
| production needs unconfirmed new physics (n007) | theory: hard to even make one | reused |
| any micro black hole would evaporate at once (n015) | theory: it wouldn't last | reused |
| the astrophysical safety case is layered (n022) | cosmic-ray + stellar-survival + accretion | reused |
| the operating LHC has produced no black holes (**n070**) | direct-search / empirical | **new** |
| independent expert reviews converge on no danger (n067) | institutional verdict | reused |

The 12 raw grounds re-route through these five (e.g. "Hawking theoretically solid" and
"production/evaporation inseparable" now support the *evaporation* limb; the formal-verdict and
failed-lawsuit grounds now support the *reviews-converge* limb). One redundant edge was dropped —
n066 ("the lawsuit's scenarios failed") grounded both n001 directly and the verdict limb n067, so
only the layered path is kept. n001 drops from 12 grounds to 5; **lint hubs 1 → 0**.

Nothing else changed: no nodes removed, the four antithesis sets and five conjunction groups carried
verbatim (they were already clean rivals / joint-support groups). Titles on the four reused-as-limb
nodes were tightened to read as scannable limb labels; their rated phrasing text is untouched.

(Remaining advisory lint: 6 redundant direct-vs-layered paths — the same rater-adjudication lane
noted in the original `LINT-REVIEW.md`, created where a leaf reaches a limb both directly and via an
intermediate; not mechanical edits.)

## Ratings

The 20-rater Sonnet Agreement panel is **replayed** onto every carried node (1,456 ratings; all 69
carried nodes stay at n=20). Blackholes edges were never rated in the original, so there are no edge
ratings to carry. The one new limb (n070) starts unrated.

A blind Haiku quorum panel (4 physics/evidential/skeptic/bayesian lenses × 2 seeds, bloc `cheap`,
tenths enforced) then fills: Agreement on n070, Reasonableness + Clarity on all 70 phrasings (the
original graph carried none), and conditional Agreement on all 79 edges. Results section to follow.

## Results — quorum rating panel (2026-07-18)

An 8-rater blind Haiku panel (4 physics/evidential/skeptic/bayesian lenses × 2 seeds, bloc `cheap`,
tenths enforced) filled every gap: A on the new limb, R+C on all 70 phrasings, conditional A on all
79 edges — 1,760 ratings, zero abstentions. **Every node, phrasing, and edge is now at or above
quorum 5**, and the tenths fix held (77% of ratings off .0/.5). The carried 20-rater Sonnet
Agreement was left untouched (distinguished by bloc).

**The de-star preserved the verdict, and it's decisively a confident-answer graph:**

- **The safety answer wins overwhelmingly.** "The LHC cannot create a black hole that destroys Earth"
  scores **4.69** vs the catastrophe claim's **0.46** — the same decisive margin the original graph
  produced (safe ≈4.70), so re-routing 12 grounds through a limb layer did not distort the verdict.
- **All five limbs are strong, and the new empirical limb is the strongest.** "The operating LHC has
  produced no black holes" (**n070, 4.73**) tops the layered-astrophysical (4.65), reviews-converge
  (4.60), evaporation (4.40), and production-needs-new-physics (4.25) limbs — the direct-search
  observation is the most defensible single limb, and it now has an explicit head instead of two raw
  grounds hanging off the thesis.
- **Contested exactly where honest residual uncertainty lives.** Only 9 nodes are contested (vs 140
  settled), between-group fraction **0.0** (no belief-camp split — earned confidence, not a
  manufactured consensus): the two thesis poles, and the genuine live cruxes the graph deliberately
  keeps open — the evaporation risk-vs-safety reading (n019/n020), the captured-black-hole
  accretion/metastable pair (n039/n041), the exclusion-limits-don't-prove-safety point (n053/n054),
  and the steelman of a stable captured micro black hole (n068). A confident answer that still marks
  its own loopholes.

This is the intended behaviour for the confident-answer case shape: settled where the evidence is
overwhelming, contested only at the narrow residual cruxes — and the de-star made the *structure* of
that confidence legible (five independent limbs, each individually strong) rather than a 12-way star.

## Evidence-source audit (2026-07-18)

A pass over every evidence node asking two questions: (1) do multiple nodes make the *same* point
from different studies (overlap that should be one claim grounded by several study-nodes), and
(2) is a **secondary aggregator** (Wikipedia, popular science reporting, a review restating someone
else's result) listed as the *source* of a factual claim whose real origin is a prior study?

**Two nodes ghosted** (secondary aggregator restating content already carried by a primary source):

- **n032** (source: *Phys.org, 2008* — popular reporting) summarised the Giddings-Mangano white-dwarf
  result. That result is already carried by the **primary** study nodes n030/n031 (source s02,
  Giddings & Mangano) which ground the same claim n034. The Phys.org restatement is not the source of
  the fact; ghosted. n034 keeps four grounds (n030, n031, the LSAG/Ellis node n033, n036).
- **n043** (source: *Phys.org, 2008*) narrated the layered safety case (Hawking evaporation as first
  line, white-dwarf/neutron-star as backstop). Both halves are already carried by primary nodes
  (n015 evaporation; n031/n034 white dwarf) and the LSAG node n021, all grounding the same claim
  n022. Ghosted; n022 keeps six grounds.

Both were demoted via `supersede` (reversible, `--restore`), then `graph.py rebuild`. Lint stays
clean (0 hubs/orphans/malformed); the ghosted edges e032/e043 drop out.

**No overlap defect found.** The two apparent same-finding pairs are in fact **correctly structured**
— one claim grounded by two independent study-nodes, which is exactly the target shape:

- n037 (Giddings-Mangano, s02) and n038 (their follow-up rebutting metastable claims, s13) both ground
  the accretion-scenario claim n039 — two papers, one claim.
- n048 (CMS first search, s10) and n049 (CMS 7 TeV search, s09) both ground n050 — two distinct LHC
  searches, one claim.

**Kept (legitimate reporting-as-source):** the lawsuit nodes n059/n063/n065 (NBC / Phys.org /
Symmetry) source *legal/social* facts — who filed the Wagner-Sancho suit and how it was dismissed —
for which news reporting is the appropriate primary-accessible record, not a stand-in for a study.

**Flagged for a source-metadata fix (not ghosted — claims are valid and load-bearing):** four physics
nodes cite **Wikipedia** for foundational facts whose real source is the primary literature —
n006/n015 (micro-black-hole production / evaporation → the extra-dimensions and Hawking-evaporation
papers) and n014/n017 (Hawking radiation → Hawking 1974). These should be re-pointed to the primary
references rather than Wikipedia; left in place pending the correct citations (domain call, Graphs' lane).
