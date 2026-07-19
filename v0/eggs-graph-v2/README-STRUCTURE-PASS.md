# eggs-graph-v2 — structural-pass rebuild of the eggs graph

*2026-07-18. The argument-structure pass applied to the eggs graph. An **experimental** parallel
of `eggs-graph/` (the original is untouched), rebuilt from scratch by a committed, reproducible
`build.py`. Eggs was already structurally healthy — 0 hubs, atomic evidence-backed claims — so this
pass is deliberately conservative and surgical: it removes specific cruft and applies the standard,
without reinventing a careful scientific evidence graph or fabricating any science. Every evidence
node and interpretive claim is carried **verbatim** from the original.*

Reproduce: `python3 eggs-graph-v2/build.py` (from `v0/`) — wipes and rebuilds this directory, then
replays the original Sonnet panel's ratings from `../eggs-graph/events.jsonl`.

## What changed

1. **Retired the one bundled root.** The original `n002` asserted two independent things — "does not
   meaningfully raise CVD risk" **and** "eggs provide real nutritional benefits." It had already been
   half-decomposed into a risk half and a benefits half; this pass drops the bundle and promotes those
   two to first-class: the **risk-NO** claim now sits in the root antithesis opposite **risk-YES** and
   **unresolved**, while **benefits** becomes its own branch feeding the ought layer.
2. **De-starred the "unresolved" synthesis.** Once the interpretive leaves were wired up, the honest
   verdict node ("the causal question remains genuinely unresolved") had 9 direct grounds. Two
   intermediate limbs now carry them — *no trial evidence on real clinical endpoints exists* (the
   RCTs that could settle it are absent/impractical, and the ones we have measure only surrogate
   lipids) and *the observational evidence can't pin down causation* (mixed results,
   association≠causation, residual confounding, responder variation, subgroup confounding). Verdict
   node drops to 3 grounds; lint hubs 1→0.
3. **Typed the two value conclusions as `ought`.** "Eating eggs is reasonable for most people" and
   "a precautionary approach is warranted" were `claim` nodes bundling an is-evaluation with a
   prescription (friction f17 on the original). Each is now an `ought`, trimmed to its prescription,
   rated on **endorsement** not truth, and given an explicit value premise (`ought` grounds `ought`,
   Hume-clean): *benefits justify a modest unproven risk* vs *limit exposure under unresolved harm*.
4. **Layered the benefits.** Benefit evidence → the three benefit claims → a single benefits summary
   → the ought, instead of individual benefit claims hanging directly off the ought.
5. **De-scaffolded titles.** Dropped the "Rival:" prefix that leaked build-scaffolding into two
   node titles, and dropped the "eggs are bad for your health" framing from the risk claim's title
   (the node is the risk proposition; "bad for health" is an ought).
6. **Removed cruft.** All 14 already-ghosted edges and the spurious 1-member set and the duplicate
   risk pairing are simply absent (the from-scratch rebuild carries no ghosts).

Result: **69 nodes, 76 edges, 8 antithesis sets.** Lint: 0 hubs, 0 malformed sets, 0 orphans,
0 question-shaped. (Remaining advisory flags: the "No long-term RCTs exist" node is a legitimate
epistemic-limit claim with no faithful positive form — kept, as in the original LINT-REVIEW; and 5
redundant direct-vs-layered paths, which per that same review are rater-adjudication lane, not
mechanical edits.)

## Ratings

The 20-rater Sonnet Agreement panel is **replayed** onto every surviving proposition and edge
(1,492 ratings carried). Two categories deliberately start fresh:

- **The retyped oughts get NO carried ratings** (40 ratings reset). The original panel's 20 A-ratings
  on each were *truth* ratings of the old is/ought **bundle** — and the original graph had already
  era-sealed them for exactly this reason. An ought is rated on **endorsement**, so those truth
  ratings must not carry; the nodes start clean for an endorsement pass. (This is the category error
  the ought-typing exists to fix, caught in the rebuild.)
- **The new nodes** (2 limbs, 2 value premises) start unrated.

A blind Haiku quorum panel then fills the gaps: endorsement on the oughts + value premises, truth on
the two new limbs, top-up on the two promoted claims (Sonnet n=4 → quorum), R+C on all 69 phrasings
(the original graph carried none), and conditional Agreement on all 76 edges (Sonnet n=4 → quorum).

## Rating-granularity note

Rater prompts here explicitly request **tenths** (e.g. 3.7, 4.2). The engine has always stored
tenths and the original Sonnet panel used them (32 distinct values), but the debate-graph Haiku swarm
self-compressed to .0/.5 on 99% of its ratings — cheap raters take the coarseness of their scale from
the prompt, not the tool. (See `debate-graph-v2/README-STRUCTURE-PASS.md`.)

## Results — quorum rating panel (2026-07-18)

An 8-rater blind Haiku panel (4 eggs lenses × 2 seeds, bloc `cheap`) filled every gap: A/endorsement
on the 8 under-quorum nodes, R+C on all 69 phrasings (the original carried none), conditional A on
all 76 edges — 1,776 ratings, zero abstentions. **Every node, phrasing, and edge is now at or above
quorum 5.** The 20-rater Sonnet Agreement on carried propositions was left untouched (kept
distinguishable by bloc from the cheap arm).

**The tenths fix worked.** With the prompt explicitly requesting tenth-point ratings, the Haiku
swarm used the full scale: only **24% of ratings landed on .0/.5**, versus **99%** for the
unprompted debate-graph swarm. One sentence of prompt guidance recovered the scale's resolution —
strong confirmation that cheap-rater granularity is a prompt property, not a model or tool limit.

**The restructured graph behaves as designed:**

- **The honest verdict wins the root.** Across the risk antithesis, "the causal question remains
  genuinely unresolved" scores highest (**3.96**), above "eggs don't raise CVD risk" (3.65) and well
  above "eggs meaningfully raise CVD/mortality risk" (**1.63**). The map refuses to manufacture a
  resolution the evidence doesn't support.
- **The two de-star limbs are the strongest claims in the graph** — "no trial evidence on real
  clinical endpoints exists" **4.77** and "observational evidence can't pin down causation" 4.25 —
  which is exactly right: the epistemic-limit claims are the most defensible thing here, and they now
  carry the verdict through an explicit two-node layer instead of a 9-way star.
- **The panel is correctly skeptical of causation-from-observation.** Every "this association is a
  real causal effect" claim rates low (mortality-causal **1.79**, T2D-subgroup-causal 2.36, dietary-
  cholesterol-raises-LDL 2.09) while its confounding-interpretation rival rates higher. The lowest
  *Reasonableness* phrasings are precisely these overreaching causal claims (n038 3.75, n033 3.78) —
  the raters flag stating causation as settled fact, which is the epistemically correct critique.
- **The ought layer split cleanly on endorsement.** "Eating eggs is reasonable for most people" is
  endorsed at **3.80** vs "precaution is warranted" 2.88, and the explicit value premises divide the
  same way (benefits-justify-modest-risk 3.66 vs limit-exposure-under-uncertainty 3.20) — a real
  value split, softly favouring the permissive side while preserving the precautionary minority,
  rated on endorsement rather than truth.
- **Contested verdict**: 18 contested / 127 settled, between-group fraction 0.13. The contested set
  is exactly the antithesis members and the live cruxes (risk poles, causal-vs-confounding
  interpretations, cap-removal reading, the ought pair); the settled set is the evidence nodes and
  the epistemic-limit claims. Settled where the evidence settles, contested where the interpretations
  genuinely diverge.
- **R/C uniformly high** (R mean 4.40, C mean 4.48) with the same same-generation-author ceiling
  caveat noted for debate — the informative signal is the *ordering* (causal-overreach claims
  lowest), not the absolute level.

## Shared-premise pass (2026-07-18)

Following the debate-graph finding (rival claims should share the common ground they diverge over),
an interconnection check flagged two eggs antithesis pairs where both rivals interpret the *same*
observation but only one connected to it. Two cross-link edges fix it (no new nodes):

- **s4 (mortality signal: causal vs confounding).** The all-cause-mortality association
  ("+7%/day", n019) now grounds **both** the causal reading (n033) and the confounding reading
  (n034) — both accept the association exists; they diverge on its cause.
- **s5 (heterogeneity: confounding vs real differences).** The geographic-heterogeneity observation
  (n022) now grounds **both** the confounding reading (n035) and the real-dose/susceptibility
  reading (n036) — which previously had no grounds at all.

(s2 and s3 were checked and left alone: those rivals rest on genuinely *different* findings, not a
single shared observation, so a shared edge would overclaim.) The two new edges are unrated
(conditional Agreement) and go to Assessment's re-rate.

## Evidence-source audit (2026-07-18)

The same two-question pass applied to blackholes-v2 (overlap; secondary-aggregator sources).

**Two nodes ghosted** (a consumer-health *blog* listed as the source, restating its own dependent
claim):

- **n055** (source s15, a consumer-health/blog page) asserted eggs' protein + satiety support weight
  management — the *same* proposition as its sole dependent claim **n058**, which it grounded. A blog
  is not the source of these nutritional facts, and the claim is already carried by n058. Ghosted;
  n058 remains as a claim feeding the benefits summary n065.
- **n056** (source s15) asserted yolk lutein/zeaxanthin and reduced eye-disease risk — the same
  proposition as its sole dependent **n059**. Ghosted; n059 remains as a claim.

Both demoted via `supersede` + `rebuild`. Lint stays clean (0 hubs/orphans/malformed). Contrast the
parallel benefit node **n057** (nutrient-dense), which rests on *real* study evidence (n053/n054,
source s14) and is untouched — the audit removes blog-backed pseudo-evidence, not the benefits branch.

**Flagged, not ghosted (judgment call):** n051/n052 cite the *Harvard Nutrition Source* commentary
(s12), a reputable secondary. **n052** carries a genuine distinct fact (the 300 mg/day cap's
mid-20th-century provenance, not trial-derived) and is kept. **n051** only restates the interpretive
point its dependent n061 already makes (and which the primary guideline text n050 already grounds) —
a mild redundancy candidate, left for the re-rate/owner call rather than ghosted unilaterally.
