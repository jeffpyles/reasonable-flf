# eggs-graph — coverage-driven build round (shared brief)

You are one author in a persona-diverse **Sonnet** swarm building the argument graph for
"Are eggs bad for your health? (Does egg / dietary-cholesterol consumption meaningfully raise
cardiovascular-disease and mortality risk for most people?)" in a **fresh** dataset (`--data
eggs-graph`), run **sequentially** (each author sees prior work). Feedstock:
`eggs-graph/harness/REPORT.md` + `eggs-graph/harness/sources.json`.

**This is a "mundane-but-contested" question** — no dramatic verdict, but a genuinely mixed evidence
base. Build **both** top-level answers fairly as the root antithesis: *eggs are bad for your health*
(they meaningfully raise CVD/mortality risk for most people) vs. *eggs are not bad for your health*
(negligible CVD effect for most people, and real nutritional benefits). The interesting structure is
that the **general-population** answer leans reassuring, the **diabetic-subgroup** answer leans
cautionary, and the **causal** question stays genuinely open — let the graph show those distinctions
rather than collapsing them.

**Your job: extract every isolatable claim in your assigned cluster — place, phrase, connect it —
nothing load-bearing left unmapped.** Restraint is in *form* (atomic, well-formed, no duplicates),
never in omitting a real claim.

## Before you start
1. Read `AGENT-GUIDE.md` fully — binding. Most important rule: **support-only** (opposition is a rival
   *positive* claim in an antithesis set, never a "not-X" node). **"Not-X" is a diagnosis, not a node
   type** — when the urge hits, route it (AGENT-GUIDE §2): competing answer → rival positive node +
   `add-antithesis`; weak premise → low rating on the claim/edge/ground; specific undercutter →
   positive node grounded at the joint it defeats; X simply false → low-rate it to a settled ghost +
   a `comment` for the reason; nothing but opposition → that's your low rating, not a node. (An
   absence-claim like "no long-term RCT exists" is a legitimate *positive* node — the ban is on
   negation as a *relation*, not the word "not.")
2. Read your persona brief (`eggs-graph/harness/personas/<your-id>.md`) — your cluster.
3. Read `REPORT.md` and the sources in your cluster from `sources.json` (filter by tags).

## Per claim in your cluster
1. **`search` first** — reuse / `agree` / `propose-phrasing` rather than duplicate.
2. **Extract every isolatable claim.** One node = one truth-apt proposition. Split bundles; draw the
   support edge. Write at the generality the source supports; don't invent effect sizes beyond the pack.
3. **Structure it:** `draw-ground --from EVIDENCE --to CLAIM` (support flows forward); `--group` for
   conjunction only when grounds support jointly; rival positive claims share an **antithesis** set
   (the two top answers are the root antithesis; also e.g. "saturated fat drives LDL" vs "dietary
   cholesterol drives LDL"); a better wording is a `propose-phrasing`.
4. **Keep the two layers distinct:** anchor **evidential facts** (RCT lipid effects, cohort
   associations, the 2015 guideline change, nutrient content) as `external_anchor` nodes cited to a
   `sources.json` id; leave **interpretive/contested** claims un-anchored as rival positive claims.
5. **`flag-friction`** wherever the grammar strains — a claim that resists atomization, correlated
   cohorts treated as independent, an association stated as causation, a subgroup effect generalized,
   an industry-funded source, a missing piece. Friction flags are a **primary deliverable**.

## Coverage self-check (required)
Re-read your cluster's report claims + sources; confirm each is represented (node, edge, phrasing, or
explicit friction). Don't fabricate coverage — if something didn't fit, flag it.

## Final line
`<your-id>: added N nodes, M edges, A antitheses, P phrasings, F frictions; cluster-claims covered X/Y (list any uncovered)`.
