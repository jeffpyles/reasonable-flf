# Reasonable phase 2 — Assessment-maturity mechanics (the contract)

This is the build contract for the **phase-2 assessment-maturity layer**: the mechanics that let the
graph express *how well-assessed* a claim is — coverage, dispersion, activity/settledness, eras of
re-opening on new evidence, replicate sampling, chain strength. It extends the v1 assessment layer
(ASSESSMENT-SPEC.md) the same way that spec extended BUILD-SPEC.md: everything here is **additive** —
no v0/v1 data format, verb, or semantic changes, only new fields, new verbs, and new derived
measures. Design rationale lives in `../Feature Discussions.md` Entries 19–27; this file is the *what*.

> **Note (scope):** an earlier version of this spec also contained an adversarial/manipulation-
> defense layer (manipulation detectors + a red-team "anchor experiment"). That work has been
> **sequestered to the `adversarial-defense-archive` branch** — it is out of scope for the FLF
> submission and preserved there in full. What remains here is the cooperative assessment machinery,
> which is normal site function even with entirely good-faith users. (The **reputation** system —
> True_R, alignment-weighting — is likewise cooperative and stays; it just tells the site who is
> tracking the evidence most carefully, among users all doing their best.)

Status of each mechanic: **[BUILD]** = build now; **[DEFER]** = spec'd for completeness, not in this build.

---

## 1. Item lifecycle: sealed → provisional → settled / contested / reopened

Every rateable target (node A, edge A, group A, phrasing R/C) carries a **coverage state**,
computed in the fold:

- **sealed** — fewer than `quorum` ratings (default **5** = one bloc; `--quorum` on rebuild to
  configure). While sealed, `graph.json` carries the ratings (the log is public) but the
  **aggregate mean is withheld** from the default read surfaces: `get-node`/`neighborhood`/viewer
  show "n ratings, pending quorum" instead of a number. An `--include-sealed` flag on read verbs
  exposes means for the analysis harness. Rationale (Entry 25): assignment concentrates on exactly
  these items, so during the rating window there is nothing to peek at — release is *sequenced*,
  not hidden.
- **provisional** — quorum met, fewer than `confirm` ratings (default **15** = three blocs).
  Aggregate shown, marked provisional.
- **settled** — coverage ≥ `confirm` AND the item's node is *cold* (temperature below the
  site-relative threshold, §3). Cold-and-uncovered is NOT settled — it is just ignored (sealed or
  provisional).
  - **Static-artifact mode (`phase2.static: true`).** In a **frozen presentation graph** (a built-
    and-rated snapshot with no ongoing editing) the cold gate is meaningless: content-heat only
    tracks *build order*, so `settled` vs `provisional` would turn on when a node was authored, not on
    any epistemic property. With `static: true` the cold gate is **skipped** — a converged,
    non-contested, coverage-≥`confirm` item reads `settled` outright. The `sealed`/`provisional`
    coverage gates (thin evidence, n < `confirm`) and the `contested` verdict are untouched, so the
    honest distinctions survive. Set on the presentation graphs' `config.json`; default `false`
    (live-wiki behavior) everywhere else.
- **contested** — coverage ≥ `confirm` but dispersion stays high (§2): added ratings are not
  shrinking the spread. Contested is a **terminal display state distinct from mid-scored**: a
  contested 3.0 and a converged 3.0 must read differently everywhere a score is shown.
- **reopened** — see §4 (eras).

**[BUILD]**: state machine in the fold; state surfaced in `get-node`, `stats`, and the viewer
(sealed = no color + "pending" badge; provisional = current rendering + badge; contested = a
distinct visual mark, spec'd as a dashed/split frame, exact treatment implementer's choice).

## 2. Dispersion & rater count (f17)

Every aggregated `(target, dim)` gains `{mean, n, stdev}` in `graph.json` (stdev of the raw
ratings, not True_R-weighted — dispersion is a fact about the raters, not about reputation).
Read surfaces show `mean ±stdev (n=N)`. **Contested** (§1) is defined as
`n ≥ confirm AND stdev > contested_threshold` (default **1.0**; configurable). **[BUILD]**

## 3. Heat: churn and settledness (Entry 25)

Deterministic heat-diffusion metric computed in the fold from event timestamps (no wall clock —
"now" for any rebuild is the max `ts` in the log, so same log → same snapshot, byte-identical):

- Every event injects heat at its node (edge events heat both endpoints; group events heat the
  `to` node). Two ledgers, same mechanics: **content heat** (create/draw/phrasing/title/comment/
  typing/friction events) and **rating heat** (rate events).
- Heat decays exponentially with half-life `heat_half_life` (default **7 days**) and, at each
  event application, a fraction `heat_diffuse` (default **0.15**) of injected heat is deposited on
  directly connected neighbors (one hop; deeper propagation emerges from chained events).
- A node is **cold** when `content_heat < cold_factor × site_median_content_heat` (default factor
  **0.5**, median over nodes with any history). Site-relative by construction.
- `graph.json` per node: `{"heat": {"content": x, "rating": y}}`; `stats` reports site medians.
**[BUILD]**

## 4. Eras — eras don't leak (Entry 27)

- Every rateable target carries an **era counter**, starting at 1. Rating events record the era
  current at cast time (assigned by the CLI, from the target's era in the folded state).
- The live aggregate for a target uses **current-era ratings only**. Prior-era ratings remain in
  the log and appear in a per-target `history` block (`[{era, mean, n, stdev, settled_seq}]`) —
  visible record, zero live influence. No carry, no re-affirmation, no damping.
- **Alignment** (reputation input) is graded per era: living while the era is open, finalized
  against the era's settlement when the item reaches **settled**, never revisited.
- New verb: `reopen --target <id> --reason "<text>"` **[BUILD]**. Increments the era, returns the
  item to **sealed**. In production, reopening is content-gated (triggered by content heat on a
  settled item); in the playground the harness calls it explicitly — the *gate* is policy, the
  *mechanics* are what we are testing. The reason string is recorded in the log (public record of
  why an era turned).

## 5. Blocs — replicate sampling (Entry 25)

Blocs are the **replicate-sampling** substrate: a target's cohort is split into small blocs so we
get several *independent* estimates of the same aggregate. Agreement among blocs is a
reliability signal (the estimate is real); divergence means genuine disagreement worth surfacing.
Bloc bookkeeping lives in the data; bloc *assignment* is the runner's job (the playground has no
accounts/sessions to assign; swarm agents are told their bloc):

- `rate` gains optional `--bloc <id>` (an opaque string, e.g. `b1`). Fold computes, per target
  with ≥2 blocs of ≥3 ratings each: per-bloc means and a **bloc-divergence statistic** (ratio of
  between-bloc to within-bloc variance, F-style) — read as split-sample inter-rater reliability.
  **[BUILD]**
- The runner assigns each rater to a bloc per item wave, m=5 per bloc, k up to 5 blocs per item,
  stratified where the population allows (Entry 25).

## 6. Small closures from Entries 25–26

- **Group rating target (f16)**: `rate --target group:<gid> --dim A` — rates the conjunction
  group's joint inference ("if ALL members were so…"). Member edges of a grouped conjunction are
  expected to be abstained (documented norm, not enforced). Group A aggregates like any other
  target; the viewer shows it on the conjunction bracket. **[BUILD]**
- **Divergence nudge**: when a `rate` lands ≥ `nudge_distance` (default **1.5**) from a visible
  (unsealed) current mean, the CLI prints a non-blocking note: consider a comment explaining the
  divergence, or add what's missing to the graph. Never a rejection. **[BUILD]**
- **Chain strength (v1)**: `chain --from <ancestor> --to <descendant> --data <dir> [--json]`
  computes, over each simple Ground-path from ancestor to descendant (cap: `chain_max_paths`,
  default 16, deterministic order): normalized product `∏ (node_A/5 × edge_A/5)` over interior
  nodes and edges (conditional edge semantics, ASSESSMENT-SPEC v1.2 — this product is the chain
  rule), the **weakest link** (min factor + its id), and per-step geometric mean. Conjunction
  groups contribute as ONE link using group A (§7a) — min over member-subchain products where a
  member has upstream structure. Unrated elements contribute the neutral 2.5/5 with a `partial:
  true` flag on the result. Viewer affordance **[DEFER]** — the verb is what the FLF writeup needs.
  Multi-path aggregation (noisy-OR) **[DEFER]** (shared-ancestor double-counting unsolved; Entry 25).

## 7. Non-goals for this build

Bandit assignment & competence fields (runner assigns; no human accounts to model), production
sortition service, temporal re-opening triggers as code (harness-invoked; §4), viewer chain UI,
noisy-OR. If tempted, add a line to FUTURE notes instead.

> **Sequestered:** the original §6 (manipulation detectors) and §9 (the red-team "anchor
> experiment" protocol) lived here and have been moved, in full, to the `adversarial-defense-archive`
> branch. They are out of scope for the FLF submission. The cooperative reference graphs those runs
> were built on (`v0/eggs-p2`, `v0/eggs-p3` — the honest populate + reputation findings) remain in
> the tree; only the attack machinery and writeups were sequestered.

---

## Amendments

- **p2.1 (2026-07-07, pre-build — heat time base):** §3's `heat_half_life` default of "7 days" is
  replaced: heat decay is measured in **site-wide events, not wall-clock time**. Half-life default
  **300 events** (of total site activity, i.e. `seq` distance), configurable via `--heat-half-life`.
  "Now" for any rebuild is the log's tip `seq`. Rationale: (a) a 20-minute swarm run under a 7-day
  wall-clock half-life never cools, so nothing can reach *settled*; (b) simulated timestamps would
  break fold determinism or force
  the runner to fake `ts`; (c) event-time makes maturity automatically relative to total site
  activity — the same design Entry 25's churn discussion already required for the 100-user vs
  10k-user scaling, now applied to the time base itself. A blended calendar component (evidence
  ages even when a site is quiet) is a possible production amendment, out of scope here.
