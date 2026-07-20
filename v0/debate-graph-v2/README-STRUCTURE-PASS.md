# debate-graph-v2 — the "best version" structural rebuild

*2026-07-17. Round 2 of the argument-structure pass. An **experimental** parallel of
`debate-graph/` (the original is untouched) holding the best version we can currently put of the
"does argument-mapping work?" question into the graph structure. Unlike production graphs — which
are append-only and supersede-to-ghost rather than delete — this clone is **rebuilt from scratch**
by `build.py`, and pieces that didn't meet the structural standard are simply absent. That is
deliberately not how the production site will operate; it's how we find out what the standard
should be so production never generates malformed nodes in the first place.*

Reproduce: `python3 debate-graph-v2/build.py` (from `v0/`) — wipes and rebuilds this directory,
then replays the original blind panel's ratings from `../debate-graph/events.jsonl`.

## The standard applied

1. **Abstract, self-contained claims.** No named critic, no named project, no assumed knowledge of
   the overall question. Every node reads on its own to a reader who knows nothing of the
   surrounding dispute (e.g. the old "its intended user barely exists" is now "Almost no one
   actually wants to argue more rigorously…"). Brand-specific mechanism references
   ("reputation-weighted", named subsystems) were removed or generalized.
2. **One proposition per node; inference lives on edges.** Every "X, so Y" bundle was split
   (over-determination → "positions are over-determined" + "flipping one point moves no one") or
   trimmed to the claim, with the inferential clause now carried by the edge (e.g. the old
   "…which resolving atomic premises does not touch" clause is now just the edge from the
   weighing-claim to "maps settle the wrong thing").
3. **The argument happens in the structure.** Both root theses rest on exactly four intermediate
   **limbs**, mirrored across the two sides — form / object / viability / history-and-concessions
   — with the leaves attached to their proximate limb, not the salient root:
   - skeptic: *maps assume a shape arguments lack* · *maps settle the wrong thing* · *not viable
     in practice* · *the concessions cut against it*
   - advocate: *a richer grammar fits real argument* · *locate the crux, don't resolve it* ·
     *a viable route and audience exist* · *the conditions have changed*
4. **Antitheses only where claims are genuine rivals** (at most one can be right). Four of the
   original ten sets were challenge-answer pairs whose members can both be true
   (values-generate-disagreement ↔ values-representable; no-false-fact ↔ jettison-modeled;
   nobody-wants-rigor ↔ built-for-readers; over-determined ↔ many-grounds-native) — those
   pairings are **not** rivalry and were dropped; the real rivalry between the two cases now sits
   at the limb level. Seven sets remain: the root triple, four limb/leaf rivalries, the
   history pair, and the ought value-crux.

## Ratings

The original 12-rater blind panel's Agreement ratings are **replayed** (348 of 384) onto every
node whose proposition survived the rewrite intact — reworded, de-branded, or trimmed of a clause
now carried by an edge, but the same claim. The 36 skipped ratings belong to the three split
parents (the two-claims-in-one nodes for user-demographics, internal-rating-limits, and
over-determination), whose children are new claims and start unrated, as do the eight limb nodes.
Headline numbers are unchanged: skeptic thesis 2.66, advocate thesis 2.93, the dissolution 3.91
(still the strongest agreement in the graph), oughts 3.84 vs 1.95.

## Removed outright (production would ghost these)

- The two-claims-in-one parents and the 13-ground direct fan on the skeptic thesis (replaced by
  the limb layer; round 1 had kept them as ghosts).
- The four non-rival antithesis pairings above.
- In-text references to the specific critic, the specific project, and this graph's
  self-demonstration parenthetical.

## Deferred / open

- The dropped challenge-answer pairings arguably deserve a first-class "responds-to" relation —
  the grammar currently has no way to say "this claim answers that one without rivaling it".
  That's a known friction (`flag-friction` territory) worth testing on other graphs.
- New nodes (limbs, split children) are unrated; a fresh panel round would complete the surface.

## Round 3 — quorum rating panel (2026-07-17)

An 8-rater blind Haiku panel (the 4 lenses × 2 seeds, bloc `cheap`, per the tiering-study protocol
of holding lens diversity constant) filled every rating gap the rebuild left: Agreement on the 16
new nodes (limbs + split children), Reasonableness + Clarity on all 45 phrasings, and conditional
Agreement on all 43 edges — 1,192 ratings, zero abstentions, plus a follow-up mini-pass on the two
late-added is→ought edges. **Every node, phrasing, and edge in the graph is now at or above
quorum 5** (all `provisional`). The carried Sonnet-panel Agreement on the 29 surviving original
propositions was left untouched; per the tiering findings, Haiku means are direction-reliable but
confidence-compressed, so the two arms are kept distinguishable by bloc.

Notable readings:

- **The limb layer holds up.** Both sides' limbs rate as real claims (skeptic: form 3.75, object
  3.79, concede 3.54; advocate: grammar 3.79, locate 3.86, conditions 3.79) — except the two
  *viability* limbs, which sit weakest and closest (2.81 skeptic vs 3.08 advocate): the panel
  reads practical viability as the genuinely open sub-question.
- **The split children now carry distinct signals** — e.g. "Positions are over-determined" (3.96)
  vs "People don't want rigor" (3.07): the old bundled parents were averaging over genuinely
  different levels of support, which is what the splits were for.
- **The ought wiring rated asymmetrically**: "adds value → worth building" e042 = 3.81, but
  "won't improve → only mind-changing counts" e043 = **2.25**, the weakest edge in the graph —
  the panel judges that even granting the skeptic thesis, it only weakly supports the strict
  mind-changing criterion of worth (a value premise empirical claims can't carry alone — Hume,
  observed in the wild).
- **Weakest original edge**: "two thousand years unsolved" → "not viable" (2.88), consistent with
  the 2000-years claim itself being the lowest-rated leaf (2.35).
- **Structural contested verdict**: exactly the antithesis members (roots, rival limbs, the
  history pair, the detail pair, the value-crux) are contested; every concession, evidence node,
  and framing claim is settled — settled-where-facts-settle, contested-where-rivals-meet, as
  designed.
- **R/C landscape is uniformly high** (R 3.75–4.38, C 4.1–4.5) — consistent with the round-2
  rewrite having done its job, and with a same-author-pass ceiling effect worth keeping in mind.

## Could Sonnet-level build agents produce this structure directly? (elicitation analysis)

The v1 debate graph was itself built by a Sonnet-class agent flow — so the hub, the bundled
nodes, and the loose antithesis pairings were not capability failures. Nothing in this rebuild
required judgment a Sonnet build agent lacks; what changed was the *procedure*. That makes the
gap look harness-shaped, not model-shaped, and suggests a viable path:

1. **Skeleton-first, two-phase builds.** The single highest-leverage change. The limb
   architecture (form / object / viability / history) was decided *before* any leaf was authored,
   and every leaf then had an obvious proximate attachment point. Harness: a planning agent
   proposes the thesis + limb decomposition for each side; build agents may only attach a leaf to
   a limb (or propose a new limb), never directly to a root thesis. Hubs become structurally
   impossible rather than lint-flagged after the fact.
2. **A testable standalone-claim rule.** "Write the claim so it reads on its own" is vague;
   "a fresh agent shown ONLY your claim text must be able to parse it without knowing the
   question or the actors" is checkable — a one-shot Haiku probe per node at author time. The
   same probe catches named-entity dependence ("Scott's example…") mechanically.
3. **A two-assertion probe at the write boundary.** The soft ~350-char warning is the current
   grain signal, but length is a weak proxy. A cheap classifier prompt — "does this text assert
   more than one independently rateable proposition? if so, state them" — run on every
   `create-node`, would have caught all three of v1's bundles, and its output *is* the split
   proposal. Belongs in `validate.py` as an advisory warning with the candidate split attached.
4. **A both-true gate on antitheses.** Before `add-antithesis`, require the agent to answer:
   "could both members be true at once?" If yes, it's a challenge-answer pair, not a rivalry —
   file the friction (or, once it exists, use a responds-to relation) instead of the set. All
   four of v1's non-rival pairings fail this one-line test.
5. **Titles as part of the authoring contract.** Requiring a ≤8-word scannable `--title` at
   `create-node` costs nothing and forces the author to find the claim's centre of gravity —
   several v1 bundles would likely have been caught by the author's own inability to title them.
6. **A periodic whole-graph editor round.** Abstractness and mirrored architecture need the
   whole graph in view; incremental authoring can't see them. Schedule a structure-editor agent
   every N build rounds with the full blind packet and the standard above, producing
   split/re-route/demote proposals executed through the normal competing-path + supersede verbs
   — this rebuild, run as a production-safe editorial pass.
7. **Rating-granularity nudge (from round 3).** The engine stores tenths and the Sonnet panel
   used them (32 distinct values), but the Haiku swarm self-compressed to .0/.5 on 99% of its
   1,192 ratings. Rater prompts must say explicitly: rate in tenths; 3.7 and 4.2 are normal
   values. Cheap raters take the coarseness of their scale from the prompt, not the tool.

Items 2–5 are cheap, mechanical, and retrofit onto the existing write path; items 1 and 6 are
harness patterns already compatible with the workflow runners in `harness/`. The honest open
question is whether skeleton-first survives contact with messier questions (eggs/covid, where
the limb decomposition is less symmetric than a critique-vs-reply debate) — extending this
treatment to those graphs is the direct test.

### Tested — the harness experiment (`../elicit-harness/`, full writeup in `COMPARISON.md`)

The analysis above was turned into a runnable harness (`elicit_build.js`) and tested: a Sonnet flow
built the debate graph from **unstructured source prose**, scored against the naive v1 (no harness)
and this hand build. Two rounds, and the results confirm the central claim while sharpening it:

- **Skeleton-first and mandatory titles are validated as robust wins.** Both runs of the harness
  produced **zero hubs** (v1 had a 13-ground star; max in-degree fell 13→4) and **100% titled** nodes
  (v1: 12%). These are deterministic, judge-independent, and identical every run — the two pathologies
  that most needed hand-fixing are eliminated by procedure alone. The planner also reproduced the
  mirrored form/object/viability/history limb architecture unaided.
- **The authoring checks help but each needed a second tuning pass.** Round 1 found bundling
  concentrated in the *unchecked skeleton* (the leaf checks ran, the planner's roots/limbs didn't);
  adding a **skeleton-refinement pass** (item 2 applied to the skeleton) visibly de-bundled the roots
  but left *enumerative* limbs bundled — a limb should be a **category label** ("the conceded
  limitations bear against it"), not a list of its contents. And an **antithesis-recall** fix
  recovered the genuine rivalries v1 missed (viability/demographic/history) but over-generated
  **duplicate** sets — recall needs a dedup / one-set-per-sub-question guard, a defect distinct from
  the both-true (non-rivalry) gate.
- **The sharpest new finding is about measurement, not building.** A single cheap LLM probe scoring
  "bundled?" / "genuine rival?" is **too noisy to trust** — rerun identically it swung ±13–28 points
  on the *same* graph (the hand build's bundled rate read 16% one run, 31% the next). A deterministic
  regex proxy is *biased* rather than noisy (it flags the hand build as most-bundled). So **cheap
  structural-quality QA is itself unreliable** — the same multi-rater/structural lesson the assessment
  layer learned (§4–§5), now recurring for *build* quality. Reliable build-QA needs a probe **panel**
  (averaged) or deterministic topology, not one cheap judge — and the trustworthy comparison stays on
  the deterministic-topology metrics (hubs, titles, altitude, counts) plus targeted inspection.

Net: the v1→hand gap is confirmed **harness-shaped, not model-shaped** — a guided Sonnet build clears
the load-bearing pathologies from raw prose. The residual is two small harness guards (limb-as-label
refinement; antithesis dedup) and a better ruler.

## Round 4 — shared premises (reconnecting the two sides, 2026-07-18)

A structural gap the owner spotted: the graph was **two almost-unconnected trees** — a skeptic tree
(→ "mapping won't improve debate" → the ought "only mind-changing counts") and an advocate tree
(→ "a faithful map adds value" → the ought "a faithful map is worth it") — joined only by antithesis
(rivalry) sets. Zero of the 45 nodes reached more than one root. But a well-formed argument between
two legitimate sides should also show the **common ground** both accept and then diverge over; an
all-divergence graph is under-modeled.

The shared premises turned out to be already present — as skeptic-side descriptive leaves the
advocate in fact *accepts and reframes* — just never connected across. Five cross-link edges fix it
(no new nodes):

1. **The value-crux fork.** "An argument map produces a durable shared artifact but does not, by
   itself, make the parties agree" (n021) now grounds **both** oughts. The disagreement is thereby
   isolated to the *value* — worth building anyway (n044) vs only-if-it-changes-minds (n045) — both
   forking from the same conceded fact, exactly the design thesis that the deepest split is a
   value-crux, not a factual one.
2. **Weighing / values.** "The load-bearing work is weighing magnitudes" (n010) now also grounds
   "the map's job is to locate the weighing" (n032); "values generate the disagreement" (n012) now
   also grounds "give values a first-class home" (n034). Both sides accept the premise; only the
   consequence (does it doom mapping, or define its job?) diverges.
3. **Over-determination.** "Positions are over-determined" (n013) now also grounds "the grammar holds
   over-determination natively" (n029).

Result: **5 nodes now reach both oughts** (was 0) — n010, n011 (the lockdown example under it), n012,
n013, n021 — so the two trees share genuine roots. Lint stays clean. The five new edges start unrated
(conditional Agreement); a small re-rate brings them to confidence. All existing ratings are
preserved (the edges were appended to the log; `graph.py rebuild --data debate-graph-v2` reproduces
the snapshot).

## Round 3 (2026-07-19) — the strengthened rebuttal, after reading the actual post

The project owner supplied the full text of Scott's post; the reconstruction held on every
load-bearing point, and a strengthened round of replies (plus a squarer concession) was added and
blind-rated like everything else: 11 new nodes (n046–n056), 12 edges (e049–e060), one new rival in
set s6, rated by a fresh 8-rater panel (4 lenses × 2 seeds, tenths resolution, lens-tagged blocs).

What the new material argues, in brief: collective understanding shifts through the *audience*, not
the arguers (the Wikipedia precedent); a public record of weak arguments raises the discourse floor
even when no individual changes their mind; no one — however capable — holds a complete map plus
accurate weights in their head (grounded by Rootclaim's memorized-knowledge complaint); the
consensus-vs-truth gap is a limit on *every* format, which supports the dissolution rather than
either side; single-point contributors and side-defenders plus AI authorship supply coverage without
Scott's nonexistent "wants to argue rigorously" user; a faithful map cannot be simpler than the
dispute (explicit-vs-implicit is the real choice, added as a rival in s6); and — conceded squarely —
a complete map is genuinely hard to take in and can tempt single-link fallacy-hunting (n056,
grounding Scott's side).

The panel did not flatter the builders. Near-unanimous: the concession n056 (3.79, sd 0.11) and the
universal-limit claim n052 (3.79, sd 0.14 — strongest edge into the dissolution at 4.06).
Strong: n050 no-one-holds-the-whole-map (3.71) with its Rootclaim evidence (3.54); the
audience-shift → third-parties edge (4.26). Merely plausible, honestly: the audience-shift mechanism
itself (3.05) and the Wikipedia tipping-point precedent (2.75). Weak, and kept that way: the
supply-channels claim (1.97 — raters read "full coverage" as overclaimed) and the discourse-floor
prediction (2.26). n055 explicit-beats-implicit correctly reads *contested* as the new rival in s6.
Lint: 0 hubs / 0 orphans / 0 malformed sets (one advisory: n050 is negation-phrased by nature of a
capability-limit claim). Graph: 56 nodes / 60 edges / 7 sets; states 16 contested / 40 settled at
confirm=8, static.

## Round 4 (2026-07-19) — structural pass over the round-3 additions

Round 3 strengthened the *content* but attached most of its new claims **directly to the root
conclusion n002**, which had grown to 7 direct grounds (one shy of the hub line) and broke the
deliberate round-2 **mirror**: n001's four critique limbs (form / atomic-premises / not-viable /
concessions) answered by n002's four (n027 / n031 / n035 / n039). A structural pass re-seats the new
grounds on the limbs they actually belong to — *support-only edge moves, no node or text churn*:

- **n049** (a public record of weak arguments raises the discourse floor) → now grounds **n046**
  (change comes through the not-yet-committed audience), the mechanism it is an instance of, instead
  of the root.
- **n054** (trusted essayists prove a fair survey is valuable; a map democratizes it) → now grounds
  **n035** (a viable audience and production route exists).
- **n055** (a faithful map is irreducibly complex; explicit beats implicit) → now grounds **n027**
  (the form limb); it is already the s6 rival to n008, so its support belongs on the form answer, not
  the root.
- **Redundant shortcut demoted:** e052 (n048→n035) — n048 already reaches n035 via n046→n036, so the
  direct edge duplicated the path.

Result: **n002 is back to exactly its four mirrored limbs** (n027, n031, n035, n039); no node exceeds
5 grounds (max is n020 at 5); redundant paths drop 2→1 (the one remaining is the *intentional*
shared-premise edge n021→n045). The three re-seated edges start unrated (conditional Agreement) and
go to the next Assessment batch; all node ratings are preserved (edge moves only).

Also proposed a **positive alternative phrasing for n050** (the sole advisory negation-flag —
"*A complicated dispute contains more claims, connections, and strength-judgments than a person can
hold in their head at once…*"); it becomes primary only if it rates at least as clear/reasonable as
the original, so it rides the same re-rate rather than being forced.

**Bundle splits (executed — Submission gave the go, split-and-rate).** Two round-3 nodes each said
more than one thing; both were superseded and split into atomic claims:

- **n053** ("Coverage without debaters") packed *point-droppers* + *side-defenders* + *AI-authorship*
  (the last already carried by n037, so dropped). Split into **n057** ("Point-droppers supply
  coverage" — single-point contributors) and **n058** ("Side-defenders supply coverage" — partisans
  arriving when their side is visibly losing), both grounding n035. The old bundle rated a low 1.97
  (raters read the merged "full coverage" as overclaimed); the two atomic claims can now be judged on
  their own.
- **n056** bundled *maps are hard to take in* + *heavy use tempts treating one weak link as defeating
  an over-determined argument*. Split into **n059** ("Maps are hard to take in") and **n060** ("Maps
  tempt single-link over-defeat"), both grounding n008. The second half (n060) is a genuine rival to
  advocate **n030** (graded support means a dropped link doesn't collapse the argument), so it now
  sits with n030 in a new antithesis set **s8** — a mushy concession turned into a legible crux.

Result: **58 active nodes**, lint clean (0 hubs / 0 orphans / 0 malformed), max in-degree 5 (n020,
n035). The four new claims + their edges + the s8 membership + the three re-seated edges from the
first round-4 pass + R/C on the n050 rephrasing all go to Assessment's round-4 blind batch; every
existing rating is preserved (splits supersede, never rewrite).

## Round 4 (2026-07-19) — the splits, rated

Round 3's two bundled nodes were split (PR #77) and the full round-4 surface blind-rated by a fresh
8-rater panel (4 lenses × 2 seeds, tenths): 4 split nodes (A + R/C), the 4 new edges + 3 re-seated
edges from PR #76 (conditional A), and the n050 positive rephrasing p1 (R/C).

The split verdicts confirm the un-bundling call. The old "coverage without debaters" bundle (1.97)
split into point-droppers **n057 = 3.29** and side-defenders **n058 = 2.29** — both above the
bundle, and the weak half now isolated (raters doubt partisans supply the *strongest available*
counter-arguments). The old concession bundle (3.79) split into hard-to-take-in **n059 = 4.39,
sd 0.06** — the most tightly agreed claim in the graph — and single-link-over-defeat **n060 = 3.84,
contested**, as it should be: it now stands in antithesis set s8 against the graded-support reply
n030, the hidden crux made legible. Edge data sharpened too: granting "hard to take in" barely
supports "adding circles makes it worse" (e066 = 1.63) while the over-defeat worry strongly does
(e067 = 4.14) — the panel separates difficulty from harm. One honest low: the re-seated
e063 (explicit-beats-implicit → the form limb) rated 1.59; the panel reads that support as weak,
and the edge stays, visibly weak, as the grammar intends. The n050 rephrasing p1 rated well on
clarity but did not overtake p0's cumulative standing; the negation-phrased original remains
primary. States: 18 contested / 42 settled; lint clean (0 hubs / 0 orphans / 0 malformed).

## Round 5 (2026-07-20) — the original panel, re-elicited at tenths

Post-submission resolution fix. The original 8-rater panel (`haiku-{epistemic,pragmatic,values,
skeptic}-{1,2}`) had cast its 1,232 ratings almost entirely at whole/half-point grain — an
instruction gap, not a judgment about the scale (the round-3/4 panels rated at tenths). Round 5
re-elicited the **same 154 targets** (16 limb/leaf nodes + 48 edges on Agreement; 45 phrasings on
R and C) from the **same agent ids**, blind, from a packet regenerated off the current graph
(`harness/packet-round5.md`, spec in `harness/round5.json`), with one instruction delta: rate on a
continuous 0.0–5.0 dial at tenths, don't snap to .0/.5. Same era, so each new rating supersedes
that agent's old value in place — the event log keeps both, as always.

Stated plainly: **this is a re-elicitation, not a reformatting** — the ratings are new judgments by
the same panel under a finer dial, and the numbers moved accordingly. All 64 Agreement targets in
the assignment shifted (median |Δ| 0.14, mean 0.19); the largest single move was e043 (2.25 → 3.30),
and e002 softened 4.31 → 3.79. **No lifecycle state changed** (still 18 contested / 42 settled), no
primary phrasing flipped, and the root theses are untouched — n001/n002/n003 and the s7 oughts were
never this cohort's targets, and their numbers are unchanged. Effective finer-than-half-grain
ratings across the whole graph: 28% → 76.5%. Panel mechanics: four raters initially skipped
e046–e048 and were re-prompted for exactly those targets, and one had rated three out-of-assignment
targets, removed as out of scope (details in `harness/round5.json`); all 1,232 ratings applied
through the CLI write boundary with zero failures, lint unchanged, both test suites green.
