# Grammar pass — integrating §1 (Evidence · Argument · Ought) into the three FLF graphs

*2026-07-17. Applies the merged §1 grammar (evidence/ought kinds, Hume's rule, `flag-type`) to
`covid-graph/`, `blackholes-graph/`, `eggs-graph/`. The headline: these are overwhelmingly empirical
(is/evidence) questions, so the honest integration is small and surgical — and the append-only log
plus Hume's rule mean the remaining ought work is correctly **sequenced behind** the assessment
thread's categorical-consensus poll, not something to force by hand now.*

## What the audit found (every `claim` node reviewed in all three graphs)

| graph | genuine ought / value nodes | action |
|---|---|---|
| **covid** | none — all 37 claim nodes are empirical (origin hypotheses, evidence weight) | no change |
| **black holes** | none — all 29 claim nodes are empirical (physics, safety, evidence) | no change |
| **eggs** | **n063, n064** — a rival *value* pair | flagged as `ought` |

- **n063**: "For most people, eggs' nutritional benefits … outweigh their modest, contested … risk,
  making them a reasonable part of a healthy diet." — a value/endorsement conclusion.
- **n064**: "Given the genuinely unresolved causal question and the … type-2-diabetes subgroup risk,
  a precautionary approach … is warranted for most people." — a prescriptive conclusion.
- The two are already **antithesis set `s9`** (rival oughts — exactly the ought-vs-ought the spec
  anticipated), and both are grounded **by** is-nodes (n058/n059/n031 → n063; n048/n038 → n064).
  That direction is Hume-clean: is-claims may ground an ought.

## Actions taken (eggs only)

- `flag-type --node n063 --as ought` (event `ft1`) and `--node n064 --as ought` (`ft2`).
  This **records** the candidate re-typing; it does not itself change the kind. Resolution is the
  categorical-consensus / democratic-endorsement poll the assessment thread is building.
- `flag-friction` on n063 (`f17`) documenting that n063 **bundles an is-evaluation with an ought**
  and should be decomposed per SPEC §1.3 — with the sequencing caveat below.

covid and black holes were left untouched (0 flag events) — the correct outcome for pure is-questions.

## The load-bearing finding: why we flag now and wire later

The grammar is working *as designed*, and it blocks premature hand-wiring:

1. **Kinds are immutable** in the append-only log — there is no retype verb, and `flag-type` is a
   flag, not a mutation. A node becomes an `ought` only when the poll resolves its flag.
2. **Hume's rule enforces the ordering.** The clean decomposition of n063 wants a value-premise
   ought grounding the ought conclusion. But you cannot draw `ought → n063` while n063 is still typed
   `claim` (Hume rejects an ought grounding a non-ought). So the value-premise oughts can only be
   added and wired **after** n063/n064 are retyped. Adding them now would leave dangling roots.

So the correct integration today is: **flag the oughts** (done) → the assessment thread's poll
retypes them → **then** decompose/wire the value premises and re-rate on *endorsement*. Doing it by
hand now would front-run the consensus-typing mechanism we deliberately built.

## Structural contested signal (live `contested` verb, post-merge engine)

| graph | contested | settled | ghost-eligible |
|---|---|---|---|
| covid | 40 | 195 | 1 |
| black holes | 9 | 60 | — |
| eggs | 18 | 116 | 2 |

(Node+edge verdicts. Keyed off antithesis structure + belief-camps, not raw stdev.)

## Two honest notes (out of scope for this pass, logged for follow-up)

- **eggs is under-quorum on Agreement.** Every eggs node has exactly 4 Agreement ratings; the default
  `quorum` is 5, so `block_for` holds them all at `state="sealed"` (pending) even though they are
  structurally contested. This is a rating-*depth* gap (one more rater crosses quorum), not a grammar
  or merge bug. covid/BH have 20–28 ratings and seal normally.
- **The evidence rename needs no migration.** The three graphs use the legacy `external_anchor` kind;
  the permanent read-alias (`is_evidence_kind`) means they load, rebuild, and group-by-source
  identically. Append-only means the stored kind string never changes — which is what keeps every
  prior snapshot byte-identical.

## Gated on the assessment thread (democratic-endorsement build)

Once the endorsement dimension + type-resolution poll land: resolve `ft1`/`ft2` → n063/n064 become
`ought` → add the value-premise oughts and wire them (Hume-clean, ought→ought) → **re-rate the oughts
on endorsement, not truth** (fixing the category error), with reputation-weighting tapered toward
democratic on value judgments.
