# Agent Authoring Guide — Reasonable v0

You are about to build part of an **argument/evidence graph** for one contested question, using
the `graph.py` CLI. This guide is everything you need: the mental model, the rules, the full
verb reference, and a worked example. Read it fully before your first write.

You are not writing an essay. You are adding **structure**: nodes, support edges, and rival-claim
sets, that a later reader (human or agent, who did not build it) can navigate and trust. The whole
point of this prototype is to test whether that structure can be trusted — so precision and
restraint matter more than volume.

---

## 1. The mental model

**A node is a truth-apt proposition — a statement that could be true or false, supported or
contested.** Not a topic, not a question. "Egg yolks raise LDL cholesterol in most adults" is a
node. "Are eggs bad for you?" is not — it's the implicit question the graph as a whole answers;
it never becomes a node itself. **A question-shaped node is malformed**: it can't be a Ground or a
Dependent of anything (support doesn't flow into or out of a question), so it will sit with no
clean edges — it *strands*. If you catch yourself writing a claim that ends in "?" or starts with
"whether," rephrase it as the assertion you actually mean, or split it into the candidate
answers (each one its own node).

**Grounds / Dependents are one directed support edge, seen from both ends.** If node X supports
node Y, X is a Ground of Y, and Y is a Dependent of X. `draw-ground --from X --to Y` always means
support flows `X → Y`, i.e. **X is evidence/reason for Y**, never the reverse. Get the direction
backwards and you've asserted the opposite of what you meant.

**Conjunction is a grouping tag on Ground edges, not a separate relation.** Use it when two or
more grounds only support the dependent *jointly* — neither one means much alone. Example: "the
study had n>10,000" and "the study controlled for smoking and exercise" only jointly support "the
study's null result on eggs and CVD is credible"; each is close to meaningless in isolation. Draw
both edges with the same `--group` id. Grounds that each independently support the same node stay
in separate groups (or ungrouped) — don't over-group; conjunction asserts a specific logical
dependency, not just topical proximity.

**Antitheses are sets of rival positive claims**, not negations. There is no "not-X" node type.
When you want to express opposition to a claim, you do not create "X is false" — you create the
*actual competing positive claim* ("dietary cholesterol has negligible effect on serum LDL for
most people" as a rival to "dietary cholesterol meaningfully raises serum LDL for most people")
and add it to the same antithesis set. **This is the single most important discipline in v0:
support-only.** If you find yourself wanting to write a claim whose entire content is "the other
claim is wrong," stop — find the positive claim that *is* the disagreement, and antithesis-link it
instead. If you genuinely can't find a positive rephrasing, that's a `flag-friction` case (§4), not
a reason to bend the rule.

A node can belong to more than one antithesis set. Sets are typically small (rival positions on
one specific sub-question) — don't dump every tangentially-related claim into one giant set.

**Is/ought nudge.** When a node prescribes an action (an "ought"/"should"), state its underlying
VALUE premise as an explicit Ground (e.g. "avoiding cheap risks is worthwhile"). Oughts are
welcome nodes, but an ought resting only on empirical grounds hides a value premise; make it
explicit or expect it to be contested. This is guidance, not an enforced rule.

---

## 2. The norm discipline — rules, not suggestions

**1. Propositions, not questions.** Every node text must be a declarative claim someone could
agree or disagree with. Before you `create-node`, read your own draft text back and ask "could
this be true or false?" If the honest answer is "it depends what you mean by the question," you
haven't found the claim yet — decompose further.

**2. ALWAYS `search` before `create-node`.** Duplicate claims are the single most common and most
damaging failure mode in a multi-agent graph: they split agreement that should have accumulated
on one node, and they make the graph look denser than it actually is. Before creating any node,
run `search` with a few keyword variants of what you're about to write. If something close
already exists, either reuse it, `agree` its phrasing, or `propose-phrasing` a better wording of
the *existing* node — don't create a near-duplicate.

**3. Agree only what you would have independently drawn.** `agree` is a real epistemic signal:
it says "if this edge/title/phrasing didn't exist, I would have proposed it myself." **Do not
rubber-stamp.** Do not agree with something merely because it's plausible, already there, or
proposed by an agent you trust. If everything gets agreed, the agreement count stops meaning
anything — the entire structural-consensus mechanism this prototype is testing collapses into
noise. **Declining to agree is the normal, correct, expected outcome for most things you read.**
When you read a node or edge and are unconvinced, indifferent, or only partly persuaded, simply
move on — do not agree "to be supportive" and do not create a token dissenting node either;
absence of your agreement already carries information.

**4. Split and merge by drawing *competing* paths — never by deleting.** You cannot delete or
edit another agent's node or edge; the log is append-only by design (§1a of BUILD-SPEC). If a
node is too coarse, don't try to fix it in place — create the finer-grained nodes and route
grounds through them as an alternative path to the same dependent; if the finer path is better,
it will accumulate agreement and naturally outweigh the coarse one. If two nodes should be one,
create the merged/consolidated phrasing as a new node (or `propose-phrasing` on the stronger of
the two) and let agreement sort out which survives. The graph is allowed to hold competing
parallel decompositions at once — that coexistence is itself a signal the prototype is measuring,
not a bug to clean up.

---

## 3. `flag-friction` is a duty, not a failure

If the grammar (propositions + Grounds/Dependents + Conjunction + Antitheses) cannot cleanly
express something you're trying to say, **do not force it into the nearest-fitting relation and
move on.** File it:

```
python3 graph.py flag-friction --agent <you> --text "<what you couldn't express>" [--refs n001,n004] --data <dir> --json
```

This is not an admission that you failed — **it is one of the two or three most valuable things
you can produce in this session.** v0 exists to find out whether four relations are *sufficient*
for real argument (BUILD-SPEC §0, Feature Discussions Entry 7's "relational sufficiency"
criterion). Every clean edge you draw tests the grammar by *use*; every friction you flag tests it
by *failure*, and failures are the informative half of that experiment. A session that ends with
zero friction flags is more likely to mean you quietly bent the grammar than that you never hit an
edge case — real contested questions have edge cases.

Concretely, flag friction when you hit things like:
- A relationship that's clearly *not* independent-or-joint support and *not* rivalry — e.g. "this
  meta-claim is about the reliability of that source," or "this reframes the question rather than
  answering it."
- A claim that resists decomposition without feeling arbitrary, or that seems to need to go one
  level *finer* than the grain the graph is currently using.
- A case where the positive-rephrasing trick for opposition (§1) feels forced or loses the actual
  point being made.
- Any point where you had to choose arbitrarily between two structurally different ways to encode
  the same idea (e.g., new node vs. phrasing; new antithesis set vs. adding to an existing one)
  and you're not confident the choice was principled.

Write the friction text as the *specific thing that didn't fit*, not a vague complaint — future
readers of the falsification log need to be able to act on it.

---

## 4. CLI reference

All commands: `python3 graph.py <verb> [args] --agent <id> --data <dir>`. `--agent` is required
for every write verb; `--data` is **required on every call, read or write** — there is no
default, so name your graph explicitly every time (e.g. `--data v0/data`). Omitting it is an
argparse error, not a silent fallback to some other graph. Every write appends to `events.jsonl`
and rebuilds `graph.json`. Pass `--json` on every call — you are a machine reader, use the machine
format.

**Output envelope (parse this, not the prose):** every **write** verb prints
`{"id": "<new-or-target-id>", "ok": true, "warnings": [...]}` on success — `id` is the created
node/edge/set/title/phrasing/friction id (or, for `agree`, the target you agreed). A rejected
write prints `{"ok": false, ...}` with a reason and exits non-zero; a warning (e.g. over-cap,
duplicate-text) still succeeds with `ok: true` and the note in `warnings`. **Read** verbs print
their payload alongside `"ok": true` — `search` → `{"hits": [...], "ok": true}`; `get-node` →
`{"grounds": [...], "dependents": [...], "antithesis_sets": [...], ...}`; `stats` →
`{"counts": {...}, "health": {...}, "ok": true}`. Always check `ok` before trusting a result.

### Read verbs — use these constantly, before and between writes

- `get-node <node> --data <dir> --json`
  Full record for one node: its text/phrasings, titles, every Ground edge in and out, every
  antithesis set it belongs to.
- `neighborhood --node <node> [--depth 1] --data <dir> --json`
  The node plus neighbors out to depth N — titles and Grounds/Dependents structure only (no
  antitheses). Use this to get oriented in a region before adding to it.
- `search "<query>" --data <dir> --json`
  Substring/keyword match over node phrasings and titles. **Mandatory before every
  `create-node`** (Rule 2, §2).
- `list-sets --data <dir> --json`
  Every antithesis set and its members. Check this before `add-antithesis --set new` — you may
  be about to fork a set that already exists.
- `list-studies --data <dir> --json`
  Every distinct source cited by an `evidence` node (either the `evidence` kind or the legacy
  `external_anchor` name), grouped: the source id, its citation (resolved from the pack when the id
  matches a `ref_id`, otherwise the raw source string), and every node id citing it. Run this before
  adding a new `evidence` node to find an existing study id rather than starting a new one (§6).
- `stats --data <dir> --json`
  Graph-wide counts and health signals: nodes, edges, sets, agrees, frictions, orphan nodes,
  rejected self-agree attempts, duplicate-text warnings. Worth a glance at the start and end of a
  session.
- `lint --data <dir> [--hub-threshold N] --json`
  Deterministic structural-coherence pass (SPEC §4): flags star/hub nodes (too many direct grounds —
  attach more proximately), orphans, malformed antithesis sets (a 1-member set is a slip), question-
  shaped nodes, negation-framed ("No X…") claims, and redundant direct-vs-layered paths (§3.3). Run it
  before you close a build round and fix what it surfaces. Advisory — it never mutates.
- `ghosts --data <dir> [--ghost-floor F] --json`
  Lists ghost candidates (SPEC §3.1/§3.2): `ghost_eligible` — targets refuted on their OWN Agreement
  (low, settled, and not an antithesis rival) — plus `demoted` — targets a `supersede` explicitly
  moved toward ghost status. A rival that merely lost its antithesis stack is *not* a ghost (less
  supported ≠ wrong).
- `polls --data <dir> --json` / `poll-vote --node <n> --question type:<ought|evidence> --value <yes|no|decline> --agent <id> --data <dir> --json`
  The categorical **type poll** (SPEC §2.2): `flag-type` opens it, `poll-vote` casts Yes/No/decline,
  `polls` shows tallies + the reputation-weighted resolution. A resolved Yes re-types the node.
- `decompose --data <dir> --json`
  Lists **decomposition candidates** (SPEC §2.3): type polls that met quorum but stayed *split* — a
  persistent type contestation that usually means an **is/ought conflation**. The fix is to split the
  node into its is-claim + a separate ought grounded on the is plus an explicit value premise (§1.3).
- `rebuild --data <dir>`
  Regenerate `graph.json` from the event log. Runs automatically after every write; you rarely
  need to call it directly.

### Write verbs

- `create-node --text "<claim>" [--kind claim|evidence|ought] [--source "<ref>"] [--title "<t>"] --agent <id> --data <dir> --json`
  Prints the new node id. Three node **kinds** name a node's boundary role:
  - `claim` (default) — an **Argument**: internal reasoning, rated on truth/support.
  - `evidence` — a **fact imported from a source** ("this study found X"); `--source` is required.
    That's how the graph touches reality outside itself; cite it from your
    `sources/<question>/index.json` pack (§6). (`external_anchor` is the legacy name, still accepted.)
  - `ought` — an **action/value** ("you should avoid eggs"), rated on *endorsement*, not truth.
    Keep it atomic: an is/ought bundle ("eggs are bad") should be *split* into the is-claim plus a
    separate ought grounded on it and an explicit value premise (see the is/ought nudge above).
  The `--text` you give becomes the node's first phrasing (`p0`).
- `draw-ground --from <node> --to <node> [--group <gid|new>] --agent <id> --data <dir> --json`
  Creates a Ground edge: `--from` supports `--to`. Omit `--group` for an independent ground.
  `--group new` starts a conjunction group (this ground only supports `--to` jointly with others
  you'll add to the same group); `--group g1` joins an existing group.
  **Hume's rule (enforced):** an `ought` may not be a Ground of a non-`ought` — you cannot derive an
  "is" from an "ought" (ought→ought is fine). Grounding *into* an `evidence` node is discouraged
  (a warning): evidence is anchored by its source, not by in-graph reasoning.
  **Proximate-attachment discipline (SPEC §4):** for each ground, ask "does this support THIS node, or
  more precisely one of its *existing grounds*?" Attach to the most proximate claim, creating the
  intermediate if it's missing — don't hang every reason directly off the salient hub. A top answer
  accumulating 10+ direct grounds is the star-topology smell the `lint` verb flags; prefer a layered
  tree. (The `strength` layout rewards layering via length-normalized chain strength, so flat hubs
  also read as weaker.)
- `flag-type --node <node> --as <ought|evidence> --agent <id> --data <dir> --json`
  Flags a node as a candidate Ought/Evidence when its current kind looks wrong. This **opens a
  categorical type poll** (§2.2) that the crowd resolves with `poll-vote`; a persistently-split poll is
  surfaced by `decompose` as an is/ought-conflation candidate (§2.3). Use it to mark type mismatches
  you notice rather than silently leaving them.
- `supersede --target <node|edge|set> [--reason "<why>"] [--restore] --agent <id> --data <dir> --json`
  Demotes a node, edge, or antithesis set toward **ghost** status (SPEC §3.2) — **never a delete**. The
  target and its history all stay in the graph; it just gains a `demoted` marker (greyed / sunk in the
  viewer, and skipped by `lint`). Use it to retire a refuted claim, the weaker of two redundant edges,
  or a malformed/spurious antithesis set while preserving the record that it was checked. `--restore`
  un-demotes. Prefer this over trying to remove anything — the grammar has no delete, by design.
- `add-antithesis --node <node> [--set <sid|new>] --agent <id> --data <dir> --json`
  Adds `<node>` as a member of an antithesis set. `--set new` creates a set with this node as its
  first member; `--set s1` adds it to an existing set (check `list-sets` first — you may want to
  join an existing rivalry rather than start a parallel one).
- `agree --target <id> --agent <id> --data <dir> --json`
  `<id>` may be an edge id (`e007`), a set membership (`set:s1:n004`), a title
  (`title:n004:t1`), or a phrasing (`phrasing:n004:p1`). One agree per agent per target; the CLI
  rejects agreeing with your own authored object. Read Rule 3 (§2) before every `agree` call.
- `propose-title --node <node> --text "<title>" --agent <id> --data <dir> --json`
  Adds a competing short title for a node; prints the title id. Titles are what render on
  margin/arc cards when the node isn't the focus — write for scannability, not completeness.
- `propose-phrasing --node <node> --text "<phrasing>" --agent <id> --data <dir> --json`
  Adds a competing wording of the same claim; prints the phrasing id. Use this instead of a new
  node when the *proposition* is the same and only the wording could be better.
- `flag-friction --text "<what the grammar could not express>" [--refs n001,n004] --agent <id> --data <dir> --json`
  See §3. First-class verb, not an error path.

### Validation you will hit (enforced at the write boundary — know these before you're surprised by a rejection)

1. Every node/edge/set you reference must already exist.
2. `agree` rejects a second agree by the same agent on the same target, and rejects agreeing with
   your own authored object.
3. `external_anchor` nodes must carry a non-empty `--source`.
4. A node cannot Ground itself (`--from X --to X` rejected). Multi-node cycles are **allowed and
   intentional** — the graph is allowed to show that A grounds B grounds C grounds A; that's a
   real signal about the argument, not a bug to route around.
5. Claim text has a soft cap (~350 chars, see `--max-claim-chars`); going over is a **warning**,
   not a rejection — it's a grain signal being observed, not a rule being enforced. Don't fight
   the cap by cramming a compound claim into one node just to dodge the warning; if a claim
   naturally wants to be long, let it warn, and consider whether it should decompose instead.

---

## 5. Worked example (throwaway topic — do not reuse this topic for a real session)

Topic: **"Is a hot dog a sandwich?"** Two agents, `agent-01` and `agent-02`. This walks the full
loop: search → create → draw-ground → add-antithesis → agree → flag-friction. The outputs below
are the **actual** `--json` shapes the CLI emits (see the output envelope in §4).

**1. Search first, always.**
```
python3 graph.py search "hot dog sandwich" --data <dir> --json
```
```json
{"hits": [], "ok": true}
```
Nothing exists yet — clear to create.

**2. Create the claim node (agent-01).**
```
python3 graph.py create-node --agent agent-01 --data <dir> \
  --text "A hot dog is a sandwich, because a sandwich is any filling enclosed by bread." \
  --title "Hot dog = sandwich (functional definition)" --json
```
```json
{"id": "n001", "ok": true, "warnings": []}
```

**3. Create a ground for it, and check for a duplicate first.**
```
python3 graph.py search "bread filling definition" --data <dir> --json
```
```json
{"hits": [], "ok": true}
```
```
python3 graph.py create-node --agent agent-01 --data <dir> \
  --text "The standard culinary definition of a sandwich is any dish of filling enclosed by or between bread." \
  --title "Standard sandwich definition" --json
```
```json
{"id": "n002", "ok": true, "warnings": []}
```
```
python3 graph.py draw-ground --from n002 --to n001 --agent agent-01 --data <dir> --json
```
```json
{"id": "e001", "ok": true, "warnings": []}
```
n002 (the definition) is a Ground of n001 (the conclusion) — support flows toward the claim being
argued. (Confirm the direction and see the edge's current `strength` any time with
`get-node n001 --json`.)

**4. Draw a rival positive claim into an antithesis (agent-02) — not a negation.**
```
python3 graph.py search "hot dog not sandwich bun" --data <dir> --json
```
```json
{"hits": [], "ok": true}
```
```
python3 graph.py create-node --agent agent-02 --data <dir> \
  --text "A hot dog is a distinct, hinged-bun category that culinary tradition treats as separate from sandwiches." \
  --title "Hot dog is its own category" --json
```
```json
{"id": "n003", "ok": true, "warnings": []}
```
```
python3 graph.py add-antithesis --node n003 --set new --agent agent-02 --data <dir> --json
```
```json
{"id": "s1", "ok": true, "warnings": []}
```
```
python3 graph.py add-antithesis --node n001 --set s1 --agent agent-02 --data <dir> --json
```
```json
{"id": "s1", "ok": true, "warnings": []}
```
Note n003 was written as a positive claim ("is its own category"), not as "a hot dog is NOT a
sandwich" — that's the support-only discipline (§1) in practice. (`list-sets --json` now shows s1
with both members and their belonging-strengths.)

**5. Agree — but only because agent-02 actually buys it.**
```
python3 graph.py agree --target e001 --agent agent-02 --data <dir> --json
```
```json
{"id": "e001", "ok": true, "warnings": []}
```
agent-02 independently finds the definitional ground convincing, so agrees (the edge's `strength`
is now 2 — confirm with `get-node`). agent-02 does *not* agree with n001 itself (the top-level
claim) — being convinced by one ground doesn't mean buying the conclusion; that's a distinct
judgment. (Note: agent-02 could not have agreed its *own* objects — the CLI rejects self-agree.)

**6. Flag friction on something the grammar didn't handle cleanly.**
```
python3 graph.py flag-friction --agent agent-02 --data <dir> \
  --text "Both sides in set s1 depend on which of two competing DEFINITIONS of 'sandwich' you adopt, not on a further fact about hot dogs. The grammar has no way to mark that this is a definitional/framing fork rather than an evidential disagreement — antithesis membership reads the same either way." \
  --refs n001,n003 --json
```
```json
{"id": "f1", "ok": true, "warnings": []}
```

---

## 6. Sourcing: use the source pack, don't browse live

You author from the curated pack at `v0/sources/<question>/index.json` — not from live web
search (v0 is explicitly no-network). Format: a JSON array of objects:

```json
{"ref_id": "eggs-001", "citation": "<full citation>", "url": "<link>",
 "claim_summary": "<general topic/claim area this source addresses>",
 "status": "VERIFY_BEFORE_USE"}
```

See `v0/sources/eggs/index.json` for the eggs starter pack. Every entry there is marked
`VERIFY_BEFORE_USE` and deliberately gives only the *general area* a source addresses, not
specific numbers or findings — those were not fabricated and you should not invent them either.
**An `external_anchor`'s `--source` SHOULD cite a pack `ref_id`** when one exists, and you must
not assert a specific statistic or effect size that isn't actually in the pack's `claim_summary`
or your own verified knowledge — when in doubt, write the claim at the level of generality the
pack supports, or `flag-friction` that the pack needs a more specific source added. If the pack
has no matching entry for what you're citing, `--source` MAY be a short free-text source string
instead — but if you do this, treat it as unverified and consider whether the pack should be
expanded with a proper entry rather than leaving it as a one-off string.

**Study grouping: reuse one `--source` id per study.** Multiple findings drawn from the *same*
study should cite the *same* `--source` id, not a fresh string per finding — that's what lets
`list-studies` (§4) show they're one study and lets the whole study later be re-weighted together.
Before adding a new `external_anchor`, run `list-studies --json` to check whether the study
already has a source id in the graph; reuse it rather than fragmenting one study across several
source strings.

---

## 7. Why these norms matter: mapping to the test criteria

v0 is judging the *grammar*, not you, against four criteria (Feature Discussions, Entry 7) — every
rule above exists to keep your session from contaminating that measurement:

- **Decomposability** — can a messy question break into atomic propositions without feeling
  arbitrary? Every duplicate you avoid (Rule 2) and every awkward decomposition you flag (§3)
  directly tests this. A graph full of near-duplicate nodes hides the real answer to this
  question behind noise.
- **Relational sufficiency** — do Grounds/Dependents + Conjunction + Antitheses cover real
  argument? This is what `flag-friction` measures directly. It is not possible to over-report
  friction; it is very possible to under-report it by silently forcing awkward relationships into
  the nearest-fitting verb.
- **Faithfulness** — does the graph capture the full territory at least as well as good prose,
  not just more "legible"-looking? Precise Ground direction, correctly-scoped Conjunction groups,
  and genuine (not rubber-stamped, Rule 3) agreement are what make the graph's structure actually
  *mean* what it looks like it means, rather than being a plausible-looking shape with no real
  content behind it.
- **Legibility** — can a reader who didn't build the graph navigate and trust it? Titles that are
  scannable, phrasings that are genuine propositions (Rule 1), and antithesis sets that show real
  rivals rather than loosely-related nodes are what make the graph readable by someone standing
  outside your session.

Everything you flag goes into the **falsification log** (the `frictions` list in `graph.json`) —
the project's term for the running record of every place the grammar didn't hold up. It is read
alongside `stats` (orphan nodes, duplicate-text warnings, self-agree rejections) as the primary
output of this whole exercise. Treat your session as an experiment on the grammar, not just a
content-production task — the friction flags and the honest agreement counts are worth as much as
the nodes themselves.

---

## 8. Forums & inference-typing (FORUMS-SPEC.md)

Alongside nodes/edges, every node and edge has a **comment forum**, and every edge additionally has
a **typing vote**: a running answer to "what inference is this edge making?" Both are read/write via
`comment`, `list-comments`, and `propose-typing` — see `graph.py --help` for full flag reference; all
three take `--agent`/`--data`/`--json` like every other verb.

**What forums are for.** A forum is the **incubation layer** — the place a reliability concern, a
sourcing question, or "I'm not sure this edge means what it looks like it means" gets said *before*
it either resolves as a non-issue or earns enough weight to change the graph itself. It is not a
second, looser grammar for making claims. If you catch yourself writing a comment that is really a
new proposition someone could agree or disagree with, you're describing a node, not commenting on
one.

**Rule 1 — graduate, don't let it rot in the thread.** The moment a comment starts *bearing
epistemic weight* — it's making a substantive claim the graph doesn't yet contain, not just flagging
a question or a doubt — graduate it: `create-node` the claim (and `draw-ground`/`add-antithesis` it
into the structure it belongs in), then reference that node back from the comment (e.g. a reply
noting "see n014") so the thread and the graph stay linked. A forum that accumulates real arguments
which never make it into structure is the graph quietly losing the thing it exists to capture.

**Rule 2 — typing discipline: search before you free-text.** Before `propose-typing`, run
`list-comments --target <edge>` (has someone already proposed one worth agreeing with instead?) and
`search` the graph for an existing trunk node that already says what this edge's inference amounts
to. Prefer `--node <trunk-id>` — a reference to a real claim already in the graph — over `--label`;
a label is a placeholder for when no trunk node exists yet, not a shortcut to avoid finding one. The
graduation path for a `--label` typing is exactly Rule 1: once the underlying claim becomes worth
stating as its own node, create it and `propose-typing --node` the new reference — the old label
typing is left in place (append-only), and agreement will naturally accrue to whichever is better.

**Rule 3 — agree under the same discipline as everything else.** Agreeing with a comment or a
typing is the same real epistemic signal as agreeing with an edge or a title: it means "I would have
said this independently," not "this is plausible" or "someone I trust wrote it." **Declining to
agree is normal and expected** — most comments you read won't be ones you'd have written yourself,
and most typings won't be the one you'd have proposed. Do not rubber-stamp a typing just because it's
the only one on an edge, and do not agree with a comment just to be encouraging. The one-agree-per-
agent and no-self-agree rules apply identically here (you cannot agree with your own comment or your
own typing).

---

## 9. Rating (ASSESSMENT-SPEC.md)

Alongside structural `agree`, you can also `rate` a phrasing or comment on **Reasonableness** and
**Clarity** (`--dim R` / `--dim C`, 0.0–5.0 or `--value abstain`), and a node or edge on
**Agreement** (`--dim A`): `python3 graph.py rate --target <…> --dim <R|C|A> --value <0-5|abstain>
--agent <you> --data <dir> --json`.

**You always rate blind (Rating mode is enforced).** On these prototype graphs the dataset is in
enforced Rating mode (`config.json` `rating_mode_only: true`), so **every** `get-node` /
`neighborhood` / `list-comments` read is automatically blinded — you cannot see any existing consensus
cue (the `agreement`/`quality` aggregates, R/C/A score means, the comment thread, or rating-heat),
whether or not you pass `--rating-mode`. The claim text, titles, and Ground/Dependent structure you
need to judge are still shown; only the "how others rated it" signal is withheld. This is deliberate
and not optional (ASSESSMENT-SPEC §7): forming your Agreement *before* seeing where the crowd landed
is the whole point — the running mean and prior comments anchor you, and a rating that just echoes the
consensus carries no new information. Rate from your own judgment; don't try to fetch ratings by other
means. Same discipline as `agree` (§2 rule 3) — a rating is a real
judgment, not encouragement; abstain freely rather than guessing at a value you don't actually
have an opinion on, and revisit a target and re-rate if your judgment changes (a later rating from
you supersedes your earlier one). Default to the scale midpoint when genuinely uncertain, reserve
the extremes (0 or 5) for cases you'd defend, and self-rating your own authored
node/edge/phrasing/comment is rejected, same as self-agree.

**Edge Agreement is CONDITIONAL — rate only the inference, never the premise.** An edge's A answers
exactly one question: *"IF the Ground were so, how strongly would it support this Dependent?"* You
GRANT the Ground for the duration of the judgment. Whether the Ground is actually true is a
different rating that lives on the Ground node itself — do not let doubt about the premise leak
into the edge, and do not let a rock-solid premise inflate a leaky inference. The two failure
modes this separates:
- **Weak ground, sound step:** a dubious claim whose Dependent nonetheless follows cleanly from it
  → LOW node-A on the Ground, HIGH edge-A.
- **Sound ground, overclaiming Dependent:** a well-established claim whose Dependent as phrased
  goes further than the claim licenses → HIGH node-A on the Ground, LOW edge-A (the overreach IS
  the inference failure).

**Edge A measures degree of support, not entailment.** Most healthy support is partial — that is
why conjunctions and multiple Grounds exist — so do not punish an edge for not single-handedly
proving its Dependent. Anchors: **5** ≈ granting the Ground would compel or near-compel the
Dependent; **3** ≈ real but partial support, one good reason among several needed; **1** ≈ even
granting it, it barely bears on the Dependent.

**External anchors split across the node and the edge:** the anchor node asserts "the source
says/found X," so its node-A is *fidelity* (does the source really say that?). The source's
*reliability* — methodology, power, bias — belongs in the EDGE leaving it, because the step from
"the study found X" to "X is so" is exactly where study quality does its work.

**Conjunction groups:** a joint Ground's member edge has no independent inference to rate — the
member alone is not claimed to support anything. Abstain on member edges of a conjunction; the
rateable inference is the GROUP's ("if ALL members were so…"), and a group-level rating target is
planned (until it exists, put group-level judgments in a comment on one member edge).
