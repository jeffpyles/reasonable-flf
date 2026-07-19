# Coherence-lint review of the three FLF graphs (2026-07-17)

*Ran `graph.py lint` over covid / black-holes / eggs and triaged every finding. The honest outcome:
the graphs are structurally sound except **one genuine slip** (fixed here); the rest of the findings
are correctly **other-lane** — rater adjudication, viewer declutter, or advisory — not mechanical
edits to make. This is the "eat our own dog food" pass, and it doubles as a map of which lint
categories are auto-fixable vs judgment.*

## Fixed here

- **eggs `s2` — spurious 1-member antithesis set.** `n002` ("eggs don't raise CVD risk") was duplicated
  into its own set `s2` even though it's already a rival in `s1` (n001/n002/n048). A 1-member antithesis
  is malformed (an antithesis needs ≥2 rivals). Fixing it exposed a **grammar gap**: `supersede` only
  covered nodes/edges, so a malformed *set* couldn't be demoted. Extended `supersede` to antithesis
  sets, then demoted `s2` with a reason. `lint` now skips demoted items, so the finding clears; covid
  and BH rebuilt **byte-identically** (only eggs changed).

## Correctly other-lane (not fixed — and why)

- **Redundant paths (covid 12, BH 4, eggs 4) → rater adjudication (§2.4), not demotion.** These are
  direct edges whose endpoints are *also* joined by a layered path — e.g. covid `n040` ("two spillovers")
  grounds `n001` ("zoonotic") directly *and* via the market-spillover chain. Both are legitimate lines
  of support; the direct edge asserts *direct* justification, the path asserts an *indirect* one — they
  are not the same claim. Per §2.4 these go to raters for side-by-side comparison; unilaterally demoting
  them would delete legitimate direct-support assertions. `lint` surfacing them **is** the intended
  action. (If a rater panel later judges a specific shortcut subsumed, `supersede` is the tool.)
- **Hub nodes (covid n001=19, n002/n041=11; BH n001=12; eggs n002=11) → viewer declutter (§3.4) +
  build-time discipline (§4), not mechanical.** Reducing a hub means creating intermediate nodes and
  re-routing grounds to their *proximate* support — an argument-authoring judgment (a build-agent task
  under the new proximate-attachment rule), not a demotion. In the living viewer, §3.4's length-
  normalized strength already **hides** a shortcut where a stronger layered path exists, so the hub
  reads as layered without editing the data.
- **Negation-framed node (eggs `n042`, "No long-term RCTs … exist") → advisory false-positive, kept.**
  A legitimate epistemic-limit claim that happens to be phrased as an absence. The lint flag is a
  prompt to check, not a defect; nothing to change. (Text is immutable anyway — a `propose-phrasing`
  could offer a positive rewording, but "no long-term RCTs exist" has no faithful positive form.)

## Post-review lint state

| graph | hubs | malformed sets | redundant paths | negation | orphans/questions |
|---|---|---|---|---|---|
| covid | 3 | **0** | 12 (rater) | 0 | 0 |
| black holes | 1 | **0** | 4 (rater) | 0 | 0 |
| eggs | 1 | **0** (was 1) | 4 (rater) | 1 (advisory) | 0 |

The remaining nonzero categories are all deliberately deferred to the rater/viewer/build lanes above.
