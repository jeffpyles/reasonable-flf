# Design spec — Evidence · Argument · Ought, competitive edges, and the ghost state

*Status: **PROPOSAL / DRAFT** (not yet implemented). Captures the design converged on in discussion
2026-07-17. Supersedes nothing yet; when accepted, amends `AGENT-GUIDE.md`, `PHASE2-SPEC.md`
(lifecycle), `ASSESSMENT-SPEC.md` (dimensions), and the grammar in `reasonable/validate.py` /
`reasonable/ops.py` / `graph.py`. §2 is the part to hand to the **Assessment-layer thread** — it has
a hard dependency on that thread's current settled-vs-contested reliability work (flagged inline).*

---

## 0. Through-lines (the principles this all serves)

- **The graph has three boundary roles, not one.** Evidence anchors reasoning to the world at the
  *start* (facts in); Argument is the internal reasoning; **Ought** anchors reasoning to the world at
  the *end* (actions/values out). Evidence↔Ought is a deliberate symmetry — and it extends to
  *weighting*: **Evidence (facts in) is maximally anchor/reputation-weighted; Ought (values out) is
  minimally so** (endorsement is near-democratic, never weighted by truth-competence — §2.1).
- **Prefer elicited explicit signals over inferred or absence-of-signal.** (Recurs across the project:
  BTS/meta-prediction; "ask meta-uncertainty directly, don't infer from dispersion"; the explicit
  "No" in typing polls below.)
- **Preserve, don't delete.** A reasoning graph that forgets what it disproved will relitigate it.
  Refuted material is demoted to a *ghost*, never removed — the record of "we checked this, it's
  wrong" is a primary asset.
- **Comparison/structure beats absolute spread.** Comparative judgments are more reliable than
  absolute ones; structural disagreement (antithesis, competing edges) is more reliable than
  statistical dispersion. (Direct consequence of the dispersion-reliability finding — see
  `FINDINGS-SYNTHESIS.md` §12 and `dispersion-regimes/`.)

---

## 1. Grammar — the Evidence · Argument · Ought node types

> **STATUS: §1 IMPLEMENTED (2026-07-17).** `evidence`/`ought` kinds added with an
> `external_anchor`→evidence read alias (all three graphs rebuild byte-identically); Hume's rule
> enforced in `draw-ground` (Evidence-leaf is a warning); `flag-type` verb records a typing flag but
> folds to nothing (its poll is §2). Kind constants + helpers live in `reasonable/fold.py`. 212 tests
> green. Remaining sub-items below (is/ought auto-split, poll resolution) are §2 / Assessment-thread.

### 1.1 Rename: External Anchor → **Evidence**
Names the *role*, not the mechanism, and makes the Evidence–Argument–Ought spine legible. Node
`kind` value `external_anchor` → `evidence`. Covers study findings, authoritative statements,
definitions, and data — anything grounding the argument from outside it. (Mechanical rename; keep a
read alias for old logs during migration.)

### 1.2 The three node types and their boundary rules
| type | role | grounded by | may ground | rated on (see §2) |
|---|---|---|---|---|
| **Evidence** | fact imported from outside | its **source** (leaf on the grounding side; not by argument nodes) | Arguments, Oughts | **reliability / fidelity** |
| **Argument** (`claim`) | internal reasoning | other nodes | Arguments, Oughts | **truth / support** |
| **Ought** | action/value exported to the world | Arguments and other Oughts | **only other Oughts** | **endorsement** |

### 1.3 The rules the types *enforce* (this is where a type earns its keep vs. a mere tag)
- **Hume's rule (structural):** an **Ought may not be a Ground of an Argument or Evidence node** — you
  cannot derive an "is" from an "ought." An Ought may ground another Ought (instrumental chains). This
  makes a whole class of smuggled-value-premise errors impossible by construction. `draw-ground`
  rejects (or friction-flags) an Ought→is edge.
- **Evidence leaf rule:** an Evidence node is grounded by its `source`, not by in-graph nodes (mirror
  image of Ought's terminal-dependent property).
- **Is/ought decomposition:** a node that is *both* descriptive and prescriptive ("eggs are bad for
  you" = "eggs raise CVD risk" [is] + "you should avoid eggs" [ought]) is malformed and should be
  **split**, the ought grounded on the is plus an explicit value premise. Ties to the existing
  atomicity discipline; see §2.3 for how type-contestation routes here.

### 1.4 New/changed verbs (grammar surface)
- `flag-type --node <n> --as <ought|evidence>` — opens a categorical-consensus poll (§2.2). Does not
  itself change the type.
- Typing resolves by crowd ratio, not author fiat (§2.2).
- `draw-ground` gains the Hume check.
- (See §3 for `supersede`/demote — **not** a delete verb.)

---

## 2. Assessment — rating dimensions, categorical polls, competitive comparison

> **STATUS (2026-07-17): RESOLVED with the Assessment thread** (their reply, folded in here; the
> conversation is archived). The blocking dependency is gone — the shared contestedness service
> (`reasonable/contested.py` `assess_contestedness` / `graph.py contested`: `contested`/`settled`/
> `ghost_eligible`, off structural + belief-camp signals, not raw stdev) is the single implementation
> §2.2 routing and §3.1 both build on. The Ought→democratic-aggregation call below is **shipped**
> (`assess.py` ought branch; ASSESSMENT-SPEC §3–§4 amendments).

### 2.1 Three rating dimensions
Agreement is not one question. By node type:
- **Evidence → fidelity (node) + reliability (outgoing edge) — two parts, kept separate.** The Evidence
  node's own Agreement rates **fidelity**: "does the cited source actually say this?" The **source's
  reliability** (methodology, power, bias) rides the **edge leaving the Evidence node** — "from 'the
  study found X' to 'X is so' is where study quality does its work." (Per the Assessment thread; already
  in `AGENT-GUIDE.md` §9 — don't collapse the two into one dimension.)
- **Argument → truth/support:** the current Agreement semantics — unchanged.
- **Ought → endorsement:** "do you endorse this action/value?" — NOT "is this true."

**Rating-dimension nudge (required):** when a user opens Agreement on an Ought (or Evidence) node, a
popup states the dimension in plain language ("You're rating whether you *endorse* this, not whether
it's factually true"). Mirror text in `AGENT-GUIDE.md` for agent raters. Absent this, raters will
apply truth-semantics to endorsement claims — a silent category error we already see in the eggs graph
(n063 "benefits outweigh risk" rated on Agreement-as-truth).

**The anchored machinery stops at the Evidence→Argument boundary — it must not touch Ought (SHIPPED).**
There is no truth oracle for a value, so calibration, discrimination-vs-anchored reputation, and the
certainty guardrail apply to Evidence (fidelity) and Argument (truth) but **not** to Ought. For an Ought,
the honest output is the **endorsement distribution and its value-camps** (`detect_camps` is exactly
right — value factions are real structure), never a calibrated "consensus value." And **reputation-
weighting tapers across the Evidence→Argument→Ought spine to ~zero on endorsement**: weighting a *value*
by someone's *truth-tracking competence* is a category error and a minority-suppression risk, so Ought
aggregation is **near-democratic** (weighted only by an anti-sybil / good-faith identity signal, not
True_R). This completes the §0 Evidence↔Ought symmetry — **Evidence (facts in) is maximally anchor/
reputation-weighted; Ought (values out) is minimally so.** *Live in `assess.py` (ought branch) +
ASSESSMENT-SPEC §3–§4.* Consequently the type-flip era-open (below) must flip the aggregation **mode**
(anchored-truth → democratic-endorsement), not merely reset ratings.

### 2.2 Categorical-consensus poll (a general primitive; Ought/Evidence are its first instances)

> **STATUS (2026-07-17): LIVE** (Assessment thread). `flag-type` opens the poll; `graph.py poll-vote
> --node <n> --question type:<ought|evidence> --value <yes|no|decline>` votes; the fold records raw
> votes; `reasonable/typepoll.py` `resolve_polls` resolves it **reputation-weighted** (quorum 5,
> two-thirds True_R-weighted Yes-share) in the assessment layer; `graph.py polls` reports state. A
> resolved Yes flips the node's effective kind (driving the Ought treatment in `assess.py`) and sets
> `reopen_required` so a truth→endorsement flip isolates prior ratings via the existing era machinery.
> `decline` is first-class but abstains from the ratio.

Typing is a **flag-triggered yes/no poll**, not a score:
- **Dormant until flagged.** No poll runs until someone `flag-type`s the node — attention is spent
  only when there's a reason to ask.
- **Yes / No / (decline).** We track the **Yes:No ratio**. A positive **No** is first-class data —
  "considered and rejected" ≠ "did not engage." (The explicit-signal principle, §0.)
- **Resolves like other consensus:** quorum + ratio threshold, reputation-weighted, reopenable if new
  raters shift it. Mechanically a cousin of `flag-friction` — reuse that plumbing.
- Build it **once** as a categorical-consensus poll; Ought-typing and Evidence-typing are instances,
  and it extends to other categorical properties (question-shaped? duplicate? disguised negation?).

**Type-flip opens a new era.** When a node crosses into Ought, its rating dimension changes
(truth→endorsement); prior Agreement ratings must not silently carry over. Use the existing
`reopen`/era mechanism so the history stays honest.

**The type-poll does NOT inherit the dispersion problem (unblocked).** The dispersion finding was about
inferring contestedness from *0–5 rating spread* — a noisy second moment. A yes/no typing poll is a
**proportion** (a first moment): the yes:no ratio *is* the signal, reliable at modest n. So the type-poll
settles on **ratio + quorum + weight** on its own — it does **not** need the Agreement contested signal.
For the weight, use reputation (True_R): typing ("is this prescriptive?") is a factual-ish classification,
so reputation-weighting it is defensible. (Only the **ghost trigger** in §3.1 genuinely needs the
settled-vs-contested signal — and it has it, via `contested.py`. The two are now decoupled.)

### 2.3 Type-contestation as a decomposition signal

> **STATUS (2026-07-17): LIVE (detection + routing).** `reasonable/decompose.py`
> `decompose_candidates` + `graph.py decompose` surface every type poll that met quorum but stayed
> *split* (rep-weighted yes-share inside the ambiguous band — resolving neither Yes nor No) as an
> is/ought-conflation **decomposition candidate**, with the §1.3 split guidance (is-claim + ought +
> explicit value premise, Hume-safe). The signal is the poll **proportion** (first moment, reliable —
> §2.2), not dispersion. The split itself is an authoring act; the rating side ("default to truth-rating
> while the type is contested") is honored by the viewer (HANDOFF-TO-UI §2.6).
While the crowd is split on whether a node is an Ought, default to **truth-rating**; the Ought
dimension activates only when the poll resolves Yes. But persistent type-contestation usually means an
**is/ought conflation** — route it to decomposition (§1.3) rather than forcing a single dimension. The
signal that a split is *persistent/real* (not transient noise) is a belief-camp on the node's nature —
`assessment.detect_camps` / `between_group_fraction` is exactly the trigger.

### 2.4 Competitive comparison for redundant paths
When redundant-path detection (§3.3) finds a direct edge 1→3 competing with a path 1→2→3, **present
the competing edges side by side, explicitly flagged as in competition**, and collect the standard
edge-Agreement ratings *in that comparative context*.
- **Why it's more than UI:** comparative judgments ("A is a stronger inference than B") are
  psychometrically more reliable than absolute ones, so the competitive framing sharpens the relative
  standing and raises confidence in it — a *direct partial remedy* for the reliability problem. This is
  the **same insight, at the elicitation layer, that makes the reputation stack work at the scoring
  layer**: discrimination-vs-anchored beats the old `align` term because *ordering is reliable, absolute
  level is not* (FINDINGS-SYNTHESIS §1/§2). Two directions of corroboration.
- **Caveat:** comparison yields *ranking*, not *magnitude*. Keep the absolute 0–5 edge-Agreement scale
  as the anchor; let the competitive context sharpen it, don't replace it (or we lose magnitudes).
- Edge Agreement itself is **unchanged and sufficient** as the primitive ("how strongly does this G
  support this D"); it runs on rater *means*, which are reliable. What's new is the comparative
  presentation and the redundant-path detection that triggers it.

---

## 3. Lifecycle + layout — the ghost state and normalized strength

> **STATUS (2026-07-17):** §3.1 ghost signal LIVE via `contested.py` (`ghost_eligible`) + the
> `graph.py ghosts` read verb; §3.2 `supersede`/demote verb now LIVE (`graph.py supersede [--restore]`
> → a conditional `demoted` marker on a **node, edge, or antithesis set**, byte-safe for existing
> graphs; `--restore` un-demotes so a ghost can be resurrected; surfaced in `ghosts` as a manual
> demotion distinct from the auto candidates, and skipped by `lint`); §3.3 redundant-path detection LIVE in `graph.py lint`; §3.4 length-normalized
> (geometric-mean) strength already computed in `chain.py` and exposed per-path by `graph.py chain`
> (the layout/declutter consumer is viewer-side). The remaining ghost visuals (grey/z-sink) are
> viewer-side; the data-layer signals (`ghost_eligible` + `demoted`) are all in place.

### 3.1 The ghost state (refuted-but-retained)
A new lifecycle state extending the existing machine. A node/edge that falls below threshold becomes a
**ghost**: present but greyed, near-zero pull on the force layout, **sinking in z** to a layer below
the living graph (a second, natural use of the z-axis alongside alternative-statement stacks). Still
retrievable — it records what the community found to be wrong.

Two triggers-and-cautions, both pointing at the same dependency:
- **Trigger on "settled-against," NOT low mean alone.** Mean 0.5 + engaged + confident-rejection →
  ghost. Mean 2.5 + high live disagreement → **alive** (the beating heart of an argument). Ghosting on
  low mean alone would bury live controversy. → **needs the reliable settled-vs-contested signal
  (§2.2 dependency).**
- **Distinguish "lost an antithesis" from "refuted on its own."** A rival floated *below* its
  competitor in an antithesis stack is *less supported*, not *wrong* — it dims relative to the winner
  but stays live. Only a node/edge refuted on its **own** Agreement ghosts. Otherwise we bury
  legitimate minority positions (the Semmelweis / minority-truth failure mode).

### 3.2 Demote, never delete
The verb is **`supersede` / demote**, not a delete. It moves a node/edge toward ghost status while
keeping it and its history in the graph. (This retracts the earlier "edge-remove verb" idea.)

### 3.3 Redundant-path detection
Detect when a direct edge and a multi-hop path connect the same pair (transitive-reduction-style), so
they can be surfaced as competitors (§2.4) and the weaker demoted (§3.2) — never silently removed.

### 3.4 Normalized strength drives layout and declutter (fixes the flatness bias)
The chain-rule **product** systematically favors direct/flat edges (each hop multiplies a factor <1),
so a naive "stronger edge pulls tighter" force-layout — and a naive "show a node only where its
connection is strongest" declutter — would self-assemble the graph **toward flatness**, undoing the
layering we want. Fix: drive both the **force-direction** and the **declutter** off the
**length-normalized strength** — the per-step **geometric mean** already computed by `chain.py`
(`product^(1/steps)`), not the raw product. Then layering is rewarded, not punished.
- **Detail-view cues:** relative left-right positioning of ground/dependent, line width, and color all
  keyed to normalized strength; a node appears as a ground of the focus only where its connection to
  the focus is strongest (its shortcut hidden when a stronger layered path exists).

---

## 4. Structural coherence — the layering discipline (build-time)

> **STATUS (2026-07-17): LIVE.** The proximate-attachment rule is in `AGENT-GUIDE.md`; the coherence
> lint is `graph.py lint` (`queries.coherence_lint`) — hubs, orphans, malformed sets, question/
> negation framing, redundant paths. Running the three FLF graphs through it surfaced real targets
> (covid n001 with 19 direct grounds; eggs' 1-member set `s2`; a negation-framed eggs node). The
> "coherence-review role" is for now the build-harness practice of running `lint` before closing a
> round; a dedicated re-routing author is deferred with the `supersede` verb (§3.2).

The measured symptom: top-answer nodes accumulate 11–19 direct grounds while mean chain depth is <1 —
a star/hub topology, not a layered tree (agents attach each claim to the salient hub rather than its
*proximate* support).

- **Proximate-attachment rule** (add to `AGENT-GUIDE.md` / round briefs): *for each ground, ask "does
  this support THIS node, or more precisely one of its existing grounds?" Attach to the most proximate
  claim; create the intermediate if it's missing.*
- **Coherence lint** (cheap, deterministic): flag high-in-degree hubs, orphans, malformed sets (e.g. a
  1-member antithesis), question-shaped nodes, disguised "not-X" negations.
- **Coherence-review role:** a closing author (extending synth-05) that walks each hub and asks "do any
  of these direct grounds support *each other*?", re-routing via `supersede`+re-`draw-ground` (edges
  are demoted, not deleted — §3.2).

---

## 5. Cross-thread dependencies & suggested sequencing

**Hard dependency:** §2.2 (poll thresholds) and §3.1 (ghost trigger) both require the **reliable
settled-vs-contested distinction** the Assessment thread is rebuilding. Neither should ship on
rating-dispersion, which we showed is too noisy. Share the threshold plumbing.

Suggested order (spec-first; each reviewable):
1. **Grammar** (§1) — rename to Evidence, add Ought type + Hume rule + `flag-type`. Low-risk, unlocks
   everything else; no dependency.
2. **Categorical-consensus poll + rating dimensions** (§2.1–2.3) — the Assessment thread's lane;
   gated on their settled-vs-contested work.
3. **Redundant-path detection + competitive comparison + normalized strength** (§2.4, §3.3, §3.4) —
   the layout/adjudication layer.
4. **Ghost/demote lifecycle** (§3.1–3.2) — gated on (2).
5. **Coherence discipline + lint** (§4) — build-harness + AGENT-GUIDE change; independent, do anytime.

## 6. Grammar extensions surfaced by the structural-review pass (2026-07-18)

Two findings from the `*-graph-v2` structural-review rebuilds (Review thread), logged here so they
aren't lost. Both are real; neither is implemented yet.

### 6.1 Auto-`reopen` on a type-flip to Ought (rule, not just a flag)
> **STATUS: PROPOSED (engine rule).** Today `typepoll.resolve_polls` *flags* `reopen_required` when a
> type poll resolves a `claim` to `ought`, but does not act — a build (or the live system) must call
> `reopen` by hand to isolate the pre-flip ratings into a closed era.

When a node that bundled an *is*-evaluation with a prescription is retyped to `ought`, its original
**truth** ratings **must not carry** into the new endorsement era — an Ought is endorsement-rated, and
carrying truth ratings recreates the exact is/ought category error the typing is meant to fix (caught
concretely in the eggs rebuild; the eggs original had already era-sealed those ratings for this
reason). So the flip should **auto-`reopen`** the node's Agreement (era-isolate the old ratings),
not merely raise a flag someone has to honor. Small change in the type-poll resolution / `ops` path;
gated behind the (dormant) live type-poll flow, so it has no effect on the static presentation graphs
— it's a correctness rule for the live system.

### 6.2 A non-rival directed "responds-to" / "addresses" edge (new relation)
> **STATUS: PROPOSED (grammar extension — cross-layer, post-deadline).** Filed as friction in
> `debate-graph-v2`; independently hit in the debate original.

Many claim pairs are **challenge → answer**: one claim *answers/engages* another without being a
mutually-exclusive rival — **both can be true at once** (e.g. Scott's "values drive the disagreement"
and the project's "so give values a first-class Ought home"; a critique and the design decision that
addresses it). The grammar has nowhere to put this: forcing the pair into an **antithesis set**
reads as "mutually-exclusive rivals" and overstates the clash; leaving it out loses the
response-linkage entirely. Proposed fix: a **first-class, directed, non-rival `addresses` edge**
("this claim responds to / engages that one"), distinct from both **Ground** (support) and
**antithesis** (rivalry), rated on *how well the response engages the challenge* (not truth, not
endorsement). It's a genuine cross-layer change (validate/fold/lint/viewer + a new rating dimension),
so it's a next-version item — but it is arguably the cleanest single grammar gap the project has
found, and it is exactly the relation an argument-map of a *debate* most wants.

## Open questions
- Do we build all three rating dimensions now, or Ought-endorsement first and Evidence-reliability
  later? (§2.1)
- Exact ghost threshold and whether a ghost can be *resurrected* by later raters (era/reopen
  interaction). (§3.1)
- Whether the coherence-review role should be able to demote edges autonomously or only *propose*
  demotions to the crowd. (§4)
- How the competitive-comparison rating reconciles with independent edge ratings already on file
  (re-rate, or blend?). (§2.4)
