# eggs-p2 — Stage-3 checkpoint: reputation sorting vs. hidden ground truth

After the cooperative populate (15 raters × varied hidden tiers + 3 authors + 2 frontier authors;
692 events, 50 nodes). The mechanism never saw the tiers; here we ask whether True_R recovered them.

## True_R by hidden tier (raters only)
| tier (hidden) | members | mean True_R | mean raw_r (alignment) | mean n_assess |
|---|---|---|---|---|
| Sonnet expert | rex-1/2/3 | **0.848** | 0.967 | 48 |
| Haiku hi-care | rg-01/03/09/13 | 0.786 | 0.942 | 33 |
| Haiku mid-care | rg-02/05/06/10 | 0.811 | 0.954 | 38 |
| Haiku lo-care | rg-04/07/11/14 | 0.804 | 0.953 | 35 |

Authors (reputation from authoring, rated nothing this round): agent-lane-a 0.773, agent-03 0.745,
agent-b 0.675. Frontier authors frontier-1/2: **0.150** (newcomer floor — their nodes are not yet
rated, so n_assess=0, confidence=0, True_R=prior. Correct: unrated authorship earns nothing yet).

## Findings (honest, and they matter for the experiment)

1. **Experts rose to the top (✓), but the within-Haiku care gradient did NOT appear.** hi/mid/lo
   are effectively tied (0.79–0.81, ordering even mildly inverted). This is not a mechanism failure
   — it is the **cooperative-run ceiling again** (cf. Entry 23/24's quality channel): the care
   personas changed *thoroughness*, not *correctness*. Even hasty raters converged near consensus
   (rg-14/lo still put n002 low, n022 high), so their rating-**alignment** — which is what
   reputation measures — is uniformly high (raw_r 0.94–0.97 across ALL raters). **Alignment can
   only differentiate raters who actually disagree with consensus; honest-but-hasty ≠ misaligned.**

2. **Among honest converging raters, True_R tracks VOLUME (confidence), not care.** raw_r is
   near-flat ~0.95, so True_R differences are driven by n/(n+K): raters who cast more ratings sit
   higher. Experts also topped because they rated the most AND had the highest raw alignment
   (0.956–0.977 vs Haiku 0.925–0.965) — a faint but real quality edge.

3. **The contrarian tension showed up concretely (and instructively).** rg-09 (tagged hi-care) has
   the LOWEST raw_r among raters (0.9255) — because it rated n005 at ~2.5 against a 4.26 consensus
   (a defensible skepticism about the strength of the dietary-cholesterol→LDL link) and **took a
   reputation hit for the divergence.** The divergence nudge fired on exactly that rating. This is
   the Entry-27 design working as specified: reputation measures tracking-the-current-consensus,
   and a lone divergence costs you — vindication, if it ever comes, must arrive through a new era's
   fresh evidence, not retroactively. A real, observable instance of the design's central tradeoff.

## What this cooperative run establishes
A reputation distribution that differentiates a real population, honest ratings that converge
without saturating, and a set of well-assessed (settled) claims — the healthy baseline the
assessment layer is meant to produce. n023 ("MR and LDL-lowering trials support LDL causality")
settled at A=4.425 (n=14) and n017 at A=3.895 (n=10); no single edge reached confirm=10, since
raters spread edge ratings thin — itself a finding (rating effort concentrates on nodes over edges).

> Note: this checkpoint was originally the setup stage for a red-team experiment; that adversarial
> work is sequestered to the `adversarial-defense-archive` branch. The reputation and coverage
> findings above are cooperative site function and stay.
