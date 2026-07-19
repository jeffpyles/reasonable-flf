# Swarm test — "Could the LHC create a black hole that destroys Earth?"

*2026-07-02. First multi-agent test (Prototype 2 territory). Question: can **independent AI agents,
working only from the `AGENT-GUIDE`, collectively build a coherent argument graph** from a shared
information base? This is the assumption the whole "point a swarm at it" FLF strategy rests on.
Interactive artifact: "blackholes-swarm-v1". Data + full provenance in this directory.*

## Setup
- 4 Sonnet agents, run **sequentially** (each saw all prior work), with **distinct perspectives**
  for uncorrelated error: `phys-01` (mainstream physicist, laid the skeleton), `skeptic-02`
  (risk-taker, built the minority case), `method-03` (methodologist, audited inference + agreed),
  `synth-04` (synthesizer, closed gaps + coherence pass).
- Shared graph, one CLI, one source pack (`sources/blackholes/`), the standard `AGENT-GUIDE`. No
  human intervention in the building.
- A **different question shape** from eggs on purpose: strong expert consensus with a vocal
  contested edge, vs. eggs' genuine scientific split. Tests generalization (FLF criterion 2).

## Result: independent agents DID build a coherent graph.
23 nodes · 25 grounds · 4 antithesis sets · 2 conjunctions · 24 agree events · **7 frictions** ·
**0 orphans** · **0 duplicates**.

**The disciplines transferred to independent agents from the guide alone** — this is the core
positive result:
- **Search-before-create worked: zero duplicate nodes.** The synthesizer searched ~15 term
  families and found no genuine duplicates; author 2 explicitly *reused* n004/n008/n012/n013 and
  *joined* existing antithesis sets rather than forking them. Duplication was the predicted #1
  failure mode; it did not happen.
- **Support-only held.** All opposition was expressed as rival *positive* claims in antithesis
  sets (s1 top answers; s2 evaporation reliability; s3 capture loophole; s4 the risk-threshold
  ought) — no "not-X" nodes, no negative edges.
- **The is/ought nudge was followed** by two different agents unprompted (skeptic-02: n020 value →
  n021 ought; synth-04: n022 value → n023 ought). The Entry-13 guidance propagated.
- **All four cruxes are legible** as rival positive-claim sets, both top-level positions reachable
  with full evidentiary chains, both sides built fairly (the minority position is steelmanned, not
  strawmanned).

## The money finding: agreement tracked *soundness*, not *side* — with an honest caveat.
Agents cast agrees **selectively** (edges by agree-count: 9 have 0, 9 have 1, 6 have 2, 1 has 3 —
not the flat "everything agreed" pattern of rubber-stamping). And the agreement concentrated on
genuinely sound inferential steps **across ideological lines**:
- The strongest-agreed edges are the mainstream evidential backbone (cosmic-ray → no-risk = 3;
  white-dwarf → no-risk = 2; dense-stars → white-dwarf = 2) **and** a *risk-side* step that is
  simply sound ("Hawking radiation is empirically unconfirmed" → both "non-negligible risk" and
  "safety case stacks two premises", each = 2). Agents endorsed the other side's good steps.
- The contested cruxes stayed at/near zero agreement — "evaporation is reliable enough to trust,"
  "mere production-possibility → risk" (everyone declined this per friction f3). Reviewers who saw
  the cruxes *declined to sign them*, which is the correct behavior.

**Honest caveat (do not over-read the zero-agree edges):** in a *sequential* run, later-created
edges have fewer or no subsequent reviewers, so "0 agrees" conflates *contested* with
*created-late-and-unreviewed*. The synthesizer's own new mainstream-ought edge sits at 0 simply
because no author came after it — not because it's weak. The clean signal is the **reviewed** set:
among edges multiple authors saw, the sound ones drew cross-perspective agreement and the
contested ones were declined. A looping / larger swarm (every node reviewed by someone later) would
remove this confound; it's a limitation of a 4-agent linear run, not of the mechanism.

## Friction convergence — the one real recurring grammar gap
Agents filed 7 frictions. Most restate known items (objection→answer f1; shared-precondition f3).
The important pattern is **convergence**: **f5 (method-03) independently rediscovered, in the
black-hole domain, the same meta-node/reliability distinction we hit with eggs (F5-residual)** — a
node that comments on *another node's evidentiary status* is structurally indistinguishable from a
first-order ground. **f7 (synth-04) then synthesized f4+f5 into a clean statement:** nodes carry a
KIND (claim / external_anchor) but no **grain/level marker** separating object-level claims from
meta-claims about another node. Suggested primitive: a meta-claim kind or a `points-at` field.
- This is now the **single strongest candidate for a real additive grammar primitive** — it
  recurred across two unrelated domains and two independent agents. Still *additive* (a node kind /
  field), not a change to support-only.

## Limitations (named, not hidden)
- **Sequential, not concurrent** (no file-locking yet) — models an async swarm but under-reviews
  late edges (above). Concurrency-safe parallel writes are the prerequisite for a true swarm.
- **Small (4 agents), single domain, one hand-authored source pack** (by Fable) — a real deployment
  ingests sources rather than being handed a curated pack.
- **Collaborative-convergence tested, not independent-reproducibility.** We showed agents build ONE
  coherent graph together; we did NOT test whether two agents *independently* produce *similar*
  graphs of the same question (the other half of Prototype 2). That's the next test.

## Verdict for the FLF story
The scalability bet is looking sound: **independent agents, given only the format's guide, produced
a coherent, non-duplicative, fairly-argued, crux-legible graph of a contested question in a domain
different from the one the format was developed on** — and the structural-consensus signal did real
epistemic work. The one recurring grammar gap (meta/object-level marker) is now well-evidenced and
additive. Both are exactly the kind of result — capability plus a named, bounded limitation — the
competition rewards.
