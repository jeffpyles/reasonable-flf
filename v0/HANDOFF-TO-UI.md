# Handoff to the viewer/UI thread — data-layer state + what the viewer needs to render

*From the fermi thread, 2026-07-17. Two parts: (1) an **update** — what the data layer now provides
that the viewer can consume, and (2) a **spec** — the rendering the graph now expects, especially the
ghost state and normalized-strength layout (SPEC-evidence-argument-ought-ghosts.md §3–§4). Everything
below is live on `main` in `graph.json` + the read verbs; nothing here needs new backend work.*

---

## Part 1 — What we've built (the update)

**Grammar (SPEC §1).** Nodes now carry a `kind`: `claim` (an *Argument* — internal reasoning),
`evidence` (a *fact from a source*; the old `external_anchor`, kept as a read alias), or `ought`
(an *action/value*). Hume's rule is enforced (an ought can't ground a non-ought). `flag-type` opens a
type-resolution poll — **now live** (see the Type-resolution poll note below).

**Assessment (Assessment thread, live).** Each node/edge/phrasing carries the full lifecycle envelope
(`agreement`, `quality` R/C) with `state ∈ {sealed, provisional, settled, contested}`, era/history/
blocs. Reputation accounts, calibrated consensus (now guarded — declines on low-spread anchors),
and **Ought nodes are rated on democratic (unweighted) endorsement, not truth**. The `contested`
verb gives a per-node/edge verdict (`contested` / `settled` / `ghost_eligible`) off structural +
belief-camp signals (not raw stdev). Enforced blind Rating mode is a dataset flag.

**Type-resolution poll (SPEC §2.2, Assessment thread — added 2026-07-17).** A node's *type* is now
resolved by a reputation-weighted **categorical poll**, completing the `flag-type` → Ought pipeline.
`flag-type` opens it (a non-folding marker); raters cast **Yes / No / decline** with the new
**`poll-vote`** verb; the **`polls`** read verb shows tallies + resolution. Resolution is reputation-
weighted (quorum 5 **and** a 0.66 True_R-weighted Yes-share; `decline` is recorded but abstains). A
poll resolved to `ought` flips the node into the democratic-endorsement treatment above; a claim→Ought
resolution raises **`reopen_required`** (the rating dimension changes truth→endorsement, so an explicit
`reopen` isolates the old truth ratings into a closed era). **`graph.json` gains a top-level `polls`
array only when a poll has ≥1 vote** (dormant flags render nothing, so poll-free graphs are unchanged):
`[{node, question, yes, no, decline, n_votes, yes_share, resolved, resolved_kind, reopen_required}]`.

**Ghost lifecycle (SPEC §3, this thread).** Two ghost signals now live in the data:
- **`ghost_eligible: true`** — the AUTO signal (refuted on own Agreement, settled, not an antithesis
  rival). **Now exported directly into `graph.json`** as a conditional per-target flag on nodes and
  edges (present only when true; identical rule to the `ghosts` read verb), added 2026-07-17 at the
  viewer thread's request so auto-ghosts render identically to manual `demoted` ones with no
  client-side re-derivation. The `ghosts` verb still returns the same set plus its diagnostics.
- `supersede` verb → a **`demoted`** marker `{reason, agent, seq}` on a **node, edge, or antithesis
  set** (manual demotion; `--restore` un-demotes). Never a delete — the target and its history stay.
- Render both the same way (grey / z-sink): a target is a ghost if it carries **either** flag.

**Coherence (SPEC §4, this thread).** `lint` flags hubs, orphans, malformed sets, question/negation
framing, and redundant direct-vs-layered paths (§3.3). Advisory. Demoted items are skipped.

**Strength (SPEC §3.4).** `chain` exposes per-path `product`, `weakest_link`, and **`geometric_mean`**
(length-normalized strength). `compare` walks two nodes back to their last common ancestor.

**Strength formula — pinned for the viewer's client-side replica (added 2026-07-18; no snapshot export).**
There are **two distinct strength metrics**; they are *deliberately different* and must not be reconciled
to each other. The viewer asked which basis `chain`'s geomean uses so its declutter replica can't silently
diverge — here is the exact answer for both:

1. **`chain` path-strength** (SPEC §3.4 / PHASE2-SPEC §7 — the `chain`/`compare` verbs). The full
   chain-rule product over a support path. Every factor on the path contributes: **both endpoint nodes'
   Agreement, every interior node's Agreement, *and* every edge's Agreement** (a grouped edge contributes
   via its conjunction-group's A, not its own), each taken as `mean/5`, an unrated element → neutral
   `2.5/5`. `product` = ∏ of all those factors; `geometric_mean` = `product ** (1 / len(factors))` where
   `len(factors) = (#nodes + #edges on the path)`. It answers *"how sound is this whole support chain,
   end to end?"* — so it legitimately folds in node truth. This is **not** an "edge_A per hop" geomean and
   **not** a "node_A·edge_A per hop" geomean; it's the per-factor geomean over the full interleaved
   node/edge sequence.

2. **Shortcut-redundancy / competition geomean** (§2.3/§2.4 — the viewer's declutter basis). This is
   **not** `chain`'s formula, and it should not be. It runs over **`edge_A` per hop only** (edges only;
   node Agreement excluded), bounded DFS **≤4 hops**; a direct edge is redundant iff some alternate path's
   geometric mean of per-hop `edge_A` **strictly exceeds** the direct edge's own `edge_A` (ghost edges and
   conjunction-group members excluded — a single-hop direct edge's geomean is just its own `edge_A`).
   Excluding node Agreement here is correct: mixing the source node's own truth into an *edge-competition*
   comparison double-counts it (the viewer's own reasoning, endorsed). The client-side replica is a pure
   function of the `edge_A` values already in the snapshot, so it is **identical to any server computation
   by construction given this formula** — there is intentionally no `chain` export for it.

If (2) is ever wanted authoritative in the snapshot, the clean shape is the `ghost_eligible` pattern: a
per-direct-edge `shortcut_redundant: true` flag plus the winning path's node ids and its edge_A-geomean —
consume-don't-rederive, no client replica. A post-submission nicety; the replica suffices now.

**Layer (layout seed — added 2026-07-18).** Every node now carries an integer **`layer`** in
`graph.json` — its Kahn longest-path **support-depth** (a ground supports its dependent, so
`layer[to] = max(layer[from]) + 1`; a source/evidence node is `0`, top-answer sinks are deepest).
Use it to **seed initial x-positions** before the force sim runs (evidence left → dependents right),
per the force-directed / self-assembly direction (Feature Discussions #33) — not as fixed columns.
Deterministic, present on every node, matches the viewer's own Kahn-longest-path fallback so nothing
drifts. Cyclic inputs degrade gracefully (partial layering; the force sim is the cycle fallback).

**Content.** Three built + panel-assessed FLF graphs — `covid-graph` (contested), `blackholes-graph`
(confident-answer), `eggs-graph` (mundane-contested) — each with a cross-model oracle where built
(`covid/anchors.json`, `blackholes-graph/anchors.json`) usable as scoring references.

---

## Part 2 — What the viewer needs to render (the spec)

### 2.1 Node kinds — three visual roles
Render `evidence`, `claim` (Argument), and `ought` distinctly. Evidence is a boundary *leaf* on the
grounding side (anchored by its `source_ref`, not by in-graph grounds); Ought is a boundary terminal on
the other side (an action/value out). The Evidence↔Ought symmetry should read visually. **An Ought is
rated on endorsement, not truth** — don't render its Agreement with truth-coded color; use an
endorsement cue.

**Name the source on the Evidence node body (FLF requirement — added 2026-07-18).** Every Evidence node
now carries a resolved **`source`** object in `graph.json`:
```
"source": {"ref": "s08", "title": "Liu, Liu et al. (2023), Surveillance of SARS-CoV-2 at the Huanan…", "url": "https://…"}
```
Render **`source.title`** at the bottom of the node's body zone (link it to `source.url` when non-null).
`ref` is the raw token (dedupe/grouping key — same study → same `ref`); `title` is the human name (falls
back to the raw ref for self-describing free-text sources, e.g. debate's `acx-solve-debate-2026`); `url`
is `null` when unknown. The field is present on every Evidence node with a source, absent otherwise —
baked into the snapshot by the fold (same consume-don't-re-derive pattern as `ghost_eligible`), resolved
from the graph's `harness/sources.json` build manifest and the curated `sources/<pack>` refs.

### 2.2 The ghost state (§3.1/§3.2) — the big new rendering ask
A node/edge/set is a **ghost** when it is `ghost_eligible` (auto) or carries a `demoted` marker
(manual). Render ghosts **greyed and sunk in the z-axis to a layer below the living graph**, with
near-zero pull on the force layout — present but clearly retired (the record of "we checked this, it's
wrong/superseded" is a primary asset, never deleted). Two cautions from the spec:
- **A demoted marker or `ghost_eligible` → ghost. An antithesis *loser* is NOT a ghost** — a rival that
  floated below its competitor is *less supported, not wrong*; dim it relative to the winner but keep it
  live (minority-truth / Semmelweis protection). The `contested` verb already encodes this (antithesis
  members are never `ghost_eligible`); honor it.
- A `demoted` set (e.g. a spurious antithesis) should drop its ring from the living layout.

### 2.3 Normalized strength drives layout + declutter (§3.4) — avoid the flatness trap
Drive both **force-direction** and **declutter** off the **length-normalized (geometric-mean)** strength
from `chain`, **not** the raw product. The raw chain-rule product systematically favors flat/direct
edges (each hop multiplies a factor <1), so a naive "stronger edge pulls tighter" would self-assemble
the graph *toward flatness*, undoing layering. Keyed on geometric-mean, layering is rewarded.
- **Declutter:** show a node as a ground of the focus only where its connection is strongest; **hide a
  shortcut edge when a stronger layered path already exists**, surfacing it on focus/expand. (This is
  how the hub topology the `lint` verb flags — covid n001 has 19 direct grounds — reads as layered
  without editing the data.)
- **Detail-view cues:** left↔right positioning of ground/dependent, line width, and color all keyed to
  normalized strength.

### 2.4 Competitive edge comparison (§2.4) — redundant paths
When `lint` reports a redundant path (a direct edge whose endpoints are also joined by a layered path),
the viewer should be able to present the **competing edges side by side, flagged as in competition**, and
collect edge-Agreement ratings in that comparative context (comparative judgments are more reliable than
absolute ones). Keep the absolute 0–5 edge scale as the anchor; the comparison sharpens, not replaces it.

### 2.5 Lifecycle / blinding (already in the data)
Respect `agreement.state` (sealed/provisional/settled/contested) for maturity cues, and **Rating mode**
(when the dataset's `rating_mode_only` is set, the read verbs already blind consensus cues — the viewer
should present the same blind surface so a rater forms an independent judgment before seeing the crowd).

### 2.6 Type-resolution poll (§2.2) — a node whose *type* is under vote
When a node appears in the top-level **`polls`** array, its **type is being contested** — a distinct
state from Agreement-contested, and worth its own affordance:
- Show the **Yes / No / decline** tallies and the reputation-weighted **`yes_share`**. `decline` is
  first-class ("considered and rejected" ≠ "didn't engage") — surface it, don't fold it into No.
- **While `resolved` is false, keep rendering the node as its *current* kind** (a claim stays truth-
  rated). §2.3: default to truth-rating while the type is contested — don't flip to the endorsement cue
  prematurely.
- **On `resolved: true`**, the node adopts its `resolved_kind` role (e.g. the Ought endorsement cue from
  2.1). If **`reopen_required`** is set, show a *pending-flip* indicator — the dimension change (truth→
  endorsement) isn't complete until an explicit `reopen` turns the era, so the old truth ratings are
  still showing until then.
- A resolved re-typing is a good candidate for a small provenance affordance ("re-typed by poll, N:M") —
  the record of *why* a node's type changed is an asset, the same principle as never-deleting ghosts.

---

## Where to look
- `graph.json` schema: nodes/ground_edges/antithesis_sets carry `kind`, `agreement`/`quality` envelopes,
  and (when present) `demoted`; a top-level `polls` array appears when any type poll has votes. Read
  verbs: `graph.py ghosts | lint | contested | chain | compare | polls`.
- Specs: `SPEC-evidence-argument-ought-ghosts.md` (§1 grammar, §2 assessment, §3 ghost/layout, §4
  coherence — status blocks mark what's live), `ASSESSMENT-SPEC.md` (rating/reputation), `AGENT-GUIDE.md`
  (the verb surface). `LINT-REVIEW.md` shows a worked triage of the coherence findings.
- Sample data to render against: `covid-graph/`, `blackholes-graph/`, `eggs-graph/` (the last now has a
  demoted set `s2` — a live example of a ghosted element).
