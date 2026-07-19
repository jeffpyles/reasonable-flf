# Covid graph — good-faith build round (shared brief)

A persona-diverse Sonnet swarm builds the SARS-CoV-2-origins argument graph, run **sequentially**
(each author sees all prior work), mirroring `main`'s `swarm-blackholes` harness but with a
**review-closing final author** (`synth-05`) to remove the late-edge "0-agrees = unreviewed"
confound.

## Authors (in order)
1. `epi-01` — molecular epidemiologist: lays the skeleton (two top answers + zoonosis evidential facts).
2. `origins-skeptic-02` — lab-origin investigator: steelmans the research-incident case (positive claims).
3. `virologist-03` — virologist: the molecular cruxes (furin cleavage site natural-vs-engineered, RaTG13 distance, genomic-signature).
4. `method-04` — methodologist/Bayesian: makes inference-to-best-explanation explicit; institutional-disagreement nodes; ascertainment-bias audit; agrees selectively across sides.
5. `synth-05` — synthesizer/review-closer: reviews everything and agrees honestly, coherence pass, fills only genuine gaps.

## Standing rules (from AGENT-GUIDE.md — every author obeys)
- `search` before every `create-node`; reuse/agree/`propose-phrasing` rather than duplicate.
- **Agree only what you'd have drawn independently.** Declining is the norm. No rubber-stamping.
- **Support-only**: opposition is a rival *positive* claim in an antithesis set, never a "not-X" node.
- `flag-friction` whenever the grammar can't cleanly express something — a primary deliverable.
- Cite `external_anchor` nodes to `sources/covid/index.json` (`list-studies` to reuse a study id).
- Do not fabricate specific statistics/sequences beyond the pack; write at the generality it supports.

## The design instruction unique to this graph (from BRIEFING.md)
Keep the **two layers distinct**: anchor the **evidential facts** (both camps accept them; a panel
can score them) and leave the **interpretive cruxes** as **un-anchored reasoning nodes** (rival
positive claims in antithesis sets). This mirrors the real epistemic situation and is what makes
the un-anchored contested frontier available for the later adversarial (sleeper) test.

## Target
~25–30 nodes; both top-level answers reachable with fair, fully-grounded chains; the contested
cruxes honestly left contested. Restraint over volume.

## Note on mode
The graph is built with `rating_mode_only: false` (authors must read node content fully to build).
It is flipped to enforced Rating mode (`true`) before any rating run.
