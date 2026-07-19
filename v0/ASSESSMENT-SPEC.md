# Assessment Layer — build spec (Prototype 3; extends BUILD-SPEC + FORUMS-SPEC)

*Design: Feature Discussions Entries 3–4, 6, 18–22. ADDITIVE — the frozen core grammar, forums,
and locking are untouched. This adds graded rating, reputation, weighted aggregation, and quality
colour, ALL as a tunable playground (Entry 3 requirement: every scale/rule/weight pluggable so we
test rather than argue). Read BUILD-SPEC.md then FORUMS-SPEC.md first.*

## 0. Scope split (read this first)
- **v1 (this spec's BUILD target — testable with agents, Entry 22 phase 1):** the `rate`
  verb, three axes, pluggable aggregation + reputation (one score, two inputs, `Raw×Confidence`),
  weighted scores, quality colour in the viewer, a `config.json` of knobs, `reputation`/`show-config`
  read verbs.
- **v2 (SPEC ONLY here — Entry 22 phase 2):** assigned-rating sortition, Reading/Rating
  mode split, competence-earned assignment, bloc formation, Brier/market temporal scoring,
  staged rollout. Documented in §7 so it's not lost; NOT built now.

## 1. The three axes (Entry 18)
- **Reasonableness (R)** and **Clarity (C)** are properties of an **expression** → rate **phrasings**
  and **comments**. Scale **0.0–5.0** (tenths) + **abstain** (distinct from 0 — Entry 18).
- **Agreement (A)** is a property of the **proposition** → rate **nodes**. Same scale + abstain.
- **Edges** keep only Agreement-as-inference-strength (already built as `agree`); v1 does NOT add
  graded edge rating (their forums + binary agree suffice for now).
- The node **inherits R & C from its current top phrasing** (no R/C of its own) — and top phrasing is
  chosen by a **R-over-C-weighted** score (default bias configurable). A node's inherited R/C can thus
  change when a better phrasing wins, with nobody rating the node — intended (Entry 18).

## 2. New event (append-only, BUILD-SPEC §1a envelope)
- `rate` — payload `{target, dim, value}`:
  - `target`: `phrasing:<node>:<pid>` (dim ∈ {R,C}) · `<nodeid>` (dim = A) · `comment:<cid>` (dim ∈ {R,C}).
  - `value`: float `0.0–5.0`, or the string `"abstain"`.
  - **Re-rating:** a later `rate` by the same agent on the same (target,dim) supersedes the earlier
    (latest-by-seq wins). Abstain is a real, superseding value (removes a prior score).
  - Validation: target exists; dim valid for target kind; value in range or "abstain"; **an agent MAY
    rate its own authored items? NO — reject self-rating** (consistent with no-self-agree, Entry §2).

## 3. Reputation (DERIVED in the fold — not an event) — Entry 21
One **Reasonableness reputation** per agent, `True_R ∈ [0,1]`, from two inputs:
- **Authoring input** `auth`: the (rater-weighted) mean R of the agent's authored phrasings + comments,
  normalized to [0,1] (R/5). Null if they've authored nothing rated.
- **Rating input** (the competence signal). Two modes, chosen by whether an anchor reference is configured:
  - **`align`** (default, no anchors): how well the agent's ratings predict the aggregate — `1 − mean(|their_value −
    aggregate_value|)/5` over items they rated that others also rated. Null if insufficient overlap.
  - **`discrimination` vs the anchored consensus** (when `assessment.anchors` = `{node: truth}` is configured, or
    `compute(..., anchors=...)` is passed) — **AMENDMENT (discrimination reputation, 2026-07-15).** The rank-agreement
    (Spearman, mapped to [0,1]) between the agent's ratings and the *anchor-calibrated* consensus, over the nodes they
    rated (≥5 overlap, else null → auth-only). This REPLACES `align` when anchored, and is the validated signal:
    `align` rewards proximity to the (True_R-weighted) aggregate, i.e. agreement with the crowd — the tyranny-of-median
    rule (FINDINGS-SYNTHESIS §1) that *inverts on a biased crowd*. Discrimination is only valid against an **anchored**
    reference (never the raw crowd); with no anchors we keep `align` (acknowledged-imperfect) rather than an invalid
    unanchored discrimination. Anchor-free datasets are byte-identical (backward-compatible). Live: `reasonable/
    assessment.py` `discrimination_scores`; demonstrated on eggs-p8 (widens truth-tracker-minus-biased True_R from
    +0.017 under align to +0.075).
- **Raw_R** = configurable blend of available inputs (default: mean of whichever are non-null; if both
  null, the prior).
- **Confidence** `conf ∈ [0,1]` = `n/(n+K)` where `n` = number of independent assessments about the
  agent (ratings received on their items + their own scored ratings) and `K` = a smoothing constant
  (knob). New account: `n≈0 → conf≈0`.
- **True_R** = `prior + conf·(Raw_R − prior)` (shrinkage toward `prior`; Entry 21 `Raw×Confidence`
  shape). **`prior` = the newcomer floor (default LOW, e.g. 0.15)** (Entry 21): a newcomer is
  *unknown*, not known-bad — neutral Raw_R but `conf≈0 → low True_R` — so trust is *earned*, not
  granted. Climb is fast for good newcomers as `conf` rises.

## 4. Weighted aggregation (the circular part — Entry 21) — MUST stay deterministic
Aggregate score of an item = **True_R-weighted mean** of its raters' values (abstains excluded).
Reputation depends on aggregates which depend on reputation → resolve by **fixed-point iteration**:
initialize all `True_R = prior`; repeat {recompute aggregates → recompute reputations} for a **fixed
N iterations** (knob, default 12) or until change < ε; use the final values. Deterministic (no
wall-clock, stable ordering) so `rebuild` stays byte-identical (BUILD-SPEC §3). Document N and ε in
`config.json`. (This is the EigenTrust/PageRank-style loop; keep it simple and legible.)

**AMENDMENT (calibrated node-Agreement aggregate, 2026-07-15).** When anchors are configured
(`assessment.anchors` = `{node: truth}`), the **node-Agreement (dim A) aggregate is the anchor-
CALIBRATED consensus** instead of the True_R-weighted mean: each rater gets a per-rater affine
un-distortion fit on the anchors plus an inverse-residual-variance weight, so a biased or coordinated
majority that fails the anchors is neutralized (the validated aggregator, FINDINGS-SYNTHESIS §2/§8;
this is what survives the adversarial dose-response where the flat/True_R-weighted mean is captured).
It is loop-independent (depends only on ratings + anchors, not True_R), computed once, and also feeds
the discrimination reputation signal (§3). Other dims (R/C, edges, groups — no anchors) keep the
True_R-weighted mean, and **anchor-free datasets are byte-identical** (backward-compatible). Live:
`reasonable/assessment.py` `calibrated_consensus`; on eggs-p8 it lowers node-A MAE-vs-truth 0.374 → 0.344.

**AMENDMENT (calibration identifiability guard, 2026-07-17).** A per-rater affine un-distortion is only
identifiable when the anchor **truths** span a real range. When every anchor is a settled fact clustered
at one end of the scale — the norm for support-only cooperative graphs, whose confidently-oracle-able
nodes are all high-agreement — the fit has no slope leverage and collapses every node toward the
anchor-truth mean, *degrading* an already-good raw aggregate (covid: raw MAE-vs-oracle 0.82 → calibrated
1.28; even offset-only stays worse at 1.08 — the distortion is genuinely unidentifiable, not merely
mis-fit). So `calibrated_consensus` now **DECLINES** to calibrate when the anchor-truth spread is below
`MIN_ANCHOR_SPREAD` (2.0 on the 0–5 scale): it returns `consensus=None` and `assess.compute` falls back
to the raw/True_R path **byte-identically to the anchor-free run** (surfaced as `used_calibration: False`
in the compute output). The validated adversarial defense is preserved because its anchors span the scale
(eggs-p8 truth spread 3.28, including a truth-1.4 low anchor) — comfortably above the floor, so
calibration still engages there. This makes "anchors configured → calibrate" safe by construction: a
graph whose anchors cannot support the fit is no longer regressed by wiring them in. Live:
`reasonable/assessment.py` `calibrated_consensus` (spread guard) + `assess.py` (`used_calibration`).

**AMENDMENT (Ought → democratic endorsement, 2026-07-17).** A node of `kind: "ought"` is rated on
**endorsement** (a value: *"do you endorse this?"*), not truth. So its **node-Agreement (dim A) aggregate
is the DEMOCRATIC (unweighted, one-agent-one-vote) mean** — never truth/reputation-weighted, and it
overrides both the calibrated and True_R-weighted paths above. Weighting a *value* by *truth-competence*
is a category error and a minority-suppression risk (`archive/RESPONSE-evidence-argument-ought-ghosts.md` §2.1),
so reputation weighting **tapers to zero** on Oughts — completing the Evidence↔Ought symmetry (Evidence
maximally anchor/reputation-weighted; Ought minimally). Correspondingly (§3), an Ought's A-dim ratings
**neither build nor spend truth-reputation** — they are excluded from the rating-input (`align` /
discrimination) and from the assessment counts, since you cannot be *right* about a value. Anti-sybil /
good-faith identity weighting is the future refinement once an identity layer exists (unweighted is the
honest democratic default now); a categorical type-flip into Ought must also open a new era so prior
*truth* ratings don't carry as endorsements (SPEC §2.2 — now live, see next amendment). **Ought-free
datasets are byte-identical** (backward-compatible). Live: `reasonable/assess.py` (`ought_nodes` branch).

**AMENDMENT (categorical type-resolution poll, 2026-07-17).** SPEC-evidence §2.2 (handed to this
thread) is now built: a node's type is resolved by a **categorical-consensus poll**, a general
primitive (`type:ought` / `type:evidence` are its first instances; it extends to other categorical
properties). A `flag_type` **opens** a poll (a pure non-folding marker — no graph surface, no era, so
existing graphs stay byte-identical); raters cast **Yes / No / decline** via the new `poll_vote` verb.
Resolution is **reputation-weighted** and therefore lives in the assessment layer, not the fold
(`reasonable/typepoll.py`): it resolves **Yes** when Yes+No votes clear a **quorum** (5) *and* the
True_R-weighted **Yes-share** clears a **ratio** (0.66); `decline` is recorded but abstains from the
ratio. A poll resolved to `ought` joins the **effective Ought set**, so the node gets the democratic
endorsement treatment above. A claim→Ought resolution surfaces **`reopen_required`**: the flip changes
the rating dimension (truth→endorsement), so an explicit `reopen` (existing era machinery) isolates the
node's prior *truth*-era ratings — completing "type-flip opens a new era." **Poll-free datasets are
byte-identical** (a poll exists only once it has a vote; dormant flags emit nothing). Live:
`reasonable/typepoll.py` (resolver) + `assess.py` (`polls` in the compute output, effective-Ought wiring)
+ `fold.py` / `ops.py` / `validate.py` (`poll_vote`) + `graph.py` (`poll-vote`, `polls`).
## 5. Snapshot additions (graph.json)
- Each **phrasing** and **comment**: `"scores": {"R": {mean, n}, "C": {mean, n}}` (mean null if n=0).
- Each **node**: `"agreement": {mean, n}` (dim A) + `"quality": {"R":…, "C":…}` **inherited from top
  phrasing**; and top-phrasing selection now uses the R/C blend (record `primary_phrasing` as before).
- Every rated aggregate block (node A, phrasing R/C, edge A) also carries **`"histogram": [c0..c5]`**
  (UI ask) — the raw rating *distribution* as 6 integer bins over the 0–5 scale (`histogram[i]` = count
  of current-era ratings rounding half-up to `i`), **unweighted** and **present only when the block has
  ratings** (unrated blocks omit it, so the viewer falls back to the stdev band and rating-free graphs
  are unchanged).
- New top-level **`accounts`**: `[{agent, true_r, raw_r, confidence, n_assessments, authored, rated}]`.
- New top-level **`polls`** (§2.2) — **present only when a poll has ≥1 vote** (omitted otherwise, so
  poll-free graphs are byte-identical): `[{node, question, yes, no, decline, n_votes, yes_share,
  resolved, resolved_kind, reopen_required}]`.
- `meta`: `"rating_count"`, `"config"` (the knob values actually used).
- All existing fields unchanged; keep v0 `agree`/`strength` intact and independent (structural
  consensus stays; assessment is a parallel layer).

## 6. CLI + config + viewer
- `rate --target <…> --dim <R|C|A> --value <0-5|abstain> --agent <id> --data <dir> [--json]`.
- `reputation [--agent <id>] --data <dir> [--json]` → accounts table (all, or one).
- `show-config --data <dir>` / config lives in `<data>/config.json`, extended with an
  `"assessment"` block: `{scale_max:5, phrasing_R_over_C_bias:1.5, reputation:{prior:0.15, K:8,
  raw_blend:"mean"}, aggregation:{weight_by:"true_r", iterations:12, epsilon:0.001}}`. **Every one of
  these is a knob** — the point is to sweep them in phase 2. Missing config → documented defaults.
- `get-node`/`neighborhood` outputs gain the scores/agreement/quality fields.
- **Viewer (node-view + neighborhood):** colour cards by **hue/sat = Agreement** (white-gold high →
  gray low) and **lightness = combined R&C** — **perceptually INDEPENDENT channels** (Entry 21): a
  low-A/high-R&C card **glows gray**, a low-A/low-R&C card is **dim gray**; brightness legible across
  the whole agreement range. Ship gates: colourblind-safe + a **2×2 swatch test panel** ({hi/lo A} ×
  {hi/lo R&C} = 4 distinct chips) toggled somewhere unobtrusive. Edge thickness (strength) unchanged.
  A small legend line explaining the colour. Keep it tasteful; this is the first time the map carries
  *quality*, not just structure.

## 7. v2 / phase-2 (SPEC ONLY — do not build now; here so it's not lost)
- **Assigned rating / sortition (Entry 19):** users can't choose targets; enter Rating mode, get
  semi-random assigned items; Reading mode shows all cues, Rating mode hides them until exit;
  competence **earned & measured** (more of what you've rated accurately vs eventual consensus), never
  self-declared; assignment needs entropy + per-round secrecy. Principle frozen; sampling/competence
  math = knobs.
- **Blocs (Entry 3):** small blind voting blocs to preserve independence; bloc-average reward.
- **Temporal scoring (Entry 3):** Brier/Hanson market-scoring rule — rate = forecast of the settled
  value; reward correct-early over conformist; escrow while churn high, finalize when settled, reopen
  on new info; roll the horizon for never-settling questions. Needs the churn/settledness signal.

## 8. Tests (stdlib unittest, extend v0/tests/) + verification
- rate on phrasing/node/comment; abstain supersedes; re-rate supersedes; self-rate rejected; dim/target
  mismatch rejected; value-range validation.
- reputation: authoring-only, rating-only, both, and new-account (conf≈0 → true_r≈prior); fixed-point
  determinism (rebuild byte-identical; converges).
- weighted aggregation: a high-True_R rater moves an aggregate more than a low one; abstains excluded.
- ENTIRE existing suite (94 tests) still green.
- Viewer: Playwright — load a rated graph, confirm the 4 quality/agreement quadrants render distinctly,
  2×2 swatch panel present, no console errors, neighborhood + node view both coloured.

---

## Amendments

The sections above are the v1 contract as originally written and are left unedited above; changes
since are recorded here instead (same convention as BUILD-SPEC.md's Amendments section).

- **v1.1 — graded edge Agreement (viewer colour + edge-Agreement follow-up):** §1's "Edges keep only
  Agreement-as-inference-strength… v1 does NOT add graded edge rating" and §2's edge-rating
  exclusion are **superseded**. `rate` now also accepts a bare **edge id** as `--target`, dim **A
  only** (R/C remain invalid for edges — validation rejects them, same `invalid_dim` path as any
  other dim/target mismatch). Semantics are identical to node Agreement: 0.0–5.0 or abstain,
  self-rating by the edge's author rejected, re-rate/abstain supersede by (agent, target, dim).
  Each edge gains a `"agreement": {mean, n}` field in `graph.json` (§5), computed by the exact same
  True_R-weighted fixed-point loop as every other rated target — an edge Agreement rating is just
  another `(target, dim)` pair to `assess.compute()`, and an edge's rater's alignment / an edge's
  author's received-ratings both feed reputation the same way node/phrasing ratings already did (no
  edge-specific reputation code was added). The original structural `agrees`/`strength` fields are
  **untouched** and remain independent of this graded layer, exactly as §5 already promised for the
  rest of the assessment layer — "keep v0 `agree`/`strength` intact and independent" now reads as
  applying to edges' graded Agreement too, not just to nodes'/phrasings'.
  **Rationale:** structural consensus (`agree`/`strength`, "would I have drawn this edge myself?")
  and graded Agreement ("how strongly does the Ground actually support the Dependent, on the
  0.0–5.0 scale?") are different questions about the same edge; v1's original scope cut graded
  rating to nodes only for build simplicity, not because the edge case was judged unimportant —
  once the node/phrasing rating machinery existed, extending it to edges required no new
  aggregation/reputation logic, only a new target kind for `resolve_rate_target`/`fold`'s already-
  generic `(target, dim) -> {agent: value}` ratings structure to resolve.
  **Viewer:** §6's edge-thickness rule is also amended — line thickness (both views) and detail-view
  proximity now prefer an edge's graded Agreement mean (0–5) over its structural `strength` when the
  edge has at least one graded rating, through the *same* stroke/distance formulas (i.e. the graded
  mean is simply substituted for `strength` as their input) — falling back to structural `strength`
  unchanged for any edge with no graded ratings yet. Neighbourhood view's spring-layout *rest
  length* (its organic-clustering physics, as opposed to a focused card's detail-view distance)
  still uses structural `strength` only, so graded ratings never move where nodes cluster, only how
  thick/close a rated edge's line to them reads. The edge-focus card and its score line show
  `Agree X.X (n=N)` alongside the untouched `Agrees N` / `Strength N` whenever a graded mean exists.
  **Viewer colour redesign (independent of the above):** §6's original hue/saturation-for-Agreement
  + lightness-for-quality single-surface scheme is replaced with a two-channel **frame/body** split:
  the card's **border ring** (frame) encodes Agreement on a gold→gray scale, and the card's
  **interior fill** (body) encodes combined R&C quality on a white→gray scale, as two independent
  CSS properties instead of one HSL surface doing double duty — intended to be more legible ("does
  this rank" reads directly off two separate visual properties rather than requiring the viewer to
  disentangle saturation from lightness on one fill). An unrated dimension (no Agreement ratings; no
  R/C ratings) leaves that half of the card at its original, uncoloured default, per dimension.
  Text colour is derived from the body fill's lightness (a WCAG relative-luminance threshold), not
  the frame's. The 2×2 swatch test panel is kept (now showing frame+body pairs) plus a fifth
  "unrated" reference chip.

- **v1.2 — edge Agreement semantics: CONDITIONAL (resolves frictions f12/f14/f15/f16, 2026-07-07):**
  an edge's graded Agreement rates ONLY the inference, never the premise: *"IF the Ground were so,
  how strongly would it support this Dependent?"* The rater grants the Ground for the duration of
  the judgment; the Ground's own truth is a separate rating living on the Ground node's Agreement.
  This resolves the coverage run's 3-way convergent friction (one scalar carrying multiple
  dimensions) WITHOUT splitting the scalar — the dimensions raters were missing were premise-truth
  leaking into the edge, and the conditional reading routes each to its home:
  - f12 (premise reliable vs inference valid): premise reliability = Ground node's A; edge A =
    the conditional step only.
  - f15 (weak ground vs dependent overclaims): overclaiming IS an inference failure (the Dependent
    as phrased exceeds what the granted Ground licenses) → low edge A. Weak ground with a
    well-fitted Dependent → low node A, high edge A. Distinct places for the two cases.
  - f14 (source fidelity vs reliability, external anchors): the anchor node asserts "the source
    says/found X," so node A = fidelity (does it really say that?); the source's RELIABILITY
    (methodology, power, bias) lives in the edge, because the step from "the study found X" to
    "X is so" is exactly where study quality operates.
  - f16 (conjunction-edge semantics): under the conditional reading a joint Ground's member edge
    has no independent inference to rate — the rateable unit is the GROUP ("if ALL members were
    so…"). Member-edge abstention (what agents already did) is now the documented norm; a
    `group:<gid>` rating target (dim A) is the planned build item.
  **Scale anchors — degree of support, not entailment:** 5 ≈ granting the Ground would compel or
  near-compel the Dependent; 3 ≈ real but partial support (one good reason among several needed);
  1 ≈ even granted, barely bears on it. Partial support is healthy (it is why conjunctions and
  multiple Grounds exist) and must not be punished into the middle of the scale.
  **Consequence for chain strength:** with node A ≈ "how likely true" and edge A ≈ "how strongly
  this, if so, supports that," the phase-2 chain-strength product over a path stops being a
  heuristic and becomes the chain rule (P(premise) × P(step|premise) × …) under the usual
  independence idealizations. Prior art: Toulmin's grounds/warrant distinction — the node is the
  grounds, the edge is the warrant.
  No code change in this amendment (the rating machinery is untouched); it fixes the MEANING of
  the number. AGENT-GUIDE §9 carries the rater-facing version; the viewer's edge hover/score-line
  carries a one-line human-facing version.

- **v1.3 — the assessment grid: R/C rate any text, Agreement is typed by target (Entry 31, 2026-07-09):**
  §1's "R & C → phrasings and comments; A → nodes" and §2's target/dim table are **extended** (not
  replaced) so the three axes apply wherever each is meaningful. The organizing principle:
  **R and C rate an *expression*; Agreement rates a *claim or relationship* whose question is set by the
  target kind.** Canonical target-type × dimension table (the new contract):
  | target | A (Agreement) means… | R | C |
  |---|---|:--:|:--:|
  | node `<nodeid>` | is the proposition **true**? | — (inherited from top phrasing) | — (inherited) |
  | edge `<edgeid>` | does the Ground **conditionally support** the Dependent? (v1.2) | invalid | invalid |
  | group `group:<gid>` | do the members **jointly support** the Dependent? | invalid | invalid |
  | phrasing `phrasing:<node>:<pid>` | does this wording **belong to** (state the same claim as) the node? | is it well-reasoned? | is it clear? |
  | title `title:<node>:<tid>` | does this label **fit** the node? | is it neutrally/defensibly framed? | is it a clear label? |
  | comment `comment:<cid>` | — | is it well-reasoned? | is it clear? |
  Two concrete additions:
  - **Titles become a graded target.** `rate --target title:<node>:<tid>` accepts **A, R, and C**
    (same 0–5/abstain, self-rate-by-author rejected, supersede rules unchanged). Title-A = *fit*;
    title-R = *neutral/defensible framing* (a title that begs the question — "Eggs are obviously
    fine" — scores low R, distinct from clarity); title-C = *clear label*. **Primary-title selection**
    now uses a graded **A(fit) + R/C blend** (mirroring primary-phrasing selection), **subsuming the
    old binary `agree`-to-float mechanic** — one selection path, not two. Title authors earn the
    **authoring-R** reputation input (§3 `auth`) exactly like phrasing/comment authors (add titles to
    `_authored_items`' R-bearing set). `graph.json`: each title gains `"scores": {"A":…, "R":…, "C":…}`.
  - **Phrasings gain belonging-Agreement.** `rate --target phrasing:… --dim A` becomes **valid**
    (previously A was invalid on phrasings): it rates *belonging* ("does this wording state the same
    claim as the node?"). It **gates** primary-phrasing selection — a phrasing must clear a belonging
    threshold before its R/C blend can win primary status, so scope drift cannot hijack the node's
    meaning. It also **protects node-A's well-definedness**: node Agreement ("is the claim true?") is
    only meaningful if all phrasings state the *same* claim. A belonging score below the threshold fires
    a **spin-off nudge** (UI + agent-guide): "where does this belong? — create its own node." On
    spin-off the migrated phrasing starts a fresh node with **reset ratings** (same spirit as Entry-27
    era reset) and the UI **offers to draw an edge** old↔new. `graph.json`: each phrasing's `"scores"`
    gains an `"A": {mean, n}` alongside R/C.
  **Rationale:** this completes a grid rather than piling on ratings — three questions (fit/truth,
  reasoning, clarity) asked only where each applies. Belonging-A is the crowd-sourced **atomicity
  check** the project has wanted since the "who decides where one idea ends" open question. Human
  sliders and AGENT-GUIDE carry explicit per-target text for Agreement's differing senses (fit vs
  belonging vs truth vs support). Reputation aggregation/fixed-point is **unchanged** — every new
  `(target, dim)` is just another pair to `assess.compute()`, exactly as the v1.1 edge amendment
  established. This amendment is **independent of the reputation-scoring track** (Entry 30, discrimination
  /BTS): it changes *what can be rated*, not *how ratings become reputation*.

- **v1.4 — score dispersion exposed (Entry 31, 2026-07-09):** §5 snapshots carry the mean and n for
  every rated `(target, dim)`; this adds the **distribution** so the mean stops hiding the story. Each
  rated target's `graph.json` scores block gains `"dist"`: a small fixed-bin histogram of the raw
  (unweighted) rating values plus `stdev`, alongside the existing True_R-weighted `mean` and `n`.
  **Viewer:** the node/edge/phrasing info panel shows a small **histogram sparkline** (next to the
  chain-strength button etc.), **click-through** to a detail card with the full distribution, n, stdev,
  and per-rating detail. Render the **raw** distribution with the **weighted mean marked as a line**
  (so a user sees both "what people said" and "what the weighting did"); **suppress/gray** the sparkline
  below ~5 raters (a 3-bar histogram is noise — show n instead). **Rationale:** the reputation work
  (Entry 30) showed the mean collapses distinct epistemic states — a "3.4" can be tight consensus, wide
  uncertainty, or experts-at-1.5 vs crowd-at-4. A histogram distinguishes **bimodal (contested)** from
  **wide-unimodal (uncertain)** — it renders the tyranny-of-the-median *visible*, and aligns with the
  site's maximum-information-availability stance. It also **replaces replicate voting blocs' dispersion
  role** without their density cost (Entry 30): dispersion is read straight off the full rater set, no
  partitioning. Forward hook (not built): the detail card is where a predicted-vs-actual overlay (the
  BTS "surprisingly popular" gap) would live if meta-predictions are ever collected.

- **v1.5 — blind Rating mode implemented for the read verbs (2026-07-14):** §7's Reading/Rating
  mode split was v2/SPEC-ONLY, deferred as a UI concern. But the eggs-p7 run exposed it as a
  *correctness* gap, not a UI nicety: raters were told to "rate blind," yet the `get-node` read they
  were instructed to run returns the live `agreement.mean/n/stdev`, and the graph scaffold's carried
  comments (30 of eggs-p6's stated explicit rating values) were visible too — so "blind" depended on
  the rater choosing not to look at data the tool handed them. This amendment **builds the read-side
  half of Rating mode**: `get-node` and `neighborhood` accept `--rating-mode`, which blinds every
  consensus cue for the target — the node's/edge's `agreement` (A), `quality` (R/C), every
  phrasing's/title's `scores` (R/C/A **including** the v1.3 belonging-A that the sealed-mask path
  never handled), the comment thread + `comment_count`, and rating-`heat` — while leaving claim/title
  TEXT, Ground/Dependent STRUCTURE, antithesis membership, and edge typing intact (you must read the
  claim and its support to rate it). The v0 structural `agree`/`strength`/`belonging` counts are left
  visible (they are the separate structural-consensus layer, not the graded rating being produced;
  blinding them too is a future knob). Implemented in `queries.get_node`/`neighborhood`
  (`rating_mode=`) + `blind_node`/`blind_edge`; CLI `--rating-mode`; tests in
  `reasonable/test_rating_mode.py`. The rater-facing rule is in AGENT-GUIDE §9, and the run harnesses
  now read with `--rating-mode`.
  **Enforcement (imposed, not opt-in).** The `--rating-mode` flag alone would still leave blindness to
  each agent's discretion (omit the flag → see everything), which just relocates "trust the rater not
  to look." So a dataset-level switch makes it a *condition on the graph*: `config.json`
  `"rating_mode_only": true` forces every rater-facing read verb — `get-node`, `neighborhood`, AND
  `list-comments` (thread withheld, only its count disclosed) — into blind Rating mode regardless of
  any CLI flag, with **no CLI way to un-blind** (the escape hatch for analysis/experimenters is reading
  `graph.json` directly, which agents never do). `queries.rating_mode_only()` reads it; `show-config`
  surfaces it. **For the whole prototype/FLF phase this is ON for every build/rate dataset** — the
  agents constructing and rating the graph are always in Rating mode, no Reading-mode surface, no
  optionality; the run scaffold (`setup_p7.py`) writes it by default. The knob (rather than hard-coded
  blindness) exists for two reasons: a future human Reading-mode surface, and the blind-vs-social A/B —
  whose "social" arm is just a second dataset with `rating_mode_only: false`.
  **Still spec-only (not built): the *write*-side of Rating mode** (the
  per-round sortition/secrecy of v2 §7) and the interactive Reading↔Rating toggle in the viewer — this
  amendment guarantees a rater is *never shown* a target's consensus when the switch is on.
  **Rationale:** social information anchors raters (coldstart-lab E1's protocol effect — the same
  personas tracked truth at 0.52 with cues visible vs 0.89 in a clean pass — was the single largest
  accuracy lever in the whole reputation investigation), and a rating that merely echoes the visible
  consensus adds no information to the aggregate. Enforcing blindness at the tool layer is the
  prerequisite for the controlled blind-vs-social experiment that lever still needs.
