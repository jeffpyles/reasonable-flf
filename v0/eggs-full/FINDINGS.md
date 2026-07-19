# Fuller buildout — "Are eggs good for you?" (second pass)

*2026-07-02. Extends the first-pass gold graph (`../gold-eggs/`) on the **unchanged grammar** to test
the Entry 12 hypothesis: that most first-pass "grammar insufficiency" frictions were **scope
artifacts** that dissolve when the argument is built out more completely. Interactive artifact:
the "eggs-full-buildout" link. Data: `eggs-full/graph.json` (27 nodes, 25 grounds, 3 antithesis
sets, 2 conjunctions, 16 agrees, 9 frictions); full event log in `eggs-full/events.jsonl`.*

This graph **continues the first-pass event log** (nodes n001–n017 are the first pass; n018–n027 are
this buildout), so the two are directly comparable.

## Result: the hypothesis held. 5 of 7 original frictions dissolved on the current grammar.

| Friction | First-pass verdict | After buildout |
|---|---|---|
| **F1** authority vs. evidence | grammar can't type support | **DISSOLVED** — the "guidelines dropped the cap" anchor (n007) is now grounded by the actual biological reason (n005, homeostasis). The appeal-to-authority *dissolved into the reasoning it pointed at*, as predicted. Thinness would now show as structure, not need a tag. |
| **F2** one study, many findings | no study identity | **RESOLVED** — two studies now each group two findings (`eggs-001`→n004,n013; `eggs-004`→n023,n024), plus a new `list-studies` verb to find a study id and see everything attached (for later whole-study re-weighting). |
| **F3** source-pack gaps | pack too thin | **MITIGATED** — pack expanded (added the Rong 2013 meta-analysis, `eggs-004`), and the guide now allows a free-text unverified `--source` when the pack lacks one. A test-condition limit, not a grammar one. |
| **F4** graded antithesis tension | binary membership overstates opposition | **UNCHANGED (by design)** — resolved by *scale* (wider Agreement → looser rendering), not by buildout. Correctly out of scope here. |
| **F5** undercutting defeaters | support-only can't hold "it's confounded"; node orphaned | **DISSOLVED — the headline result.** The confounding claim (n017) grew its **own positive support chain** (n018 diabetics' worse baseline risk, n019 observational≠causal, n020 adjustment attenuates) and now sits in genuine antithesis with a **balanced** causal chain (n016 ← n013, n021, n022). `stats` orphan count went 1 → **0**. No negative/undercut edge was needed. Your call was right. |
| **F6** relevance-horizon truncation | leans on LDL→CVD via one anchor | **RECEDED** — n010 (LDL causally raises CVD) now also grounded by Mendelian-randomization (n025) and LDL-lowering-trial (n026) claims. The horizon moved out a layer; it's still finite, which is expected — it recedes as far as anyone builds (Entry 10). |
| **F7** is/ought unmarked | value premise hidden | **DISSOLVED — with no rule.** The ought (n015) now carries an explicit **value-premise** ground (n027, "avoiding cheap risks is worthwhile"). Added by normal authoring, exactly per Entry 13: the grammar didn't require it; a reasoner supplied it, and the value is now its own contestable node. |

**Scoreboard:** 5 dissolved/resolved · 1 mitigated (F3) · 1 out-of-scope-by-design (F4). **Zero required a grammar change.** Strong vindication of "build it out on the current grammar; don't pivot to negative-claim edges."

## Two NEW frictions — and they're better ones

The buildout traded seven scope-artifacts for two **generative** frictions that are about *affordances*, not core-grammar fixes — and both map to things FLF explicitly rewards:

- **F8 — general principles want to be reusable nodes.** n019 ("observational data can't establish causation") is a general methodological principle bearing on *every* causal inference in the graph, but the grammar only let me attach it as a **local** ground of one node. It wants to be a single **shared/reusable node** linked from many inference points (the "wormhole"/shared-node idea), not re-authored per site. → an *additive* affordance (node reuse across regions), not a change to support-only.
- **F9 — no distinction between common ground and the crux.** n021 ("the diabetic association is real/replicated") is **common ground both rivals accept**; the real disagreement is only the causal-vs-confounded *interpretation*. The grammar marks no difference between "premise both sides share" and "the crux where they diverge." FLF **explicitly** wants cruxes surfaced (criterion 1) → a high-value additive affordance (crux/agreement tagging), still not a core-grammar change.

Both are *wishlist affordances layered on top of* the support-only grammar, not evidence against it. The core grammar is holding.

## Curated reading path (in the artifact)

1. **Neighborhood view** → see the whole 27-node territory; the causal/confounded dispute is the cluster in the lower-middle, now with balanced chains on both sides.
2. **Node view → "Diabetic link may be confounded"** — the F5 headline: a claim that was *orphaned* last pass now stands on its own three grounds, in antithesis with an equally-built causal claim. This is what "build it out, don't add negative edges" looks like.
3. **Node view → "Guidelines dropped cholesterol cap"** (F1) — an external anchor now backed by the biological reason it was really standing on.
4. **Node view → "High-risk people should limit eggs"** (F7) — an ought with its value premise now explicit alongside its empirical grounds.

## What carries forward

- Grammar changes still needed: **none** from this pass. F2's `list-studies` is a *read* convenience, not a grammar change.
- Affordance wishlist (post-v0, additive): **shared/reusable nodes** (F8) and **crux / common-ground tagging** (F9). Both serve FLF's compounding + insight dimensions.
- The support-only + Antitheses grammar survived a genuinely harder, more complete argument than the first pass. That's the result worth reporting to FLF: *the minimal grammar's apparent gaps were mostly unbuilt argument.*
