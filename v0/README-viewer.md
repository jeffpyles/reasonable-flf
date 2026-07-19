# The viewer

The **viewer / UI** of the *Reasonable* argument-mapping project — how the community-assessed
argument graph is drawn and read. (Developed for a while on the orphan `viewer-ui` branch;
rejoined `main` 2026-07-17 — the viewer thread now works here directly. `HANDOFF-TO-UI.md` is the
active roadmap for what the viewer renders next.)

**Start here:** [`VIEWER-SPEC.md`](VIEWER-SPEC.md) — what the viewer is, the project context, the current
visual language, and the open questions/ideas for improving clarity and intelligibility.

## Contents

```
VIEWER-SPEC.md   what it is + visual encoding + open UI questions (read first)
HANDOFF-TO-UI.md what the data layer now provides + the render spec for the next iterations
viewer.html      the single-file viewer (self-contained; no build step, no dependencies)
data/
  eggs-p4.json   79-node cooperative graph (the embedded default)
  eggs-p3.json   60-node graph
  eggs-p6.json   79-node graph from a different rater population
eggs-graph/      panel-assessed eggs graph (type polls + a demoted set)
covid-graph/     contested-question graph (some edges carry typings)
blackholes-graph/  confident-answer graph
debate-graph/    28-node graph with real evidence + ought kinds
```

## Viewing

- **Zero-setup:** open `viewer.html` directly in a browser — with no server, it falls back to the
  **embedded** eggs-p4 graph and renders immediately.
- **Switch graphs:** the `⋯` menu's **Load Graph…** picker jumps straight to the four premier graphs
  (Debate, Covid, Eggs, Black Holes — latest snapshots when served over http; bundled copies on the
  published artifact). Or serve the folder and use the query param, e.g.
  `viewer.html?data=debate-graph/graph.json`:
  ```bash
  python3 -m http.server 8000    # then open http://localhost:8000/viewer.html?data=debate-graph/graph.json
  ```

## How to read a graph (quick)

Each card is a **claim**. In focus view (click a card): **Grounds** (what supports it) sit to the left,
**Dependents** (what it supports) to the right, and **Antitheses** (rival claims) stack vertically
through the focus, strongest at the top. Every color cue shares one **dark (bad/split) → bright
(good/tight) spectrum**, told apart by card zone (thin black rules separate them): the **title bar** =
community **Agreement** with the claim, the **body** = the leading phrasing's **Reasonableness &
Clarity**, and the **bottom bar** = rating **consensus** (dark = contentious; that's also where
"contested" shows). Edge lines use the same spectrum for their Agreement (brighter = stronger
inference). Thick outlines mark node type: **gold = ought**, **medium blue = evidence / external
anchor**. An **ought** is rated on democratic *endorsement*, not truth — its title bar runs dark →
bright **gold** instead of the truth-gray ramp. **Faded, sunk cards are ghosts** (demoted /
superseded items, kept on the map as a record, never deleted). A title-bar **pill** marks a
type-resolution poll ("type under vote" / "re-typed → ought · flip pending") — tallies in Analytics.
Direct edges outcompeted by a **stronger layered path** (geometric-mean strength) are shortcuts:
hidden behind a "+N weaker shortcuts" pill in detail view, faint in the map, and flagged **"in
competition"** on their edge card (Analytics compares the routes side by side). **Rating mode**
(⋯ menu) blinds every consensus cue for independent judgment — datasets that enforce it
(`config.json` `rating_mode_only`) open blind. Cards carry no metadata text — on a focused card, click the **title** for alternate titles
& ratings (on an edge: its inference phrasings), the **body** for alternate phrasings, the bottom
bar's **mean-labelled spread glyph** (band = ±stdev, dots = rating-bloc means; its **lozenge** shows
confidence — **red** = too few ratings, **amber** = marginal, bar-coloured = confident) for full
analytics, and **💬** (grayed = no comments) for the forum. Scroll to the bottom of a focus view, then keep scrolling, to pull back to the
neighborhood (force-layout) view. A collapsible **Key** (bottom-left) explains the encodings; the
`⋯` menu has the fuller color key.

**New here?** Click **Introduction** (topbar, left of the `⋯` menu) for a short guided walkthrough — it
runs on the Debate graph, spotlighting each part of a card and the map in turn, and explains the whole
visual grammar in about two minutes.

The graph is a derived snapshot (`graph.json`) of an append-only rating log; this branch carries snapshots
only, for the UI to render — no rating engine or agent runs here.
