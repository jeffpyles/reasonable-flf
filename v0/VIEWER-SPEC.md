# The Viewer — what it is, and how to make it clearer

*A working doc for the viewer/UI of the **Reasonable** argument-mapping project. Scope: presentation and
intelligibility only — how the graph is drawn and read. (Assessment/reputation machinery lives in the
separate reputation-lab branch.)*

---

## 1. Project context (one paragraph)

**Reasonable** is "Wikipedia for arguments": a web app for collective truth-finding by *argument mapping*.
A contested question is decomposed into atomic, truth-apt **claims** placed on a 2-D **graph**, connected
by typed relations. The premise: language is linear because time is, but ideas branch — so faithfully
mapping reasoning needs a 2-D medium, not prose. The **viewer** is the window into that graph. It has to
make a large, multi-relation, community-assessed structure *legible at a glance and navigable in depth* —
which is the whole UI problem.

## 2. What the viewer renders (the frozen grammar)

- **Nodes** — claims (truth-apt propositions). Two kinds: `claim` and `external_anchor` (a pointer to a
  source: "the study found X").
- **Directed support edges** — **Grounds → Dependents** (X justifies Y). Seen from both ends.
- **Antithesis sets** — rings of *rival positive claims* (not negations): competing answers to the same
  point.
- **Conjunction groups** — grounds that support a dependent only *jointly* (drawn as a joined bracket).
- Each node carries **phrasings** (alternative wordings) and **titles** (short labels); a "primary" of
  each is shown.

## 3. Current visual language (as built — `viewer.html`)

**Two views, joined by zoom:**
- **Focus view** (click a node): the node centered, its **Grounds to the left**, **Dependents to the
  right**, and its **antithesis set stacked vertically through it** — rivals ordered by their own
  community-Agreement strength, stronger rivals above (strongest at top), weaker below, so the focus
  card sits at its own rank in the column (clicking a rival re-sorts the column around it). A dashed
  spine + "strongest ↑ · weakest ↓" label mark the set.
- **Neighborhood view** (zoom out): a spring-layout force graph — organic clustering by structural
  strength, for orienting in the larger map. **Layout is self-assembly, permanently** (Feature
  Discussions #33): the craft is the energy function — depth-seeded starts, forward-flow bias,
  strength-proportional straightening, ghost/shortcut spring-releases — so the lowest-energy state
  settles into the logically clear one. Never columns. Two further energy rules (Feature Discussions
  #34) keep it legible as graphs branch: **component banding** (each unconnected sub-graph seeds into
  its own horizontal band so they don't intertwine) and **wormhole springs** (antithesis rivals, which
  share no ground edge, attract to ~one card-width apart, so the two sides of a debate settle facing
  each other at the seam — nearness of space = nearness of logical relation). A further rule (#35)
  keeps edges readable: **node-off-edge clearing** pushes unrelated nodes off any edge line they'd sit
  on, so edges thread through gaps and stay straight instead of reading as false connections; the edge
  router complements it by anchoring its curve along the edge to clear the few remaining obstacles
  without wider swoops. **Density-adaptive spread** (#36) scales node repulsion with graph size, so a
  dense graph (Covid) gets the whitespace its edges need to route while a small one (Debate) stays
  compact — the same energy function, tuned by how crowded the graph is.

**The assessment encoding (one spectrum, three zones — 2026-07 redesign, iterated):**
- Every cue shares **one dark-gray (bad) → bright-white (good) spectrum**; the *trait* is told by
  **which zone of the card** carries it, spatially co-located with what it rates (thin black rules
  separate adjacent zones so close shades never blend):
  - **Title bar** (top) = **Agreement** with the claim (the brief statement being agreed/disagreed with).
  - **Body** = the **leading phrasing's combined Reasonableness & Clarity** (the text that is
    reasonable & clear, or not).
  - **Bottom bar** = **rating consensus** (Agreement stdev: bright = tight, dark = contentious/split).
    This is where **contested** shows — no dashed cue, no state text on the card. Non-focus cards
    collapse body/bottom to slim colour-only strips beside the title.
- **Cards carry no metadata text** (iteration 2): kind labels, score lines, R&C numbers, state text,
  author/created are all gone from cards — the main view stays clean; everything is preserved and
  expanded in the pop-up panels (analytics = state/n/era/blocs/author/kind/history; phrasings = per-
  wording R/C + belonging; titles popdown = per-title ratings).
- **Node type is a thick outline colour** (10px, matching the slim strips, so it registers even at
  neighborhood-view zoom): bright **gold = ought**, medium **blue = evidence** — which IS the
  grammar's `external_anchor` (one concept; `kind:"evidence"` also honored). Both are live in
  debate-graph.
- **Ought endorsement cue** (HANDOFF §2.1): an ought is rated on **democratic endorsement, not
  truth**, so its title bar colours on a **dark → bright-gold ramp** (same brightness semantics,
  unmistakably not the truth-gray ramp); its glyph tooltip and analytics section say "Endorsement —
  democratic, not truth".
- **Ghosts** (HANDOFF §2.2): a node/edge/antithesis-set carrying a `demoted` marker renders **faded,
  grayscaled and sunk below the living layer** (still hoverable/clickable — kept, never deleted),
  loses its spring pull in the force layout, its edges draw faint, and a demoted set drops its
  column from the living detail view (a muted note + Analytics provenance replace it). Antithesis
  *losers* are NOT ghosts — only an explicit `demoted` marker ghosts anything (minority-truth
  protection). `ghost_eligible` (the auto signal) lives in the `ghosts` read verb, not the
  snapshot — see the checklist.
- A **nonlinear color ramp** (`emphasisT`, knee at 3): scores ≤3 are compressed into the bottom
  ~15% of the ramp and 3–5 gets the rest — so the band that matters (good-but-differ) is actually
  distinguishable. (The consensus ramp is linear in stdev over 0–2 instead.) The legend's spectrum
  bar is a score *ruler* sampled from the live ramp every 0.25, so position s on the bar is exactly
  the colour a card scoring s gets.
- **Edges carry the same spectrum**: line **brightness** = graded Agreement mean of the inference,
  **thickness/closeness** = strength (falls back to structural strength when unrated); the conjunction
  bracket colours the same way from the group's joint-inference Agreement. Edge midpoint labels show
  the typing text only (no comment chips — comments live on the edge focus card).
- **Detail-view interactions on the focus card**: click the **title bar** → popdown of alternate titles
  with ratings (best cumulative first); click the **body** → panel of alternate phrasings & their R/C +
  belonging ratings; the **bottom bar** carries the **spread glyph, labelled with the mean**,
  dead-centered on the card (click → full analytics panel: state, n, an explicit stdev row, blocs,
  divergence, author, history), with the **💬 icon** anchored right (no count; grayed when the forum
  is empty; click → forum, Reddit-style nested threads). The glyph's axis is **plain linear 0–5**
  (only the colour ramps are nonlinear). The glyph always draws in the standard zone ink and sits on
  a **confidence lozenge** — a snug pill edged with the same thin black rule as the zone separators,
  whose body is **red** below the engine's quorum (n < 5), **amber** below its confirm threshold
  (n < 10), and the bottom bar's own colour (border only) once confident — this replaces all
  "(provisional)" text. The lozenge tracks **sample size only** (fixed 2026-07-18: it briefly also
  fired amber on the `provisional` lifecycle state, which mislabelled well-sampled n=20 aggregates —
  convergence lifecycle belongs to the consensus bar and Analytics, not the sample-confidence pill).
- The **edge focus card**: title bar = the **strongest suggested inference phrasing** (typing; falls
  back to the edge id — *no bundled edge carries typings yet*), coloured by the edge's conditional
  Agreement, click → **inference-phrasings panel**; body = an empty slim bar that colours by the top
  phrasing's own ratings (*dormant: typings carry no rating aggregates yet*); bottom bar = same
  labelled glyph + comment icon as nodes. Structural agrees/strength moved to the analytics panel.
- Unrated dimensions stay at the uncoloured default (per-zone).
- A **⋯ menu** carries the color key and options; there's a **chain-strength** affordance.
- A **persistent legend** (bottom-left, collapsible, both views): the shared spectrum bar, a mini
  three-zone card, ought/evidence outline swatches, edge brightness/thickness cues, and a worked
  sample of the spread glyph. Complements (doesn't replace) the menu's fuller key.
- **Scroll vs. zoom-out**: in detail view, wheel-down scrolls while the stage still has content below
  (tall antithesis columns / ground stacks; an invisible spacer keeps a little empty room under the
  lowest card); only at the bottom does a further wheel-down (2 notches) pull back to the
  neighborhood view.

**Loading:** `viewer.html?data=<url>` fetches a `graph.json`; with no server (opened directly) it falls
back to an **embedded** graph. This branch ships `data/eggs-p4.json` (79 nodes) embedded as the default,
plus `data/eggs-p3.json` and `data/eggs-p6.json`.

## 4. Open questions & ideas — clarity and intelligibility

*Roughly ordered from most-specced/actionable to most-open.*

1. **Distribution, not just the mean** *(BUILT, in the honest-to-the-data variant).* The card shows
   `mean ±stdev`, but that still hides the difference between a *tight consensus*, a *wide-uncertain*
   spread, and a *bimodal / contested* split — three different epistemic states. **As built:** a
   **spread glyph** in the focus card's bottom (analytics) bar (±stdev band + per-bloc mean dots +
   overall-mean tick — the three states read as narrow band / wide band with merged dots / two
   separated dots), grayed below 5 raters, with **click-through to the analytics panel**
   (per-dimension strip, bloc breakdown, bloc divergence, history). **DATA GAP / dormant:** a true
   *histogram* is not derivable from current snapshots — aggregates carry only `mean/stdev/n` +
   per-bloc `mean/n` + `bloc_divergence`, no per-rating list. The viewer already renders real bars
   automatically wherever an aggregate carries `histogram: [c0..ck]` (bins spanning 0–5); the rating
   engine just needs to export binned counts into the snapshot.
2. **Surface the full assessment grid** *(UI built; DATA GAP).* **As built:** clicking the focus
   card's title bar lists alternate titles with ratings; clicking its body lists alternate phrasings
   with their R/C means and belonging-agrees. Both rank by *cumulative rating* with automatic
   fallback to structural `agrees`. **DATA GAP:** no bundled snapshot carries title A/R/C aggregates,
   graded belonging Agreement, or graded comment ratings — the ranking/labels upgrade automatically
   when the engine exports them. The "spin this phrasing off into its own node" nudge is still open.
3. **A persistent legend.** *(BUILT, core part.)* **As built:** a small always-visible, collapsible
   legend (bottom-left, both views) teaching the one-spectrum/three-zones system: spectrum bar
   (computed from the live ramp, so the sub-3.5 compression is honestly visible), mini zone card,
   ought-outline swatch, edge cues, and a worked sample of the spread glyph. **Still open:**
   **redundant encoding** (a shape/label/icon, not color alone) for colorblind-safety and
   accessibility — the single-spectrum redesign helps (it's a pure lightness ramp, robust to most
   color-vision differences), but n/confidence still has no non-numeric cue.
4. **Does the multi-cue read hold up?** *(REDESIGNED 2026-07 — re-test.)* The old frame=gold/body=white
   two-channel split is replaced by one dark→white spectrum across three card zones (title=Agreement,
   body=phrasing R&C, bottom=consensus). Adjacent same-spectrum zones give relative comparison for
   free; worth user-testing the new read, and whether confidence/`n` deserves its own subtle encoding
   (e.g., border weight or opacity) rather than only a number.
5. **Visualization at scale.** The focus/neighborhood metaphor is lovely for tens–hundreds of nodes. Does
   it survive thousands→millions? Likely it becomes a **queryable store that renders local subgraphs on
   demand** rather than one big canvas — a core open design question (how to preserve spatial intuition
   while only ever drawing a neighborhood).
6. **Chain traversal & chain-strength.** Focus shows depth-1. How does a reader *walk a chain* of support,
   see where it's strong or weak, and read the chain-strength product legibly without getting lost?
7. **Antithesis & conjunction legibility.** *(Partially addressed 2026-07:)* rivals now stack in a
   vertical column through the focus, physically ordered by Agreement strength with a labelled dashed
   spine — visibly different geometry from the AND-bracket. Still worth first-timer testing that
   "these compete" vs "these only count together" reads immediately.
8. **Onboarding the grammar.** *(SHIPPED 2026-07-18 — the **Introduction** button, topbar, left of the
   ⋯ menu.)* An 11-step guided walkthrough runs on a live graph (Debate — its top-level split *"A
   faithful map adds value"* vs *"Mapping won't improve debate"* packs the whole vocabulary into one
   focus view: grounds left, a gold **ought** dependent right, a rival stacked vertically). A dimming
   overlay with a moving spotlight lifts the element under discussion; a callout explains it; the tour
   drives the viewer through real states (three zones → node types → grounds/dependents/rivals →
   click-throughs → the self-assembling map → the ⋯ menu). Each node step **centres the focus card**
   and the reader can **scroll** (wheel) with the spotlight tracking, so nothing clips on a short
   screen. It loads the Debate demo itself so it works from any starting graph. Deterministic,
   keyboard-navigable (←/→/Esc), pure DOM (no data mutated). *Remaining, if wanted: an even lighter
   hover-explainer for repeat visits, and first-timer testing of claim vs support vs antithesis vs
   conjunction specifically.*
   - **Rating mode is hidden for the submission** (`SHOW_RATING_MODE = false`): no human-rating
     machinery exists yet and blind assessment isn't part of the presentation, so the viewer stays in
     **Reading mode** — the ⋯-menu toggle and topbar pill are suppressed and a dataset's
     `rating_mode_only` flag no longer opens blind. The whole §2.5 feature is intact behind the flag;
     flip it back to `true` to restore it.
9. **Comment/discussion density.** Comment bubbles show counts; how to invite reading the discussion
   thread without cluttering the map.
10. **Low-confidence / few-ratings cues.** Convey "barely rated / low confidence" vs "settled" visually,
    not just via `n=` — ties into (1) and (4).
11. **Touch, mobile, accessibility.** Keyboard navigation, screen-reader structure, contrast, and a
    workable focus/zoom model on small touch screens.

## 5. Merge-back checklist — RECONCILED 2026-07-17 (viewer thread rejoined main)

The viewer branch now sits on main with shared history; this checklist is reconciled against the
data layer as of the rejoin (see `HANDOFF-TO-UI.md`, which is the ACTIVE ROADMAP for the next
viewer iterations — its Part 2 supersedes the older open questions below where they overlap):

1. **Ought nodes** — LIVE in the grammar (`kind:"ought"`; debate-graph carries two, and the eggs
   type polls have resolved two more). The viewer's gold outline lights up, and the **endorsement
   cue is BUILT** (HANDOFF §2.1): ought title bars colour on the dark→gold endorsement ramp, with
   matching glyph-tooltip and analytics wording.
2. **Evidence nodes** — RESOLVED, inverted from the earlier guess: `evidence` is the real kind and
   `external_anchor` is kept as a read alias. The viewer's dual-kind blue outline already renders
   both spellings correctly; no change needed.
3. **Histograms** — SHIPPED by Assessment (PR #39): every rated aggregate carries
   `histogram: [c0..c5]` — 6 integer bins, `histogram[i]` = count of current-era ratings rounding
   half-up to value i (unweighted raw distribution; absent when unrated). The viewer renders
   value-CENTERED bars (centers at i·5/(k−1), half-step edges, so it generalizes unchanged to
   half-point bins) with the reputation-weighted mean tick riding over the raw counts — the
   weighted-vs-raw contrast is deliberate and legible. 6 integer bins kept: raw ratings are
   integers, so finer bins would only interleave zeros.
4. **Title ratings** — still pending (no title A/R/C in any snapshot); `agrees` fallback active.
5. **Typing ratings** — partially live: covid-graph has edges with typings (the edge card's
   typing title bar lights up there); rating aggregates on typings still pending.
6. **Graded belonging + comment ratings** — still pending; `byCumulativeThenAgrees` fallback active.
7. **Render asks from HANDOFF-TO-UI Part 2** (rough priority):
   ~~endorsement cue for Ought (§2.1)~~ **BUILT** → ~~ghost rendering (§2.2)~~ **BUILT for
   `demoted` markers** (grayed/sunk/spring-released; demoted sets drop their column; antithesis
   losers are never ghosted; eggs-graph's demoted set `s2` is the live test case). `ghost_eligible`
   export SHIPPED by Graphs (conditional per-target flag on nodes/edges, same rule as the `ghosts`
   verb): the viewer now ghosts anything carrying EITHER `demoted` or `ghost_eligible`, with
   provenance wording per flavour (authored demotion vs the automatic rule) →
   ~~type-poll affordance (§2.6)~~ **BUILT**: a title-bar pill ("type under vote" while open,
   "re-typed → kind · flip pending" when resolved with `reopen_required`; nothing once the flip
   completes — the kind itself changes), with tallies in Analytics (decline first-class, weighted
   yes-share) and current-kind rendering preserved until the era turns; eggs-graph's n063/n064 are
   the live pending-flip cases →
   ~~normalized-strength layout/declutter (§2.3)~~ **BUILT (declutter core)**: the viewer computes
   redundant shortcuts client-side (a direct edge outcompeted by a layered path's geometric-mean
   strength, depth ≤4) — hidden behind a "+N weaker shortcuts" pill in detail view, drawn faint in
   the map, and spring-released in the force layout so layering shapes clusters (the anti-flatness
   rule; answers §4 item 6's "read chain strength legibly" in part). Conjunction-group members are
   never hidden (the AND bracket stays whole). Full `chain`-verb parity (per-path products,
   weakest-link, compare-to-ancestor walks) is still open → ~~competitive edge comparison
   (§2.4)~~ **BUILT (read-side)**: a redundant edge's Analytics carries an "In competition —
   direct vs layered" section (this edge vs each hop of the stronger path, hop rows click through
   to their edges, geometric-mean footer) and the edge card wears an "in competition" pill;
   collecting comparative edge-Agreement *ratings* in that context awaits the write surface →
   ~~blind rating mode (§2.5)~~ **BUILT**: an interactive Reading↔Rating toggle (⋯ menu, topbar
   "RATING MODE" pill) blinds every consensus cue — zone colours, spread glyphs/lozenges, scores,
   aggregate panels, comment threads (count only), rating columns in the title/phrasing/typing
   lists, Agreement-driven edge brightness/thickness/proximity, and the consensus-ordered
   antithesis column (structural belonging order instead). Structure, texts, kinds, ghosts and
   type polls (governance, not score consensus) stay visible. A dataset whose sibling
   `config.json` sets `rating_mode_only: true` (all four bundled graphs) **opens blind**
   automatically; the toggle stays available since the viewer is the sanctioned human read
   surface. The interactive write side (rating from the viewer) remains future work. (The
   `settled` state renders sanely today: confident lozenge.) Graphs to render against:
   `eggs-graph/`, `covid-graph/`, `blackholes-graph/`, `debate-graph/` (each has a `graph.json`).

## 6. Where to start

Open `viewer.html` directly (renders the embedded eggs-p4 graph), or serve the folder and try
`viewer.html?data=debate-graph/graph.json` — the first dataset with real `evidence`/`ought` kinds —
or `?data=eggs-graph/graph.json` (type polls + a demoted set). `README-viewer.md` has the specifics.
The next build targets are the HANDOFF-TO-UI Part 2 items listed in §5.7 above; §4 item 5
(visualization at scale) remains the big open design question.
