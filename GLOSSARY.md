# Glossary

*One-line definitions of every term of art used across this project's documents. Deeper treatment:
[MECHANISMS.md](MECHANISMS.md) for how the systems work, [VISION.md](VISION.md) for why.*

- **Agreement (A)** — the 0–5 rating of a claim's truth/support (or, for an Ought, its endorsement;
  for evidence, its fidelity to the source). One of the three rating dimensions.
- **Anchor** — a question whose answer is independently well-established, used to measure raters
  against reality rather than against each other.
- **Antithesis set** — a group of *rival positive claims* answering the same question, displayed
  stacked together. Opposition is always a rival claim, never a "not-X" negation.
- **Belief camp** — a faction of raters who systematically rate the same items in opposite
  directions from another faction, detected from rating patterns alone.
- **Blind rating** — rating without seeing the current consensus, other ratings, comments, or author
  reputation; enforced by the tool, not optional.
- **Bloc** — a tag grouping a set of ratings (e.g. by rater lens) so between-group divergence can be
  tracked.
- **Chain strength** — how strongly a conclusion is supported through a whole path of grounds, with
  each step's support compounding.
- **Claim** — the atomic unit of the map: one statement, small enough to examine on its own, in
  ordinary natural language.
- **Clarity (C)** — the 0–5 rating of how clearly a particular phrasing is written.
- **Conditional rating** — the way support edges are rated: *grant* the FROM claim as true, then
  rate how strongly it supports the TO claim.
- **`confirm`** — the minimum number of ratings before an aggregate is treated as mature; set from
  measured split-half reliability, not chosen by taste.
- **Conjunction group** — grounds marked as supporting a claim *jointly* (together, not separately).
- **Contested** — the lifecycle state of a claim with a live, structurally real rivalry (see
  antithesis set / belief camp) — as opposed to merely having noisy ratings.
- **Dependent** — a claim that follows from another; the outbound side of a support relationship
  (shown to the right in the viewer).
- **Era** — a rating epoch for a node; when a node materially changes (e.g. its type is corrected),
  old ratings are closed into a previous era rather than mixed with new ones.
- **Evidence node** — a node anchored to a source *outside* the graph (a study, a document); rated
  on fidelity to that source, with source quality rated on its outgoing edge.
- **Event log** — the append-only record of every write ever made to a graph; the source of truth
  from which the snapshot is deterministically rebuilt.
- **Ghost** — refuted or superseded material, demoted (greyed, sunk, retrievable) but never deleted.
- **Ground** — a claim that justifies another; the inbound side of a support relationship (shown to
  the left in the viewer).
- **Hume's rule** — the write-boundary check that an Ought may never be used to ground a non-Ought:
  no deriving an "is" from an "ought."
- **Lens** — a rater persona/perspective (e.g. epistemic-rigor, values-pluralist) used to make
  panels viewpoint-diverse.
- **Lifecycle state** — the at-a-glance trust label on every rated item: sealed, provisional,
  settled, or contested.
- **Ought node** — a value or action claim ("we should…"); rated on *endorsement*, one person one
  vote, never truth-weighted.
- **Phrasing** — one wording of a claim; alternative phrasings stack behind the same node, with the
  community floating the best to the top.
- **Provisional / sealed** — lifecycle states meaning "not enough ratings yet to lean on."
- **Reasonableness (R)** — the 0–5 rating of whether a phrasing is fairly and logically stated,
  kept separate from whether you agree with it.
- **Reputation (True_R)** — a rater's earned truth-tracking score, learned from anchor performance;
  weights ratings on factual claims, never on Oughts.
- **Settled** — the lifecycle state of a claim whose ratings have converged with adequate coverage
  and no live rivalry — whether the settled verdict is "strong" or "weak."
- **Sleeper** — the attack of rating anchors honestly while lying only where no anchor exists;
  the measured limit of bias-correction's reach.
- **Snapshot (`graph.json`)** — the derived, read-optimized state of a graph, rebuilt byte-for-byte
  identically from the event log.
- **Split-half reliability** — how well two independent halves of a rater panel reproduce each
  other's per-node scores; the measurement behind `confirm`.
- **`static`** — a config flag for frozen presentation graphs so "settled" reflects convergence
  rather than an artifact of build order.
- **Supersede** — the reversible demote-to-ghost operation, with the reason recorded publicly.
- **Type poll** — the community process for correcting a node's kind (claim/evidence/ought),
  resolved by reputation-weighted vote at a quorum.
