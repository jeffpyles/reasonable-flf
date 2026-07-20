# covid-graph — coverage-driven build round (shared brief)

You are one author in a persona-diverse Sonnet swarm building the SARS-CoV-2-origins argument graph
in a **fresh** dataset (`--data covid-graph`), run **sequentially** (each author sees all prior
work). This build is unusual in one way: it is **coverage-driven**. The feedstock is a deep-research
report (`covid-graph/harness/REPORT.md`) plus the exact sources it drew on
(`covid-graph/harness/sources.json`). Our goal is a controlled comparison: the flat report and this
structured graph are built from the **same evidence**, so any difference is a difference in
*representation and sense-making*, not in what information each reached.

**Your job: make sure every isolatable claim in your assigned cluster is extracted, placed,
phrased, and connected — nothing load-bearing left unmapped.** "Restraint over volume" here means
restraint in *form* (atomic, well-formed, well-connected, no duplicates), never omitting a real
claim. Full depth is the target.

## Before you start
1. Read `AGENT-GUIDE.md` fully — the mental model, the norm discipline, and the verb reference. It
   is binding. The most important rule: **support-only** (opposition is a rival *positive* claim in
   an antithesis set, never a "not-X" node). **"Not-X" is a diagnosis, not a node type** — route the
   urge (AGENT-GUIDE §2): competing answer → rival positive node + `add-antithesis`; weak premise →
   low rating on the claim/edge/ground; specific undercutter → positive node grounded at the joint it
   defeats; X simply false → low-rate it to a settled ghost + a `comment` for the reason; nothing but
   opposition → that's your low rating, not a node. (An absence-claim like "no infected intermediate
   host found" is a legitimate *positive* node — the ban is on negation as a *relation*, not the word
   "not.")
2. Read your persona brief (`covid-graph/harness/personas/<your-id>.md`) — who you are and which
   evidence cluster you own.
3. Read `covid-graph/harness/REPORT.md` (the deep-research synthesis + its verified claim list) and
   the sources in your cluster (`covid-graph/harness/sources.json`, filter to your cluster's tags).

## What to do, per claim in your cluster
1. **`search` first** — reuse / `agree` / `propose-phrasing` rather than duplicate. On a fresh graph
   early authors create most nodes; later authors mostly connect, phrase, and fill genuine gaps.
2. **Extract every isolatable claim.** One node = one truth-apt proposition. If a report sentence
   bundles two claims ("X, and therefore Y"), split them and draw the support edge X→Y. Write at the
   generality the source supports — do not invent specific statistics/sequences beyond the pack.
3. **Structure it:**
   - `draw-ground --from EVIDENCE --to CLAIM` (support flows forward; get the direction right).
   - Use `--group` for conjunction only when grounds support the dependent *jointly*.
   - Rival positive claims go in the same **antithesis** set (`add-antithesis`). The two top-level
     answers (zoonotic spillover vs. research-related incident) are the root antithesis.
   - A better wording of an existing node is a `propose-phrasing` (alternative statement), not a new
     node.
   - `propose-typing` where the edge/claim kind is worth marking.
4. **Keep the two layers distinct** (this graph's signature design choice): anchor the **evidential
   facts** both camps accept as `external_anchor` nodes cited to a source id from `sources.json`
   (`list-studies` to reuse an id); leave the **interpretive cruxes** as **un-anchored reasoning
   nodes** — rival positive claims in antithesis sets. This mirrors the real epistemic situation:
   shared facts, contested inferences.
5. **`flag-friction`** whenever the grammar can't cleanly express something (a claim that resists
   atomization, a correlation-treated-as-independence, a rhetorical-not-evidential move, a missing
   piece). Friction flags are a **primary deliverable**, not a failure — they are exactly the
   structure a flat report can't show.

## Coverage self-check (required, end of your turn)
Re-read the report claims + sources in your cluster and confirm each is represented (as a node, an
edge, a phrasing, or an explicit friction flag). Do not fabricate coverage — if something didn't
fit, flag it.

## Final line
Output exactly one line:
`<your-id>: added N nodes, M edges, A antitheses, P phrasings, F frictions; cluster-claims covered X/Y (list any uncovered)`.
