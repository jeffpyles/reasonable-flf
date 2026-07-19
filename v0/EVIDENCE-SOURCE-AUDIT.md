# Evidence-source audit — the four v2 flagship graphs (2026-07-18)

A pass over every evidence node in the four v2 graphs, asking two questions:

1. **Overlap** — do multiple nodes make the *same* point from different studies, when they should be
   **one claim grounded by several study-nodes**?
2. **Bad sources** — is a **secondary aggregator** (Wikipedia, popular science reporting, a review or
   consumer-health page restating someone else's result) listed as the *source* of a factual claim
   whose real origin is a prior study?

Method: enumerate `kind ∈ {evidence, external_anchor}` nodes; read each node's **source title/url**
(not just its paraphrased text — the paraphrase often hides the aggregator) and what it grounds;
compare same-target / high-text-overlap pairs. Changes are applied via `supersede` (reversible) +
`graph.py rebuild`, never a `build.py` rerun (that would wipe the post-build Haiku fill).

---

## Applied — 4 nodes ghosted (unambiguous: aggregator restating content already primary-sourced)

| graph | node | source | why | downstream |
|---|---|---|---|---|
| blackholes | **n032** | Phys.org 2008 | popular reporting of the Giddings-Mangano white-dwarf result already carried by primary nodes n030/n031 (s02) grounding the same claim n034 | n034 keeps 4 grounds |
| blackholes | **n043** | Phys.org 2008 | popular reporting narrating the layered safety case (Hawking + white-dwarf), both halves already carried by n015 / n031 / n021 grounding n022 | n022 keeps 6 grounds |
| eggs | **n055** | consumer-health blog (s15) | restates its own sole dependent claim n058 (protein/satiety → weight management); a blog isn't the source of the fact | n058 remains as a claim |
| eggs | **n056** | consumer-health blog (s15) | restates its own sole dependent claim n059 (yolk lutein → eye-disease risk) | n059 remains as a claim |

All four are reversible (`supersede --restore`). Lint stays clean on both graphs (0 hubs / orphans /
malformed). These change edge counts, so the ghosts go to Assessment's re-rate along with the
interconnection edges.

## Good news — no overlap *defect*; the apparent duplicates are correctly structured

The pairs that looked like "same point, two nodes" are in fact **one claim grounded by two independent
study-nodes** — exactly the target shape:

- **blackholes n037 (Giddings-Mangano, s02) + n038 (their metastable-rebuttal follow-up, s13)** → both
  ground the accretion claim n039.
- **blackholes n048 (CMS first search, s10) + n049 (CMS 7 TeV search, s09)** → both ground n050.
- **covid** — the "earliest cases near the market" family (n013 geographic centering / n014 proportion
  epidemiologically linked / n025 Pekar statistical localization / n026 lineage-A proximity) are
  genuinely **distinct analyses**, not restatements; and the raccoon-dog pair (n008 co-location vs n064
  Bloom's non-correlation reanalysis) is a genuine **antithesis**, not a duplicate. No covid folds.

## Flagged — Wikipedia / secondary as source of a *scientific* fact (re-source, don't ghost)

These claims are valid and often load-bearing; the fix is **re-pointing the source** to the primary
literature, not removal. Left in place pending correct citations (a domain call — Graphs' lane, and
covid was not rebuilt by this thread):

- **covid n049–n052** — source tagged *"Proximal Origin (Wikipedia)"*, but the node text is about the
  **Andersen et al. 2020, Nature Medicine** paper itself (named verbatim in the text) — its conclusion,
  drafting history, and published genomic case. Re-point to the paper (self-evident from the text).
  (Minor: n050 and n051 both narrate the Proximal-Origin *draft* and mildly overlap — one candidate to
  merge if desired.)
- **blackholes n006/n015** (*Micro black hole — Wikipedia*) and **n014/n017** (*Hawking radiation —
  Wikipedia*) — foundational physics whose real sources are the extra-dimensions papers and Hawking
  1974. Re-point to primary refs.

## Kept — reporting/book as source of a *social / legal / institutional* fact (legitimate)

Here the fact **is** a social one and reporting is the appropriate primary-accessible record, not a
stand-in for a study:

- **covid n066/n067** (WHO SAGO conclusion — could optionally re-source to the SAGO report), **n088–n092**
  (what U.S. intelligence agencies / DOE / FBI assessed — reporting is the record for agency positions),
  **n118** (an *argument* attributed to the Chan & Ridley book *Viral* — sourcing a position to where it
  is made; optionally re-type evidence→claim as it's an argument, not a study finding).
- **blackholes n059/n063/n065** (NBC / Phys.org / Symmetry on the Wagner-Sancho lawsuit and its
  dismissal — legal facts).
- **eggs n052** (Harvard Nutrition Source commentary — a genuine distinct provenance fact: the 300 mg/day
  cap predates any trial). Kept. **eggs n051** (same source, only restates the interpretation its
  dependent n061 already makes) is a mild redundancy candidate, flagged not ghosted.

---

### Summary

- **4 clean ghosts applied** (blackholes n032/n043; eggs n055/n056) — aggregator restating
  already-primary-sourced or self-duplicating content.
- **0 overlap defects** — the same-finding pairs are already the correct "two studies → one claim" shape.
- **~8 Wikipedia/secondary-for-science nodes flagged for re-sourcing** (covid n049–n052; blackholes
  n006/n014/n015/n017) — valid claims, wrong source attribution; needs correct primary citations.
- **Reporting-for-institutional-facts kept** as legitimately sourced.
- **eggs n051** flagged as a soft redundancy call.
