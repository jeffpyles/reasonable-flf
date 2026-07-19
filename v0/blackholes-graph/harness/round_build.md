# blackholes-graph — coverage-driven build round (shared brief)

You are one author in a persona-diverse **Sonnet** swarm building the argument graph for
"Could a high-energy particle collider (the LHC) create a black hole that destroys Earth?" in a
**fresh** dataset (`--data blackholes-graph`), run **sequentially** (each author sees prior work).
Feedstock: a deep-research report (`blackholes-graph/harness/REPORT.md`) plus the exact sources it
drew on (`blackholes-graph/harness/sources.json`). Same evidence in, structured graph out — a
controlled comparison against the flat report.

**This is a "confident-answer" question.** The scientific answer is a well-established *no* — but
build **both** top-level answers fairly: the safety answer AND the contrarian catastrophe claim,
each as a positive claim in the root antithesis. The interesting structure here is *how decisively*
the evidence grounds the safety answer and *how thinly* it grounds the catastrophe claim — let the
graph show that, don't assume it.

**Your job: make sure every isolatable claim in your assigned cluster is extracted, placed,
phrased, and connected — nothing load-bearing left unmapped.** "Restraint" means restraint in *form*
(atomic, well-formed, no duplicates), never omitting a real claim.

## Before you start
1. Read `AGENT-GUIDE.md` fully — the mental model, the norm discipline, the verb reference. Binding.
   Most important rule: **support-only** (opposition is a rival *positive* claim in an antithesis
   set, never a "not-X" node).
2. Read your persona brief (`blackholes-graph/harness/personas/<your-id>.md`) — who you are and
   which cluster you own.
3. Read `blackholes-graph/harness/REPORT.md` and the sources in your cluster from `sources.json`.

## Per claim in your cluster
1. **`search` first** — reuse / `agree` / `propose-phrasing` rather than duplicate.
2. **Extract every isolatable claim.** One node = one truth-apt proposition. Split bundled claims
   and draw the support edge. Write at the generality the source supports; don't invent numbers.
3. **Structure it:** `draw-ground --from EVIDENCE --to CLAIM` (support flows forward); `--group` for
   conjunction only when grounds support jointly; rival positive claims share an **antithesis** set
   (the two top answers are the root antithesis); a better wording is a `propose-phrasing`.
4. **Keep the two layers distinct:** anchor **evidential facts** (Hawking-radiation theory, cosmic-
   ray flux measurements, LHC energies, safety-review conclusions) as `external_anchor` nodes cited
   to a `sources.json` id; leave **interpretive/contested** claims un-anchored as rival positive
   claims.
5. **`flag-friction`** whenever the grammar strains — a claim that resists atomization, correlated
   evidence treated as independent, a rhetorical-not-evidential move, a category error, a missing
   piece. Friction flags are a **primary deliverable**.

## Coverage self-check (required)
Re-read your cluster's report claims + sources and confirm each is represented (node, edge,
phrasing, or explicit friction). Don't fabricate coverage — if something didn't fit, flag it.

## Final line
`<your-id>: added N nodes, M edges, A antitheses, P phrasings, F frictions; cluster-claims covered X/Y (list any uncovered)`.
