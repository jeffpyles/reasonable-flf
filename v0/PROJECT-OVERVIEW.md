# Reasonable — a full account of what we built, how it works, and where it goes

*Written 2026-07-17, from a fresh reading of the repository on `main`. This is the coherent
overview of the whole project as it actually ended up — the concept, the working machinery, the
discoveries and corrections we made along the way, a map of where every piece lives, and honest
suggestions for where it could go next. It is **not** the FLF submission draft; it is the
comprehensive reference a submission (or a new contributor, or a future session) can be written
from. Everything below is in the repo and reproducible; file pointers are given throughout.*

---

## 0. What Reasonable is, in one paragraph

Reasonable is **"Wikipedia for arguments" rather than facts** — a web app for argument-mapping-based
collective truth-finding. A disputed question is decomposed into atomic, truth-apt **claims** placed
on a 2-D **graph**, connected by a small set of typed relations: **Grounds/Dependents** (a directed
support edge, seen from both ends), **Antitheses** (sets of *rival positive claims*, never
negations), **Conjunction groups** (grounds that only support jointly), and **Alternative phrasings**
(a z-axis stack of the same claim re-worded, the community floating the best to the top). On top of
that structure sits an **assessment layer**: reputation-weighted, blind rating that surfaces *who
tracks the evidence most carefully* and lets the map's verdicts approach truth without collapsing
into a popularity vote. The founding intuition (from the project's originating "Fable" note):
language is linear because time is, but ideas branch, so faithfully mapping reasoning needs a 2-D
medium — especially in the **untestable** domains (ethics, politics, religion) where we can't
falsify our way to truth and the best we can do is map the disagreement honestly.

The project is organized around the **FLF "Lab Leaks, Black Holes, and Eggs" Epistemic Case Study
Competition** (deadline 2026-07-19), whose three-layer framing — *ingestion → structure →
assessment* — we adopt directly. Most of this repository is the **structure** and **assessment**
layers, built and stress-tested against the competition's three deliberately-varied case shapes.

---

## 1. The design through-lines (why it's shaped the way it is)

Six principles recur across every part of the system. They are worth stating up front because they
explain most of the specific engineering choices that follow.

1. **The graph has three boundary roles, not one.** **Evidence** anchors reasoning to the world at
   the *start* (facts in); **Argument** is the internal reasoning; **Ought** anchors reasoning to
   the world at the *end* (values/actions out). This Evidence↔Ought symmetry is deliberate and it
   extends to *weighting*: Evidence (facts in) is **maximally** anchor/reputation-weighted; Ought
   (values out) is **minimally** so — endorsement is near-democratic and never weighted by
   truth-competence.

2. **Support-only; opposition is a rival positive claim.** There is no "not-X" node. Disagreement is
   expressed by writing the *actual competing claim* and antithesis-linking it. This is the single
   most important authoring discipline, and it is what keeps the graph a map of positions rather than
   a flame war of negations.

3. **Prefer elicited explicit signals over inferred ones.** Ask meta-uncertainty directly rather than
   inferring it from rating dispersion; make the explicit "No" in a typing poll first-class data;
   collect comparative judgments where they're more reliable than absolute ones. This principle,
   learned the hard way (see §5), reshaped the assessment layer.

4. **Preserve, don't delete.** A reasoning graph that forgets what it disproved will relitigate it.
   Refuted material is **demoted to a ghost**, never removed — "we checked this, it's wrong" is a
   primary asset. The event log is append-only by construction; even the "delete" verb is a
   `supersede`/demote that keeps the target and its history.

5. **Comparison and structure beat absolute spread.** Comparative judgments are more reliable than
   absolute ones; *structural* disagreement (antithesis sets, competing edges, belief-camps) is more
   reliable than *statistical* dispersion (rating variance). This is a direct consequence of the
   dispersion-reliability finding (§5) and it shows up at both the scoring layer and the elicitation
   layer.

6. **A purely internal rule can only measure agreement with the crowd** — so it inherits whatever the
   crowd gets systematically wrong. The fix is a small, frugally-spent dose of *external* ground truth
   (anchors). This is the thesis of the entire assessment investigation (§4–§5).

---

## 2. The data layer — how the machine actually works

The whole system is **stdlib-only Python plus one interface** (`v0/graph.py`, ~1000 lines). No pip
installs, no servers, no frameworks, no network. That is a deliberate submission asset: the judges
said "run it, don't just read it," and every analysis in the repo reproduces from committed data with
one command.

### 2.1 Append-only log → deterministic fold → frozen snapshot

Every graph lives in a directory with three files (`v0/BUILD-SPEC.md` is the frozen contract):

- **`events.jsonl`** — the append-only log, the *source of truth*. One JSON object per successful
  write: `{seq, ts, agent, verb, payload}`. Never rewritten, only appended. Rejected writes never
  appear (they aren't mutations).
- **`graph.json`** — a derived snapshot, rebuilt wholesale by *folding* the event log after every
  write. This is what a viewer reads. Never hand-edited.
- **`config.json`** — persists the assessment/phase-2 config so a rebuild is reproducible from
  log + flags alone.

The core invariant is **`same events.jsonl + same config → byte-identical graph.json`**. It is what
lets the grammar evolve (we added `evidence`/`ought` kinds mid-project) while every existing graph
rebuilds bit-for-bit unchanged. Achieving it required a **determinism discipline** enforced
throughout the assessment code: no wall-clock reads in the fold, no unordered `set()` feeding a
float sum, always iterate in log-`seq` order — so `graph.json` is stable regardless of
`PYTHONHASHSEED`.

### 2.2 The code package (`v0/reasonable/`, ~5k lines)

The package is strictly **layered**: each higher layer consumes the one below without mutating it.

- **`store.py`** — on-disk I/O and the write lock. `locked()` wraps the entire read→fold→validate→
  append→rebuild critical section under a POSIX `flock` (bounded-wait, with a timeout); reads never
  take the lock. Atomic `graph.json` writes via `os.replace`.
- **`fold.py`** (the largest module) — the heart. `fold(events)` replays the seq-sorted log into an
  internal state; `to_graph_json(state, …)` projects that state to the frozen public schema,
  consulting the assessment/lifecycle/heat layers. Holds the node-kind constants (`claim`,
  `evidence`, `ought`, with `external_anchor` a permanent read-alias) and the shared target-string
  grammar (`set:`, `title:`, `phrasing:`, `comment:`, `typing:`, `group:`, bare id). All ids are
  derived from fold-state counts, so assignment is deterministic and idempotent.
- **`validate.py`** — one `validate_*` per write verb; turns bad writes into structured
  errors/warnings *before* they touch the log (no self-agree, duplicate-text warnings, target
  resolvability, Hume's rule, the soft ~350-char claim cap as a warning not a block).
- **`ops.py`** — write orchestration: ties lock + validate + fold + rebuild into one command per
  verb, returning a `Result`.
- **`queries.py`** — all read-side derivations, the **blind-rating masking** (hides consensus cues
  from raters), and the deterministic **coherence lint**.
- **`assess.py`** — reputation (True_R) + reputation-weighted aggregation via a fixed-point loop.
  Ought nodes get *democratic* (unweighted) aggregation and never feed truth-reputation.
- **`assessment.py`** — the statistical primitives: affine **calibration**, **discrimination**
  scoring, and spectral **belief-camp detection** (`detect_camps`, `camp_contested`), plus the
  `certainty_guard`. Holds the `MIN_ANCHOR_SPREAD = 2.0` identifiability floor (§5).
- **`lifecycle.py`** — the phase-2 envelope around each aggregate: lifecycle `state`
  (sealed/provisional/settled/contested), per-era history, per-bloc breakdown, and
  `structurally_contested` (the antithesis-rival signal that is the *reliable* contested trigger).
- **`heat.py`** — event-time (not wall-clock) heat diffusion, so "what's active" stays deterministic.
- **`typepoll.py`** — reputation-weighted resolution of the categorical **type polls**
  (`DEFAULT_QUORUM = 5`, `DEFAULT_RATIO = 0.66`); resolution lives here, not the fold, because it
  needs True_R.
- **`decompose.py`** — the is/ought decomposition router (§3): a type poll that clears quorum but
  stays *split* is surfaced as a conflation candidate.
- **`contested.py`** — the single shared **settled / contested / ghost-eligible** verdict, composing
  structural rivalry + belief-camp disagreement + a target's own Agreement. Antithesis members are
  *never* ghost-eligible (the minority-truth protection).
- **`chain.py`** — support-chain strength over the Ground DAG, including the length-normalized
  **geometric-mean** strength and the `compare` walk back to two nodes' last common ancestor.

### 2.3 The CLI verbs (`graph.py`)

Every call is `python3 graph.py <verb> [args] --data <dir> [--agent <id>] [--json]`. `--data` is
required on every call; there is no default graph. Highlights:

- **Authoring:** `create-node` (`--kind claim|evidence|ought`), `draw-ground` (from → to, with the
  Hume check), `add-antithesis`, `agree`, `propose-title`, `propose-phrasing`, `flag-friction`.
- **Grammar-evolution:** `flag-type` (opens a type poll), `poll-vote` (yes/no/decline),
  `supersede` (demote to ghost; `--restore` un-demotes).
- **Rating:** `rate` (`--dim R|C|A`), `reopen` (start a new era when a node's rating dimension
  changes).
- **Reading/analysis:** `get-node`, `neighborhood`, `search`, `list-sets`, `list-studies`,
  `polls`, `decompose`, `assess`, `contested`, `ghosts`, `lint`, `reputation`, `chain`, `compare`,
  `stats`, `rebuild`.

The authoring rules a rater/author must follow live in **`v0/AGENT-GUIDE.md`** (the mental model,
the norm discipline, the full verb reference, a worked example, and — §9 — the three rating
dimensions and the conditional-edge-rating rule). Test coverage is **~266 test functions across 19
files** (heaviest on assessment, phase-2 lifecycle, and the forums/comment layer).

---

## 3. The grammar extensions — Evidence · Argument · Ought, polls, ghosts, coherence

Partway through the project we wrote a design spec (**`v0/SPEC-evidence-argument-ought-ghosts.md`**)
that added the boundary-role type system and its consequences. It is now implemented §1–§4 on the
data/CLI layer; only the *viewer* rendering is outstanding (handed off in `v0/HANDOFF-TO-UI.md`).

- **§1 — the three node kinds and Hume's rule.** `external_anchor` was renamed **Evidence** (naming
  the role, not the mechanism), and an **Ought** kind was added. **Hume's rule is enforced at the
  write boundary**: an Ought may not be a Ground of a non-Ought (you cannot derive an "is" from an
  "ought"); ought→ought chains are allowed. This makes a whole class of smuggled-value-premise errors
  impossible *by construction*. Grounding *into* an Evidence node is a warning (evidence is anchored
  by its source, not by in-graph reasoning). All three flagship graphs rebuilt byte-identically after
  this change.
- **§2.1 — three rating dimensions.** Agreement is not one question. Evidence is rated on **fidelity**
  (does the source really say this?) at the node plus **reliability** (methodology/power/bias) on the
  *outgoing edge*; Argument is rated on **truth/support**; Ought is rated on **endorsement** ("do you
  endorse this?", never "is it true"). The anchored machinery — calibration, reputation-weighting, the
  certainty guardrail — applies to Evidence and Argument but **stops at the Ought boundary**: there is
  no truth oracle for a value, so an Ought's honest output is its endorsement distribution and
  value-camps, aggregated near-democratically.
- **§2.2 — the categorical type poll.** A node's *type* is resolved by a dormant-until-flagged
  yes/no/decline poll, resolved reputation-weighted (quorum 5, two-thirds True_R Yes-share). A
  resolved "Yes → ought" flips the node into democratic-endorsement treatment and raises
  `reopen_required` so the old truth-ratings are isolated into a closed era. A **positive "No" is
  first-class** ("considered and rejected" ≠ "never engaged"). The poll is a *proportion* (a first
  moment), so — unlike rating dispersion — it is reliable at modest n.
- **§2.3 — type-contestation as a decomposition signal.** A poll that clears quorum but stays *split*
  usually means an **is/ought conflation** ("eggs are bad" = "eggs raise CVD risk" [is] + "you should
  avoid eggs" [ought]); `decompose` surfaces it with Hume-safe split guidance.
- **§3 — the ghost lifecycle.** A node/edge refuted **on its own Agreement** (low, settled,
  confidently rejected — *not* merely low-mean, and *not* a rival that lost an antithesis stack)
  becomes **ghost-eligible**: retained, greyed, sunk in z, near-zero pull on the layout, still
  retrievable. `supersede` is the manual demote (node/edge/set; `--restore` reverses it). The
  crucial guard: *losing an antithesis is not being refuted* — a floated-below rival is less
  supported, not wrong — which protects legitimate minority positions (the Semmelweis failure mode).
- **§3.4 — normalized strength drives layout.** The chain-rule product favors flat/direct edges (each
  hop multiplies a factor < 1), so a naive "stronger edge pulls tighter" layout would self-assemble
  the graph *toward flatness*. Driving layout and declutter off the **length-normalized geometric
  mean** rewards layering instead of punishing it.
- **§4 — coherence lint.** A cheap deterministic pass flags star/hub nodes (a top answer with 11–19
  direct grounds instead of a layered tree), orphans, malformed antithesis sets, question-shaped
  nodes, and disguised negations. Advisory only; run before closing a build round. Paired with the
  **proximate-attachment rule** in the author guide ("attach each ground to the most proximate claim,
  not the salient hub").

---

## 4. The assessment layer — the research spine

This is the deepest body of work, and the strongest part of the FLF fit. The full synthesis is
**`v0/FINDINGS-SYNTHESIS.md`**; the frozen contract is **`v0/ASSESSMENT-SPEC.md`**. The core question:
*in a collaborative map, how do you reliably find the truth-tracking raters and give their judgments
due weight — so verdicts approach truth, cold-start from nothing, scale to millions, survive genuine
contestedness, and resist coordinated manipulation?*

### 4.1 What we killed (robust negative results)

- **Alignment / level-agreement** rewards proximity to the average rater → buries the sharpest
  raters (**tyranny of the median**). Every variant, including Dawid-Skene/latent-truth, inherits the
  majority's error because it infers "truth" from the same ratings.
- **Discrimination (ordering-tracking)** is the cheap win but **inverts catastrophically on a biased
  crowd** — it scores agreement with the biased consensus. Ship it only against an *anchored*
  consensus, never the raw one.
- **Bayesian Truth Serum** is principled and dominates in synthetic worlds, but on real agents the
  prediction-asymmetry it needs failed in aggregate. Parked pending first-class prediction
  elicitation.
- **Winner-take-all (superlinear) weighting** beats a biased majority on clean anchors but shatters
  on wrong anchors and *amplifies* anchor-gaming sleepers. Retired as a default.

Every failure is the same failure (through-line #6): an internal-only rule measures agreement with
the crowd and inherits its systematic errors.

### 4.2 What works — the validated stack (now live in the code)

1. **Blind rating, enforced at the tool layer.** Raters never see the consensus/comments while
   rating. This was the single biggest accuracy lever measured (0.52 tracking with cues visible →
   0.89 blind). Enforced by a dataset config with no opt-out.
2. **Discrimination vs the *anchored* consensus** as the ongoing rater signal — never vs the raw
   crowd.
3. **Calibration as the aggregator** — fit each rater an affine map on external anchors, invert their
   systematic error, weight by inverse residual variance. Works with *zero* competent raters, degrades
   gracefully under wrong anchors — **but gated on anchor spread** (§5).
4. **Camp detection + adjudication for contested regions** — a spectral split of the rater-agreement
   matrix finds viewpoint factions with no oracle; a few contested anchors adjudicate which faction
   tracks truth. Detection is cheaper and more robust than correction.
5. **Panel anchors** — a diverse frontier-model panel deliberates to forge anchors where no ground
   truth exists (validated to reproduce an independent expert oracle at r≈0.98, with a value-question
   guard).
6. **A thin external-grounding check** — the one thing that catches biases the whole model generation
   shares (the Sonnet oracle tracks the documented real-world egg record at corr +0.95, but *both* of
   its divergences over-rate how "unsettled" a settled question is — a plausibly whole-generation LLM
   bias, invisible from inside an all-model loop).

All three killed rules (align, raw-stdev trigger, True_R-weighted node aggregate) are now **replaced
in the running code, gated on anchors** and byte-identical on anchor-free datasets. The validated
stack — calibration (aggregator + reputation), camp-detection, structural contested trigger, and the
certainty guardrail — is live.

### 4.3 Cold-start, scale, and the disposition/capability results

- **"Reasonableness" is two quantities of very different measurability.** Fine quality-rank among
  good-faith raters is nearly unmeasurable at realistic budgets (~77 ratings for a 0.5-reliable
  estimate); a systematic *disposition* is cheap (~8 ratings). So: **assess dispositions/tiers fast,
  accumulate fine rank slowly**, and set shrinkage from measured split-half reliability rather than as
  a taste knob.
- **One global reputation scalar is structurally insufficient** — a diligent-but-biased user earns
  good global reputation on the uncontested majority and rides it into the contested items.
  Disposition must be assessed **per contested region**; only general diligence is global.
- **Anchors are worthless without routing** — random assignment means almost no user ever rates enough
  anchors; a ~20% routed probe slice flips a broken contested consensus to 0.8–0.9, and reputation
  then propagates ~2 hops. **Oracle budget scales with the number of contested divides, not users.**
- **Disposition dominates capability.** A biased *strong* model is barely better than a biased weak
  one, and worse than a *neutral* weak one — raw capability doesn't reason its way out of an
  entrenched prior. Camp detection tracks *belief*, not capability, and the axis doesn't rotate as the
  divide weakens (the feared failure mode doesn't occur); the transition is sharp, and the trigger
  doesn't false-fire on a homogeneous population.

### 4.4 Adversarial robustness (the red-team spine)

Offline dose-response (attacker fraction swept 0→60%), scored with **verdict-level MAE** because
correlation is offset-invariant and *hides* a coordinated level-shift (a metric-choice lesson):

- No defense → captured near 40–50% attackers.
- **Calibration robustly defeats naive/jittered/sybil even at a 60% majority** — they lie on the
  anchors too, so calibration inverts them.
- **The sleeper is the crux** — honest on anchors, lying only in the un-anchored gaps — it defeats
  calibration by ~30%, and superlinear weighting makes it *worse*. Calibration's reach = the anchors'
  coverage of the contested frontier.
- **Detection is the 100%-recall backstop** — camp-detection flags every attack type including
  sleepers, even where correction fails. Design consequence: **correction + detection + escalation**,
  with dense rotating/secret anchors and attack-aware metrics.

The **covid second-domain run** (real blind LLM raters, both attack directions) reproduced every
eggs hypothesis *and* surfaced two findings eggs couldn't:
- **On a camp-split question, detection is necessary but insufficient** — it flags the suspicious
  *side* at 100% recall but sweeps in the honest same-side camp (precision ~0.5). The isolating
  signal is **coordinated extremity** (attacker crux |Δ| = 2.2 vs honest 0.66) — a two-stage detector.
- **The over-certainty attack is the hardest case, and calibration can't stop it.** A bloc pushing
  the *already-leading* answer can't flip the verdict, so it manufactures false *certainty* — driving
  the calibrated gap past the oracle's warrant, collapsing a live question into fake near-settlement
  and burying the legitimate minority (the **Semmelweis / minority-truth-survival** problem). Crucially
  **distance-to-oracle MAE hides it** — a second "the metric is a defense surface" lesson. Net thesis:
  **for a truth-finding layer the hardest adversarial case is consensus entrenchment, not
  verdict-flipping — and it's the attack real agents most willingly serve** (2/8 agents refused to
  manufacture the *contested* consensus; 0/8 refused the *mainstream* one — small-n, but directional).
- A working **verdict-certainty guardrail** was built and tested offline against every committed
  sweep — quiet on the honest baseline, catches the flip and the MAE-invisible over-certainty sleeper.

---

## 5. The corrections we made along the way (the honest part)

The project's methodological signature is that we followed our own findings to the point of
**revising our own prior claims on new data**. Three corrections are worth calling out because each
one changed the design:

1. **Dispersion is not a reliable contested signal — even for experts.** We initially inferred
   "which nodes are contested" from rating spread. A denser reference (12 Sonnet lens-raters on a
   covid subset) showed two *independent* 6-rater panels reproduce their own crux map at only r≈0.36
   — so rating variance is intrinsically noisy *for everyone*, not just cheap raters. **The reliable
   "where is it contested" signal is the structural markers the build produces** (antithesis sets,
   friction flags, belief-camps), not the rating variance. This is why the contested trigger was
   swapped from raw stdev to `structurally_contested` + `detect_camps`, and why through-line #5 reads
   the way it does. (`analyze_dispersion_reference.py`; FINDINGS-SYNTHESIS §12e.)

2. **Calibration has an identifiability floor.** Wiring the calibrated aggregator into covid-graph
   (a cooperative honest panel) *degraded* accuracy (held-out MAE 0.82 raw → 1.28 calibrated).
   The root cause wasn't mis-fit but **unidentifiability**: covid's confidently-oracle-able anchors
   are all settled facts clustered high (spread 0.62), so the affine fit has no slope leverage and
   collapses every node toward the anchor mean. Even offset-only calibration stayed worse. Fix
   (shipped): `calibrated_consensus` **declines when anchor spread < `MIN_ANCHOR_SPREAD` (2.0)** and
   falls back to the raw aggregate byte-identically. So "calibration is the aggregator" holds
   *wherever anchors span the scale*; on clustered-anchor cooperative graphs the raw aggregate was
   already good and is now preserved. (FINDINGS-SYNTHESIS §13.)

3. **Cheap swarms scale breadth, not the crux map — but the durable penalty is confidence, not
   dispersion.** Model-tiering (16 Haiku vs Sonnet lens-raters) on both a contested (covid) and a
   confident-answer (black holes) graph showed the verdict is preserved and cheap means track experts
   (r 0.85–0.88), but a cheap swarm's **verdict confidence compresses with contestedness** (~58%
   margin collapse on contested covid vs ~9% on confident black holes). So a cheap swarm's confidence
   is trustworthy exactly when the question is easy and untrustworthy exactly when it's hard — which
   argues for a **hybrid**: cheap swarm for scale/verdict/mean, a little expensive scrutiny reserved
   for trustworthy confidence on the hard, contested regions. (`blackholes-graph/harness/
   TIERING-RESULTS.md`; FINDINGS-SYNTHESIS §12c–e.)

There is also a standing **report-vs-graph result** worth its own line: fed the *same* 24 sources /
80 claims, an off-the-shelf deep-research pipeline's adversarial verifier **inverted the scientific
consensus** (refuted six peer-reviewed pro-zoonotic findings, confirmed contrarian preprints), while
the assessed graph *recovered* it. The diagnosis is **structural, not political**: a binary adversarial
*filter* (right for catching junk) misfires as a truth-*weigher* — default-to-refute fires on any
confident claim in a contested field, and binary votes discard the fact inside a fact-plus-inference
bundle. We then *fixed* it with a graded-verify step (separate provenance from a 0–5 merit score, drop
default-to-refute), validated live. This is the head-to-head "beat off-the-shelf deep research on the
same sub-question" the rubric asks for. (`covid-graph/COMPARISON.md`.)

---

## 6. The content — the graphs we built

### 6.1 The three canonical FLF case graphs (plus the meta graph)

All are built + blind-panel-assessed, each with a full `harness/` (a `workflow_build.js` +
`workflow_assess.js` pair of panel runners), a deep-research `REPORT.md` baseline, and its own source
pack under `v0/sources/`. They are the same three case *shapes* the competition specifies:

- **`v0/eggs-graph/`** (66 nodes) — the **mundane-but-contested** shape ("Are eggs bad for your
  health?", dietary cholesterol → CVD/mortality). The dev question and the spine of the whole
  investigation. Rated by a 20-rater depth panel (`harness/DEPTH-RESULTS.md`): "eggs raise CVD" ~1.6
  vs the overall "not bad on balance" ~3.7. The bundled "not bad" root was later decomposed into a
  risk sub-claim (`n065`) and a benefits sub-claim (`n066`) so benefits no longer prop up the no-risk
  claim.
- **`v0/covid-graph/`** (133 nodes — the largest graph in the repo) — the **genuinely-contested
  curated-debate** shape (SARS-CoV-2 origins). Carries the marquee **`COMPARISON.md`** (the
  report-vs-graph head-to-head of §5) and the model-tiering study. Its synthetic-origin branch was
  built out (restriction-site / CGG-codon / RBD-ACE2 arguments, each with rebuttals) and its hubs
  de-starred into strand-aggregators; the panel still favors zoonosis (n001 3.34 vs n002 2.17).
- **`v0/blackholes-graph/`** (69 nodes) — the **confident-answer** shape ("Could the LHC create a
  black hole that destroys Earth?": strong consensus with a vocal edge). Panel grounds "safe" 4.70 vs
  "catastrophe" 0.33, decisively, as a confident-answer case should. Carries a cross-model
  **`oracle/`** subdirectory (Sonnet×2/Opus/Fable scored all 69 nodes; the 20-rater panel tracks the
  oracle at **MAE 0.197, r=0.912**, and the certainty guardrail correctly stays *quiet* — earned
  confidence, in contrast to covid where it fires) and `harness/TIERING-RESULTS.md`.
- **`v0/debate-graph/`** (32 nodes, 10 antithesis sets) — the **meta** graph and the single most
  rhetorically potent piece (see §7).

Building all three shapes is the direct hit on the **generalizability** dimension. The `blackholes-graph`
is the matured successor to two earlier reproducibility prototypes, `v0/swarm-blackholes/` (23 nodes)
and `v0/swarm-blackholes-2/` (24 nodes) — the latter's `COMPARISON-run1-vs-run2.md` established that
two independent swarms reproduce the content layer (positions, chains, cruxes) strongly even when
personas differ.

**Structural-review parallels (`v0/*-graph-v2/`).** A later review pass rebuilt each of the four
flagships as a structural-review parallel — `debate-graph-v2`, `eggs-graph-v2`, `blackholes-graph-v2`,
`covid-graph-v2` — with tightened argumentative structure (cleaner layering; the four lint clean, with
zero hubs/orphans/malformed sets). Each is a self-contained dir with a reproducible `build.py`, replayed
ratings, and a Haiku quorum fill, and rebuilds through the current engine (so it carries both the
`histogram` and `ghost_eligible` fields). The originals are left untouched as the assessed-of-record
artifacts; the v2 set is the cleaner-structure reference.

### 6.2 The experimental line (the assessment investigation)

The assessment research (§4–§5) runs on its own large series of experimental graphs, indexed and
narrated from **`v0/README-assessment.md`** and the reproduce list in **`v0/FINDINGS-SYNTHESIS.md §14`**.
Each has its own `events.jsonl`, `graph.json`, `harness/`, and `*-FINDINGS.md`:

- **`v0/gold-eggs/`** (17 nodes) — the hand-seeded first-pass *gold reference*, authored by Fable
  playing three agents through the real CLI. The historical seed the whole eggs line grows from; its
  FINDINGS is the original grammar falsification log.
- **`v0/eggs-p2 … eggs-p10/`** — the reputation/assessment run series (p2=50, p3=60, p4–p10=79 nodes on
  a saturated shared scaffold). p3 first surfaced tyranny-of-the-median; p4 is the flagship negative
  result (volume doesn't rescue expertise); **p5's 8-Sonnet-expert panel is the reused truth-oracle for
  p6–p10**; p6 is the biased-population flywheel; p7–p10 are the balanced 2×2 disposition×capability
  de-confound (disposition dominates capability; the camp axis tracks belief, not model, at every
  detectable divide, with no axis rotation).
- **`v0/eggs-adversarial/`** — the offline dose-response red-team (42 real good-faith raters +
  synthetic attackers; the "correlation hides a coordinated level-shift" methodology lesson).
- **`v0/eggs-p8-deliberation/`** — the deliberated-panel anchor prototype (Fable+Opus forge anchors).
- **`v0/eggs-external-check/`** — the external-grounding check (does the model oracle track the
  documented real-world record? yes, in this domain) + the panel-size curve.
- **`v0/eggs-coop/`** (37) & **`v0/eggs-full/`** (27) — the fuller-buildout second pass (5 of 7
  first-pass grammar frictions dissolved with more scope).
- **`v0/covid/`** (27 nodes) & **`v0/covid-adversarial/`** — the **real-agent** adversarial second
  domain: a smaller two-layer covid graph (source-facts both camps accept + interpretive cruxes) with a
  *real blind sleeper-attacker bloc* (not synthetic); this is where the over-certainty attack and the
  certainty guardrail were found (`covid-adversarial/FINDINGS.md`). Distinct from the 109-node
  `covid-graph/`.
- **`v0/coldstart-lab/`** — cold-start & scale (the two-quantities result, newcomer budgets, sparse
  propagation; nine e1–e10 scripts).
- **`v0/dispersion-regimes/`** — the §5.1 correction (dispersion is a valid contested signal only when
  between-group variance dominates; the diagnostic is the variance *fraction*).
- **`v0/review/`** — a fresh-eyes adversarial audit of the whole branch: the negative results reproduce
  byte-for-byte, but several headline *positive* numbers are flagged as partly true-by-construction —
  an honesty check we kept in the repo rather than burying.

---

## 7. The debate-graph — the tool arguing about whether the tool works

The FLF competition intro *itself cites* Scott Alexander's essay **"Your Attempt To Solve Debate Will
Not Work,"** whose thesis is that projects exactly like this one are doomed. So we built the Reasonable
graph *of that debate* (`v0/debate-graph/`, `REPORT.md`): a faithful steelman of Scott's seven
sub-arguments, the project's counter-position, and honest concessions where Scott is right (three of
them citing *our own* retired findings), then blind-panel-assessed it (12 Sonnet raters, 4 lenses × 3
seeds). Provenance is honest — the ACX post is paywalled and post-cutoff, so Scott's side is a
faithful steelman reconstructed from his cited examples and related essays, noted in the report.

The assessed map behaved exactly as the design predicts, which is the whole point:

- **It refused to declare a winner and converged the diverse panel on the reframing.** Both partisan
  theses land genuinely contested and near the middle (Scott's "won't work" 2.66; Reasonable's "adds
  value" 2.93); the single strongest agreement in the graph is the **dissolution** — *"whether it
  works depends on what you demand of it"* (3.91, agreed across all four lenses).
- **The deepest disagreement isolated itself as a value-crux.** The two Ought nodes (*"a faithful map
  is worth building even if it never changes minds"* endorse 3.84 vs *"only worth it if it changes
  minds"* endorse 1.95) are the two highest-dispersion nodes, split along the *value* axis (skeptic vs
  values lens), rated on **democratic endorsement** — the skeptic's dissent preserved, not
  steamrolled.
- **It settled exactly where the facts are settled** — the evidence and the honest concessions are
  the lowest-dispersion nodes.

Scott's deepest point is that *values, not facts, generate the disagreement, and no map resolves
them.* The grammar's response is to put that very value-generator on the board as an explicit Ought
antithesis, rated democratically — **located but not resolved.** The graph enacts the project's own
thesis about what "working" means, on the debate about itself. It is a direct hit on the *insight /
critique-with-counterexample* dimension and a showcase of *transparency* (the graph argues against
itself).

---

## 8. How this maps to the FLF competition

Against the competition's seven judging dimensions, the work is strongest on:

- **Methodological transparency** — every FINDINGS doc names its own limits; we revised our own
  claims on new data (§5). This is the clearest suit.
- **Adversarial robustness** — the dose-response, the sleeper, the over-certainty attack, the built
  detectors; failure modes named and bounded (§4.4).
- **Insight contribution** — comparative methodology study + counterexample-driven critiques (align
  buries the sharpest; discrimination inverts on bias; the sleeper defeats calibration; MAE hides the
  over-certainty attack) + the debate-graph.

with real support on epistemic uplift (the report-vs-graph head-to-head), generalizability (three case
shapes), compounding (append-only graph, reusable anchors, per-region reputation), and scalability
(oracle spend scales with contestedness not graph size; the tiering hybrid). The submission-shape fit
is a **comparative analysis of ≥2 assessment methodologies on the same sub-questions** plus a
**critique-with-counterexample** — two of the rubric's named prize-worthy shapes.

---

## 9. Where this could go next

The engineering roadmap the adversarial runs pointed to is **`v0/ROADMAP-NEXT-VERSION.md`** (deferred
past the deadline, deliberately). Ordered by leverage:

1. **Live-wire the certainty guardrail** into the aggregator as a first-class flag/escalation, and
   tune its sensitivity against an adaptive attacker (the detector is built and tested; it isn't yet
   wired into the running pipeline).
2. **The extremity/tightness second-stage detector** — turn the measured coordinated-extremity signal
   into a two-stage detector so an honest same-side camp isn't tarred with a manufactured bloc.
3. **Denser, rotating, hard-to-predict anchors** over the contested frontier — the sleeper's entire
   edge is knowing the anchor set; secret rotating anchors degrade it back toward the defended naive
   attack. Fundamentally a coverage/economics problem, not an algorithm.
4. **Firm up the findings before leaning on them** — replicate the refusal asymmetry properly
   (multi-question, multi-model, larger n), and build an **adaptive/harder red-team** (every attacker
   so far is static and one-shot — a floor on attack strength, not a ceiling).

Beyond the roadmap, three research threads would most raise our honest confidence (currently ~60–65%
that the assembled machinery is robust for a real deployment; high on tested mechanisms, lower on
transfer to the messy real thing):

- **A human-rated slice** — the only thing that breaks the model-on-model circularity (the whole
  ground-truth chain is model-generated except the thin external check). Highest-value gap.
- **An end-to-end longitudinal run** — the assembled flywheel over many rounds with real churn; never
  yet run live end-to-end (the integration is untested even though the components are validated).
- **The viewer** — the entire §3 lifecycle (ghost grey/z-sink, normalized-strength layout,
  competitive-comparison rendering, the type poll and endorsement cues) is specified and data-ready in
  `v0/HANDOFF-TO-UI.md` but lives in a separate UI thread. Rendering it is what turns the data layer
  into the actual "Wikipedia for arguments" experience.

There is also a standing vision note, **`v0/SITE-VARIANTS-CONCEPT.md`** (open/in-house site variants,
benchmarks, and the reality-refereed math frontier), for where the concept goes past v0.

---

## 10. Where everything lives (quick index)

**Concept & background**
- `Reasonable - Concept Overview.html` (repo root) — the full concept synthesis (read for the vision).
- `Reasonable - Claims Index.html` (repo root) — a bullet-by-bullet census of the concept's claims.
- `v0/BUILD-SPEC.md` — the frozen data-model contract (events/graph/config).
- `Feature Discussions.md` (repo root) — the design-log narrative.

**Grammar & authoring**
- `v0/AGENT-GUIDE.md` — rater/author rules, verb reference, worked example, rating dimensions.
- `v0/SPEC-evidence-argument-ought-ghosts.md` — the Evidence/Argument/Ought + poll + ghost + lint spec.
- `v0/FORUMS-SPEC.md`, `v0/PHASE2-SPEC.md`, `v0/GRAMMAR-PASS.md`, `v0/LINT-REVIEW.md` — supporting specs.

**Code**
- `v0/graph.py` — the CLI (single interface).
- `v0/reasonable/` — the package (store/fold/validate/ops/queries + assess/assessment/lifecycle/heat +
  typepoll/decompose/contested/chain). Tests in `v0/reasonable/test_*.py` and `v0/tests/`.

**Assessment research**
- `v0/FINDINGS-SYNTHESIS.md` — the complete synthesis (read first for the research arc).
- `v0/ASSESSMENT-SPEC.md` — the frozen assessment contract + amendments.
- `v0/README-assessment.md` — the map of the experimental directories.
- `v0/ORACLE-BUDGET-POLICY.md` — where to spend scarce oracle points at scale.
- `v0/eggs-p3…p10/`, `v0/*-adversarial/`, `v0/coldstart-lab/`, `v0/dispersion-regimes/`, `v0/review/`,
  `v0/eggs-external-check/`, `v0/eggs-p8-deliberation/` — the runs + per-run FINDINGS.

**Content graphs**
- `v0/eggs-graph/`, `v0/covid-graph/`, `v0/blackholes-graph/`, `v0/debate-graph/` — the four flagship
  graphs (each with `harness/` + a REPORT/COMPARISON where applicable).
- `v0/covid/`, `v0/covid-adversarial/`, `v0/swarm-blackholes*/` — the adversarial/build runs behind
  covid and black holes.
- `v0/sources/` — the curated source packs.

**Submission & forward**
- `v0/ROADMAP-NEXT-VERSION.md` — deferred next-version engineering.
- `v0/SITE-VARIANTS-CONCEPT.md` — the longer-range vision.
- `v0/HANDOFF-TO-UI.md`, `v0/VIEWER-SPEC.md`, `v0/README-viewer.md` — what the viewer needs to render.
