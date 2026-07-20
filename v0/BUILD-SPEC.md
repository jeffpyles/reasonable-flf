# Reasonable v0 — Build Spec (the contract)

This is the **single source of truth** for the v0 structural-test playground. Three
components are built against it: the **CLI + data layer**, the **HTML viewer**, and the
**agent authoring guide**. They interoperate *only* through the data formats defined here —
so those formats are frozen; everything else is implementation freedom.

Design rationale lives in `../Feature Discussions.md`, Entry 11 ("v0 structural-test spec").
Read that entry for the *why*; this file is the *what*.

---

## 0. What v0 is

A local, no-network, no-accounts playground for building an **argument/evidence graph** of one
contested question (dev question: **"Are eggs good for you?"**). It tests whether the structural
grammar can faithfully capture and convey argument. It has **structural consensus** (agents draw
connections and *Agree* with them; agreement strengthens them) but **no assessment** (no
node-quality ratings, no reputation weighting, no demotion/"sinking").

Everything is **stdlib-only Python** + **one static HTML file**. No pip installs, no servers,
no frameworks, no external calls.

---

## 1. Data model (FROZEN)

Two files under `v0/data/`:

### 1a. `events.jsonl` — append-only log (source of truth)

One JSON object per line. Every mutation is an event. Never rewritten, only appended.

```json
{"seq": 1, "ts": "2026-06-24T18:03:11Z", "agent": "agent-03", "verb": "create_node", "payload": { ... }}
```

- `seq` — monotonically increasing integer, assigned by the CLI.
- `ts` — ISO-8601 UTC (`datetime.now(timezone.utc).isoformat()`).
- `agent` — the acting identity (see §3).
- `verb` + `payload` — one of the write verbs below.

### 1b. `graph.json` — derived snapshot (rebuilt from the log)

Never hand-edited. Rebuilt by folding the event log (`graph.py rebuild`, and after every write).
This is what the viewer reads. Schema:

```json
{
  "meta": {"question": "Are eggs good for you?", "generated_ts": "...", "event_count": 42},
  "nodes": [
    {
      "id": "n001",
      "kind": "claim",                     // "claim" | "external_anchor"
      "primary_phrasing": "p0",            // id of highest-agreed phrasing (ties -> earliest)
      "primary_title": "t0",               // id of highest-agreed title, or null
      "phrasings": [{"id": "p0", "text": "...", "agrees": 3, "agents": ["agent-01", ...]}],
      "titles":    [{"id": "t0", "text": "...", "agrees": 2, "agents": [...]}],
      "source_ref": null,                   // required non-null for kind=="external_anchor"
      "author": "agent-01",
      "created_seq": 1
    }
  ],
  "ground_edges": [
    {"id": "e001", "from": "n002", "to": "n001", "group": "g1",   // group null if independent
     "agrees": 2, "strength": 3, "agents": [...], "author": "agent-02", "created_seq": 5}
  ],
  "conjunction_groups": [
    {"id": "g1", "to": "n001", "members": ["n002", "n003"]}    // members jointly support `to`
  ],
  "antithesis_sets": [
    {"id": "s1",
     "members": [{"node": "n001", "agrees": 4, "belonging": 5, "author": "agent-01"},
                 {"node": "n007", "agrees": 2, "belonging": 3, "author": "agent-03"}]}
  ],
  "frictions": [
    {"id": "f1", "agent": "agent-02", "ts": "...", "refs": ["n004"], "text": "couldn't express ..."}
  ]
}
```

**Strength convention (FROZEN):** `strength = agrees + 1` (the author implicitly counts as one).
`belonging` for antithesis members = `agrees + 1` likewise. Distance in the viewer is `∝ 1/strength`.

**Edge semantics (FROZEN):** a ground edge `{from: X, to: Y}` means **X is a Ground of Y / Y is a
Dependent of X** — support flows `from → to`. "Grounds" and "Dependents" are the same edge seen
from opposite ends; the viewer labels the left side (things that support the focus) *Grounds* and
the right side (things the focus supports) *Dependents*.

**IDs:** CLI-assigned, stable, human-readable: nodes `n001`, edges `e001`, groups `g1`, sets `s1`,
phrasings `p{n}` (per node), titles `t{n}` (per node), frictions `f1`. Zero-padded to 3 for nodes/edges.

---

## 2. CLI verbs (FROZEN interface — `python3 graph.py <verb> [args]`)

All verbs take `--agent <id>` (required for writes) and `--data <dir>` (default `./data`).
Writes append to `events.jsonl` **and** rebuild `graph.json`. All output is text for humans by
default and JSON with `--json` (agents use `--json`).

### Write verbs
- `create-node --text "<claim>" [--kind claim|external_anchor] [--source "<ref>"] [--title "<t>"]`
  → prints new node id. `source` required iff kind=external_anchor. Initial `text` becomes phrasing `p0`.
- `draw-ground --from <node> --to <node> [--group <gid|new>]`
  → creates a ground edge. `--group new` starts a conjunction group; `--group g1` joins an existing one.
- `add-antithesis --node <node> [--set <sid|new>]`
  → adds node to an antithesis set (`--set new` creates one). Membership is agreeable.
- `agree --target <id>` → target may be an edge id, a `set:<sid>:<node>` membership, a
  `title:<node>:<tid>`, or `phrasing:<node>:<pid>`. One agree per agent per target; agreeing your
  own object is rejected.
- `propose-title --node <node> --text "<title>"` → adds a competing title; prints title id.
- `propose-phrasing --node <node> --text "<phrasing>"` → adds a competing phrasing; prints id.
- `flag-friction --text "<what the grammar could not express>" [--refs n001,n004]`
  → appends a falsification-log entry. **First-class verb** — this is the single most valuable output.

### Read verbs (agents MUST use these; write-only would be unusable)
- `get-node <node>` → full node record + its ground edges (both directions), antithesis sets, titles, phrasings.
- `neighborhood --node <node> [--depth 1]` → node + neighbors out to depth N (titles + G/D structure).
- `search "<query>"` → substring/keyword match over node phrasings + titles. **Agents MUST `search`
  before `create-node`** to avoid duplicate claims (the predictable failure mode).
- `list-sets` → all antithesis sets with members.
- `stats` → counts (nodes, edges, sets, agrees, frictions), and simple health signals
  (orphan nodes, self-agree attempts rejected, duplicate-text warnings).
- `rebuild` → regenerate `graph.json` from `events.jsonl` (idempotent; also runs after every write).

### Validation rules enforced at the write boundary (FROZEN)
1. Referenced nodes/edges/sets must exist.
2. `agree`: reject if agent already agreed that target; reject if agent is the object's author.
3. `external_anchor` nodes require a non-empty `source`.
4. No node may be its own Ground (`from == to` rejected). **Cycles across multiple nodes ARE allowed**
   (they're intentionally visible in the graph — see Entry 11); only 1-cycles are rejected.
5. Claim text length: soft cap **350 chars**, configurable via `--max-claim-chars`; over-cap is a
   **warning, not an error** (it's a grain signal we want to observe, not block).

---

## 3. Identity & determinism

- Agents pass `--agent agent-NN`. The CLI trusts it (no auth in v0).
- The log is the truth; `graph.json` is a pure function of it. `rebuild` must be **deterministic**
  and idempotent: same log → same snapshot, byte-for-byte (sort keys, stable ordering by `seq`).
- No wall-clock in the rebuild logic except copying `ts` values already in the log.

---

## 4. Component requirements

### 4a. CLI + data layer (`v0/graph.py`, optional `v0/reasonable/` module, `v0/tests/`)
- Stdlib only. Python 3.11+. `python3 graph.py --help` documents every verb.
- Fold logic and validation live in an importable module so tests hit functions directly.
- `v0/tests/` uses stdlib `unittest`. Cover: fold correctness, each validation rule, self-agree
  rejection, duplicate-text warning, cycle allowed / 1-cycle rejected, strength math, determinism
  of rebuild. Provide `python3 -m unittest discover v0/tests`.
- Include a `seed_demo.py` or `make-demo` that lays down ~8–12 nodes so the viewer has something to
  show — but keep demo content clearly trivial/placeholder (NOT a real egg analysis; the real
  hand-seed is a separate human step).

### 4b. Viewer (`v0/viewer.html`) — single self-contained file
- Vanilla JS, no build step, no CDN. Loads `data/graph.json` (via `fetch` when served, with a
  documented `file://` fallback: a `?data=` paste box or an embedded-JSON option, since `fetch` of
  local files is blocked under `file://`). Must work when opened directly in a browser.
- **Match the repo aesthetic** (see `../Reasonable - Editor.html`): dark bg `#0f1216`, panel
  `#161b22`, ink `#e8e6e1`, gold accent `#c9a227`, serif body font.
- **Node-view:** focus node as a centered card showing its primary phrasing; **Grounds arrayed to
  the left, Dependents to the right**, each as a small title card; **Antitheses as an arc of title
  cards above** the focus node, ordered by belonging-strength (weakest low-left → strongest
  high-right). Conjunction groups visibly bracketed (joint supporters tied together). Clicking any
  neighbor re-centers on it.
- **Neighborhood-view:** a zoomed-out map of titles + G/D edges only (NO antitheses), for "follow
  one line of reasoning." Toggle between the two views.
- **strength → proximity (FROZEN rule):** line length / neighbor distance `∝ 1/strength`; also
  reflect strength as line thickness. Do NOT implement a force simulation; deterministic placement
  (e.g. radial by 1/strength around the focus) is correct and sufficient for v0.
- Node quality color is **post-v0** — do not invent a quality color cue. Strength is shown by
  proximity + thickness only. Show friction flags somewhere unobtrusive (a count / panel).

### 4c. Agent authoring guide (`v0/AGENT-GUIDE.md`) — a prompt deliverable, not code
- The operating manual a Sonnet/Haiku agent reads before building the graph via the CLI. Written to
  be pasted into a subagent's context. Must cover:
  - The mental model: nodes = truth-apt propositions; Grounds/Dependents = support; Antitheses =
    sets of rival claims; support-only (no negative claims — express opposition as a rival positive
    claim + antithesis membership). Include the **"Not-X" diagnosis/triage** (AGENT-GUIDE §2): the
    recurring urge to write a negation is not a rule gap — route it five ways (competing answer →
    rival node; weak premise → low rating on claim/edge/ground; specific undercutter → positive node
    at the joint; X false → settled-low ghost + `comment`; pure opposition → your low rating), noting
    an absence-claim is still a legitimate positive node. Build-swarm and rater prompt templates
    should carry the condensed one-liner so agents route at generation time instead of stalling on
    `flag-friction`.
  - The **norm discipline**: propositions not questions; `search` before `create`; **Agree only what
    you would have drawn independently** (explicitly warn against rubber-stamp/sycophantic agreement —
    the consensus signal is worthless if everything gets agreed); split/merge by drawing competing
    paths, not by deleting.
  - **`flag-friction` is a duty, not a failure**: whenever the grammar can't cleanly express
    something, file it. This is a primary deliverable.
  - A concrete worked mini-example (2–3 CLI calls with expected output) on a throwaway topic.
  - Sourcing: author from the curated `v0/sources/<question>/` pack, not live web; every
    `external_anchor` node cites a pack item. Include the source-pack file format (a simple JSON or
    markdown index of `{ref_id, citation, url, one-line-claim}`), and a small starter for eggs with
    2–3 genuinely well-known landmark references **clearly marked "VERIFY before use"** (do not
    fabricate specific findings/statistics).

---

## 5. Non-goals (do NOT build in v0)
Ratings (Reasonableness/Clarity), reputation-weighted agreement, demotion/sinking, threaded
comments, depth tiers, force-directed physics, the wider zoom ladder, accounts, networking,
databases. If tempted, add a line to a `FUTURE.md` note instead.

---

## Amendments

The sections above are the frozen v0 contract as originally written and are left unedited above;
changes since are recorded here instead.

- **v0.1 (2026-07-04):** `--data` is now REQUIRED on all verbs (was: default `./data`) — rationale:
  multi-agent runs wrote to the wrong graph when the flag was forgotten. File locking added for
  concurrent writers (see §3 note).
