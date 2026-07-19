# Build your own graph — the end-to-end recipe

*How to take a disputed question from a pile of prose to a built, structure-checked, blind-rated
Reasonable graph, using only this repository and stdlib Python 3. This is not a hypothetical
workflow: it is the pipeline we ran to produce the four case graphs, and each step below points at
the committed artifact where we did it. The authoring manual with full verb reference and norms is
[`v0/AGENT-GUIDE.md`](v0/AGENT-GUIDE.md); this document is the map of the whole journey.*

Everything runs from `v0/` with no installs:

```bash
cd v0
python3 graph.py --help
```

A note on who does the typing: we drove every step below with teams of AI agents (the harness
scripts referenced in steps 4 and 6 are the actual drivers we used), but nothing requires that —
every step is a sequence of ordinary CLI calls a human, a script, or an agent can make.

## 1. Frame the question

Start from **one disputed question** that decomposes into checkable parts — "where did SARS-CoV-2
come from?", not "is science trustworthy?". Create a directory for the new graph and give it a
`config.json`:

```json
{
  "question": "Your disputed question, stated neutrally.",
  "phase2": { "confirm": 8 }
}
```

That's the whole setup — the first write verb creates `events.jsonl` and everything else. `confirm`
is the ratings-per-item bar for "covered" (8 is what our split-half reliability measurement
supports; see [`MECHANISMS.md`](MECHANISMS.md) §7). Leave `rating_mode_only` out for now — it comes
in at step 6.

## 2. Assemble a source pack

Before building, **freeze the raw material**: gather the substance of *every* serious side into a
source pack — quoted excerpts with stable reference ids, or a prose brief that states each side's
case at full strength. Builders then work from the pack and never browse live. Two reasons: the
build becomes reproducible (same pack in, comparable graph out), and every `evidence` node can cite
a `ref_id` a reader can check.

What ours looked like:

- [`v0/elicit-harness/SOURCE-BRIEF-debate.md`](v0/elicit-harness/SOURCE-BRIEF-debate.md) — a prose
  brief: both sides of the debate question in flowing paragraphs, deliberately unstructured, with
  the named-entity framing left in so the build has to abstract it (step 3).
- [`v0/blackholes-graph/harness/sources.json`](v0/blackholes-graph/harness/sources.json) — an
  excerpt pack: per-source quoted passages with ids, which `evidence` nodes then cite via
  `--source`.
- The sourcing norms — pack-only, no live browsing, one study id per source — are
  [`v0/AGENT-GUIDE.md`](v0/AGENT-GUIDE.md) §6.

## 3. Extract claims

Turn the pack into candidate **atomic claims**. The standard that survived our structure passes
(stated in full in
[`v0/debate-graph-v2/README-STRUCTURE-PASS.md`](v0/debate-graph-v2/README-STRUCTURE-PASS.md)):

- **One proposition per node.** Every "X, so Y" bundle splits into two nodes; the "so" lives on the
  edge between them.
- **Self-contained and abstract.** Each claim must read on its own to someone who knows nothing of
  the surrounding dispute — no named critics, no "this platform", no assumed context.
- **Typed at the boundary.** A fact imported from a source is an `evidence` node and must cite it
  (`--source`). A value or action claim ("…is warranted", "…should be avoided") is an `ought`,
  rated later on *endorsement*, never truth. Everything else is a `claim`. Mixed "eggs are bad"
  statements decompose into the is-claim plus the ought that rests on it.
- **Disagreement is a rival claim, never a negation.** Don't extract "not-X"; extract the actual
  competing position the other side holds.

## 4. Build the structure

Build with the CLI verbs, a few rules deep in muscle memory (full reference and a worked example:
[`v0/AGENT-GUIDE.md`](v0/AGENT-GUIDE.md) §4–§5):

```bash
# search before every create — the claim may already exist
python3 graph.py search "lockdowns economy" --data my-graph --json

python3 graph.py create-node --text "..." --agent builder-01 --data my-graph --json
python3 graph.py create-node --text "..." --kind evidence --source "ref:smith2020" \
    --agent builder-01 --data my-graph --json

# FROM supports TO; attach each ground to its most *proximate* claim, not the big conclusion
python3 graph.py draw-ground --from n002 --to n001 --agent builder-01 --data my-graph --json

# rivals: the other serious answers to the same question, in one antithesis set
python3 graph.py add-antithesis --node n003 --set new --agent builder-01 --data my-graph --json
python3 graph.py add-antithesis --node n004 --set s1  --agent builder-01 --data my-graph --json
```

The write boundary enforces the grammar as you go: Hume's rule (an ought may not ground a
non-ought), sources required on evidence, no self-grounding, soft length caps. When the grammar
can't express something you need, log it with `flag-friction` rather than forcing it — that verb is
how the format itself improves.

For a fully automated build, the committed drivers are
[`v0/blackholes-graph/harness/workflow_build.js`](v0/blackholes-graph/harness/workflow_build.js)
(agent swarm → verbs) and [`v0/elicit-harness/elicit_build.js`](v0/elicit-harness/elicit_build.js)
(one-shot build from the prose brief, used to test how well the standard transfers).

## 5. Check the argumentative structure

Before any rating, run the structural pass we ran on every graph:

```bash
python3 graph.py lint  --data my-graph --json
python3 graph.py stats --data my-graph --json
```

`lint` flags hub nodes (too many grounds hung directly on one conclusion — layer them), malformed
antithesis sets, orphans, question-shaped and negation-framed nodes, and redundant
direct-vs-layered paths. **Not every finding is a mechanical fix** — our triage of a real lint run,
finding by finding, is [`v0/LINT-REVIEW.md`](v0/LINT-REVIEW.md): genuine slips get demoted with
`supersede` (never deleted), redundant paths go to raters to adjudicate, hubs go back to the
builder to layer. The companion audit for is/ought typing — checking every claim node for a value
claim hiding as a fact — is [`v0/GRAMMAR-PASS.md`](v0/GRAMMAR-PASS.md). And the deepest version of
this step, a full rebuild of a graph to the structural standard with every deviation documented, is
[`v0/debate-graph-v2/README-STRUCTURE-PASS.md`](v0/debate-graph-v2/README-STRUCTURE-PASS.md) with
its reproducible [`build.py`](v0/debate-graph-v2/build.py).

## 6. Run raters over it

Rating is **blind, by a deliberately diverse panel**. Set it in config so the tool layer enforces
it — while rating, no consensus, no other ratings, no authorship is visible:

```json
{ "rating_mode_only": true }
```

Each rater gets a packet containing the *structure* (claims, edges, rivals) and nothing else, and
rates independently:

```bash
# Agreement on a node or edge
python3 graph.py rate --target n003 --dim A --value 3.5 --agent rater-epistemic-1 \
    --bloc epistemic --data my-graph --json
python3 graph.py rate --target e007 --dim A --value 4.0 --agent rater-epistemic-1 \
    --bloc epistemic --data my-graph --json

# Reasonableness / Clarity on a phrasing
python3 graph.py rate --target phrasing:n003:p0 --dim R --value 4.5 \
    --agent rater-epistemic-1 --bloc epistemic --data my-graph --json
```

What we actually ran, committed in [`v0/debate-graph-v2/harness/`](v0/debate-graph-v2/harness/):
the blind packet ([`packet-blind.md`](v0/debate-graph-v2/harness/packet-blind.md)), a panel of
distinct rater personas (different priors and lenses, tagged via `--bloc` so camp analysis can see
them), and the driver ([`workflow_rate.js`](v0/debate-graph-v2/harness/workflow_rate.js)). Aim for
at least `confirm` ratings per item (8, per the measured reliability bar). If you also want
reputation and calibration to engage — not just raw aggregation — include some **anchor** items
whose answers are independently established; the contract is
[`v0/ASSESSMENT-SPEC.md`](v0/ASSESSMENT-SPEC.md) and the anchor-budget reasoning is
[`v0/ORACLE-BUDGET-POLICY.md`](v0/ORACLE-BUDGET-POLICY.md). (With no anchors, or anchors that
don't span the scale, bias-correction deliberately declines to fire.)

Then read the results the way we did:

```bash
python3 graph.py assess    --data my-graph --json   # the assessed verdicts
python3 graph.py contested --data my-graph --json   # settled vs genuinely contested, and why
python3 graph.py compare --a n001 --b n003 --data my-graph --json  # two rivals, from common ground
```

## 7. Verify and share

```bash
python3 graph.py rebuild --data my-graph   # same log + config -> byte-identical graph.json
```

The directory — `events.jsonl`, `config.json`, `graph.json` — is the entire artifact. Open it in
the viewer (serve `v0/` over http and load `viewer.html?data=my-graph/graph.json`), hand it to
someone else to extend by appending, or re-run assessment over the same log
under your own configuration. The append-only log is what makes all of this compounding: nothing
you built locks anyone else out of re-checking it.

---

*Terms: [`GLOSSARY.md`](GLOSSARY.md) · reading the result: [`HOW-TO-READ-A-GRAPH.md`](HOW-TO-READ-A-GRAPH.md)
· why the assessment works this way: [`MECHANISMS.md`](MECHANISMS.md) ·
what it's all for: [`VISION.md`](VISION.md).*
