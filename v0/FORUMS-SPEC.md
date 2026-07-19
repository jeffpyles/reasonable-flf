# Forums & Inference-Typing — build spec (extends BUILD-SPEC.md; core schema unchanged)

*Design settled in Feature Discussions Entries 17 + addendum (2026-07-04). This is an ADDITIVE
extension: nothing in the frozen BUILD-SPEC core changes; new event verbs and new snapshot fields
only. Builder: read BUILD-SPEC.md first, then this.*

## Why (one paragraph)
Comment forums are the **incubation layer**: where reliability concerns surface before graduating
into graph structure (Entry 17 Case 1 — "comments incubate, the graph adjudicates"), where an
edge's *inference* is discussed and typed (Case 3 — "the edge IS the inference"), and where the
reassessment trigger will later live. Edge forums + the typing vote close the last meta-claim
residual (Entry 17 addendum) with zero grammar change.

## 1. New events (append-only, same envelope as BUILD-SPEC §1a)

- `comment` — payload: `{target, text, parent}` where `target` is a node id (`n007`), an edge id
  (`e012`), or (for replies) omitted in favor of `parent` = an existing comment id. Comment ids:
  `c001, c002…` (global, CLI-assigned).
- `propose_typing` — payload: `{edge, node?, label?}`: a candidate answer to "what inference is
  this edge making?" Must supply `--node <trunk-node-id>` (preferred: a reference to an existing
  node in THIS graph, e.g. an epistemology/trunk claim) **or** `--label "<free text>"` (when no
  trunk node exists yet — the graduation path is to later create the node and propose a typing
  that references it). Typing ids: `ty1, ty2…` per edge.
- `agree` — targets extended: `comment:<cid>` and `typing:<edge>:<tyid>`. All existing rules hold
  (one agree per agent per target; no self-agree).

## 2. Snapshot additions (graph.json)

- Every node AND edge record gains `"comments": [{id, parent, agent, ts, text, agrees, agents}]`
  (flat list; thread structure recoverable via `parent`; order by seq).
- Every edge gains `"typings": [{id, node, label, agrees, agents, author}]` and
  `"primary_typing": "<tyid>|null"` — primary = most agrees, tie → earliest (same convention as
  titles/phrasings). Exactly one of `node`/`label` is non-null per typing.
- `meta` gains `"comment_count"`.
- Rebuild stays a pure, deterministic fold. No wall-clock.

## 3. CLI verbs

- `comment --target <node|edge> --text "..." [--reply-to <cid>] --agent <id> --data <dir> [--json]`
  → `{"id":"c00N","ok":true,...}`. `--reply-to` and `--target` are mutually exclusive (a reply
  inherits its parent's target).
- `list-comments --target <node|edge> --data <dir> [--json]` → the target's thread, each comment
  with agrees; default text mode renders indented threading, ranked siblings by (agrees desc, seq
  asc).
- `propose-typing --edge <eid> (--node <nid> | --label "...") --agent <id> --data <dir> [--json]`
- `get-node` / `neighborhood` outputs: include `comment_count` per node/edge and `primary_typing`
  (resolved to the trunk node's title or the label text) per edge.
- Validation: target must exist; reply parent must exist; typing's `--node` must reference an
  existing node; comment text non-empty (soft cap 2000 chars, warning not error).

## 4. Viewer (single-file constraint unchanged)

- **Node view:** each Ground/Dependent edge line gets a small **typing label** at its midpoint —
  the primary typing's text (trunk-node title or label), rendered in the small UI font, clickable:
  if the typing references a node, clicking **re-centers on that trunk node** (the wormhole).
  No label when an edge has no typings. NEVER draw a line from the label to anywhere — the
  reference is data, not geometry (Entry 17 addendum: no lines-to-lines).
- **Forum affordance:** focus card and each edge label get a small comment-count chip (e.g. "💬 3";
  omit when zero). Clicking opens a right-side **forum panel** (same visual family as the friction
  panel): threaded comments, siblings ranked by agrees desc, reply indentation, the target's
  typings listed at top (for edges) with agree counts, primary starred.
- **Neighborhood view:** NO typing labels, NO comment chips (keep the map clean). Nothing changes.
- Panel is read-only in the viewer (writing happens via CLI); keep it that way for now.

## 5. Explicitly OUT of scope
Reasonableness/Clarity rating of comments (assessment layer); auto-coupling edge strength to a
typing's trunk-node standing (Entry 17: label informs raters, never auto-discounts); reassessment
markers; any change to the core grammar, fold determinism, or locking (a parallel task hardens
store.py — coordinate by building on its committed result, or if it hasn't landed, keep your
changes inside the existing append+rebuild pipeline so the merge is trivial).

## 6. Tests (stdlib unittest, extend v0/tests/)
Comment on node / on edge / reply threading; agree-on-comment ranking; self-agree rejected;
typing with --node and with --label; primary-typing tie-break; validation failures (missing
target, bad parent, bad node ref); determinism of rebuild with forums present; existing suite
still green.

## 7. Agent guide additions (AGENT-GUIDE.md)
Short section: forums are for *discussion about* nodes/edges — meta-observations, source-quality
concerns, "what inference is this edge making?" proposals. **Rules:** (1) a comment that starts
bearing epistemic weight must GRADUATE into the graph (create the node/rival path; link it from
the comment); (2) typing an edge: `search`/`list-comments` first, reference an existing trunk node
where one exists, `--label` otherwise; (3) agree with comments/typings under the same
independent-endorsement discipline as everything else — declining is normal.
