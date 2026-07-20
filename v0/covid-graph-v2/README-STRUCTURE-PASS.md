# covid-graph-v2 — structural audit + rating completion

*2026-07-18. The structural pass applied to the SARS-CoV-2 origins graph (133 nodes — the largest in
the repo). An experimental parallel of `covid-graph/` (original untouched). Unlike the other three
v2 graphs, this pass is **not a restructure**: covid was already de-starred into strand-aggregators
in an earlier pass and is structurally clean, so this is a **light audit that came back clean, plus a
rating-completion pass** to bring covid's rating surface up to the standard of the other three.*

Method: `covid-graph-v2` is a clone of `covid-graph` (all original ratings preserved on the shared
event log); the audit and rating fill append to it. Nothing is restructured or removed.

## The audit (came back clean)

- **Lint:** 0 hubs, 0 malformed sets, 0 orphans, 0 question-shaped nodes, 0 redundant paths.
- **Antithesis discipline:** all **17** sets were reviewed by hand against the both-true test — every
  one is a genuine rivalry ("this interpretation of the evidence" vs "the rival interpretation of the
  same evidence": market-epicenter vs ascertainment-bias, FCS-natural vs -engineered vs -lab-accident,
  restriction-pattern-synthetic vs not-evidence, and so on). **None** are challenge-answer (both-true)
  pairs. No sets demoted.
- **Bundling:** the 54 claim nodes were scanned (a crude conjunction/inference heuristic flagged 24;
  every flag was inspected). On inspection they are **single interpretive positions with inline
  reasoning or evidence-lists** (e.g. "Because major biomedical centres cluster in cities … the
  co-location is weak evidence" is one claim, not two), not two-in-one bundles. This is consistent
  with the graph having been carefully built and previously de-starred. **No nodes split.**

The honest conclusion is that the structural pass finds nothing to fix here — covid was the marquee
graph and was already built to the standard the other three had to be rebuilt toward. The value this
pass adds is completing its rating surface.

## Rating completion

The original graph carried Agreement only (a mix of n=28, n=20, and a later n=4 batch) and **no
Reasonableness or Clarity at all**, and its edges sat at n=4 (under quorum). A blind Haiku quorum
panel (covid domain lenses × 2 seeds, bloc `cheap`, tenths enforced) fills every gap:

- **Agreement** on the 24 under-quorum nodes (n110–n133, the synthetic-origin branch batch).
- **Reasonableness + Clarity** on all 133 phrasings (the original carried none).
- **Conditional Agreement** on all 187 edges (Sonnet n=4 → quorum).

The carried Sonnet Agreement is left untouched (distinguished by bloc). Results section to follow.

## Results — quorum rating panel (2026-07-18)

An 8-rater blind Haiku panel (4 covid domain lenses × 2 seeds, bloc `cheap`, tenths enforced) filled
every gap across two proven-size passes — R+C on all 133 phrasings, then Agreement on the 24
under-quorum nodes and conditional Agreement on all 187 edges. 3,817 ratings, zero abstentions.
**Every node, phrasing, and edge is now at or above quorum 5** (R/C at n=8; carried Sonnet Agreement
untouched, distinguished by bloc); 67% of ratings landed off .0/.5.

**The completed rating surface confirms the genuinely-contested case shape:**

- **The honest verdict leads, and the carried verdict is unchanged.** "The origins question remains
  genuinely unresolved" scores highest (**3.59**), above natural zoonotic spillover (**3.34**) and
  the research-related incident (**2.17**) — identical to the original Sonnet panel (those Agreement
  ratings were carried), so completing R/C and the edge/synthetic-branch ratings did not move the
  verdict. Unlike the confident black-holes case, no thesis is settled: the map holds a real
  three-way tension.
- **The newly-rated synthetic-origin branch is where the fill added the most signal.** These 24
  nodes (the restriction-site, CGG-codon, and ACE2-preadaptation "engineering signature" arguments
  and their rebuttals) were under quorum; rated out, the panel is decisively skeptical of the
  engineering-signature claims — "restriction pattern = synthetic fingerprint" **2.02** vs "not
  evidence of engineering" **3.95**; "CGG doublet = engineering signature" **1.90** vs its rebuttal
  **4.12**; "pre-adaptation suggests lab origin" **2.06** vs "sub-optimal binding indicates natural
  selection" **3.99**. Every engineering-signature claim rates below its natural-origin rival, and
  the aggregator "the engineering-signature arguments have each been rebutted" lands **3.89** — the
  branch now visibly favours natural origin on the molecular specifics while the top-level origins
  question stays open on the epidemiological and circumstantial evidence.
- **Contested where a contested question should be.** 38 contested / 282 settled (node+edge
  verdicts), between-group fraction **0.05** — a broad contested frontier (far wider than
  black-holes' 9), concentrated on the interpretive cruxes the 17 antithesis sets mark, while the
  source-level evidence nodes settle. Contested-where-interpretations-diverge, at the scale a real
  curated-debate question demands.

This completes covid's rating surface to the standard of the other three v2 graphs, with no
structural change — the audit found nothing to fix, and the fill left the marquee verdict intact
while lighting up the previously-unrated synthetic-origin branch.

## Shared-premise pass (2026-07-18)

An interconnection check (following the debate-graph shared-premise finding) confirmed covid is
already the model here — 9 of 17 antithesis pairs share the specific evidence both interpret, and
most "unshared" pairs are rebuttal pairs where the rebuttal correctly flows from its *rebutting*
evidence, not the observation. The one genuine gap was the **3-way furin-cleavage-site origin set**
(s5: natural / engineered / unintentional-lab-passage), which had no common anchor. Added one shared
node — **n134, "The furin cleavage site: a feature every origin must explain"** (the FCS is a
distinctive feature absent from close relatives) — grounding all three explanations (n054/n055/n056),
so the molecular-origin branch now forks from a shared observation. The new node (Agreement) and its
three edges (conditional Agreement) are unrated and go to Assessment's re-rate.

## Tenths re-elicitation (2026-07-20, post-submission)

The coarse-rating cohorts on this graph — the Sonnet `panel-{evidential,skeptic,domain}` (bloc
`b1`), the sixteen Haiku `{ev,skeptic,domain}-h{1..4}` (bloc `cheap`), and the two Sonnet
`skeptic-s{2,3}` (bloc `refdense`) — had rated almost entirely at whole/half-point grain. They were
re-elicited **blind at tenths** over their original live assignments (274 targets each for the
panel — including the live conjunction target `group:g1` — 109 for the cheap swarm, 69 for the
refdense pair; 2,268 total), same agent ids, same blocs, same era — supersede in place. This is a
**re-elicitation, not a reformatting**: the values are new judgments under a finer dial. The
already-fine-grained cohorts (`bayes-*`, `ev-s`, `domain-s`) were left untouched.

Effect: whole-graph finer-than-half ratings rose ~41% → 65%; 324 target means shifted (median |Δ|
0.10, max 0.86 on n092); **no lifecycle state changed** (38 contested / 96 settled); lint clean;
tests green. The load-bearing assessed verdict is preserved: zoonotic entry (n001 = 3.46) still over
lab entry (n002 = 2.29), and natural furin-cleavage-site origin (n054 = 3.48) still over engineered
(n055 = 1.83) — the consensus direction the deep-research comparison turns on. Packet + spec:
`harness/packet-tenths.md`, `harness/tenths-reelicitation.json`.
