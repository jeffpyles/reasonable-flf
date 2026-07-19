# External grounding — does the model "oracle" track documented reality, or only itself?

*Thread 4, the deepest caveat in the program: every "truth" here is model-generated (the eggs-p5
oracle is 8 Sonnet personas), so all our competence/adjudication results could in principle be "the
system recovers model-consensus," not "…recovers truth." This probes that by scoring the Sonnet
oracle (and the Fable+Opus panel) against an EXTERNAL reference grounded in the documented real-world
record ~2024 — the source-pack studies (Hu 1999, Rong 2013), the U.S. Dietary Guidelines
cholesterol-cap change (300 mg cap → removed 2015-2020), and established lipidology/physiology
(LDL/ApoB causality, hepatic downregulation, saturable absorption, hyper-responders, FH, choline,
Salmonella). Reproduce: `python3 eggs-external-check/external_grounding.py`.*

## Result — the model oracle does track the documented record (in this domain)

| comparison | corr | mean abs error | n |
|---|:--:|:--:|:--:|
| Sonnet oracle vs documented external | **+0.95** | **0.11** | 54 |
| Fable+Opus panel vs documented external | +0.91 | 0.28 | 11 |

On the 54 nodes where the documented record clearly speaks, the Sonnet "expert" oracle lands within
~0.1 (of 5) of the documented value on average. **This substantially de-risks the "it's all just
models agreeing with models" worry for the eggs domain**: the model consensus is not free-floating —
it aligns closely with the actual documented state of nutrition science and guidelines. Since every
downstream result (competence measurement, camp adjudication, calibration) is scored against that
oracle, its validation as truth-tracking *retroactively strengthens the whole chain* here.

## Where model-consensus diverges from the record (the valuable part)

Only two nodes diverge by ≥0.6, both mild and interpretable:

| node | oracle | external | Δ | what it is |
|---|:--:|:--:|:--:|---|
| n029 "dietary-cholesterol evidence remains mixed/unsettled" | 3.99 | 3.00 | +0.99 | oracle **over-rates 'unsettled'**: the record has tilted to "small, variable effect for most," not 50/50 |
| n064 "gut microbiome → TMAO, TMAO assoc. CVD risk" | 4.16 | 3.50 | +0.66 | oracle slightly **over-credits a genuinely debated** mechanism (mixed replication, causality unclear) |

The pattern in both: the models retain a touch more "it's still controversial / this mechanism is
real" framing than the documented consensus now supports. That is a plausibly *general* LLM tendency
(hedging toward older/ongoing controversy, over-crediting mechanistic stories) worth watching — and
exactly the kind of subtle miscalibration only an external check can surface, because the model
raters and the model oracle share it and so it is invisible from inside the loop.

## Honest limitations — the grounding is stepped toward reality, not fully independent
- **The external reference is LLM-applied (by me, Fable).** It is anchored to specific citable
  real-world facts rather than to the eggs-p5 panel's free judgment — and where I judged the record to
  have moved (n029) it diverges from the oracle, so it is not merely echoing it — but a skeptic can
  fairly note this is still one model's rendering of the documented record agreeing with another
  model's. The residual circularity is real; the genuine fixes (human expert ratings; direct
  quote-extraction from the primary sources) remain future work.
- **Scored only where the record speaks (54/79).** Value/ought claims and genuinely frontier-contested
  empirical claims were abstained (transparently listed in the script). So this validates the models
  on *claims with documented answers* — which is the right scope, but means the high correlation is
  partly "the models get the clear ones right," not a claim about the contested frontier.
- **One domain, and an unusually well-documented one.** Eggs has authoritative real-world positions
  (a guideline reversal, major meta-analyses) to check against. A politically/morally contested domain
  would be a harder, different test — and is where the model-grounding worry would bite hardest.
- Correlation is helped by the wide value range (1.4–4.8); the **mean abs error 0.11** is the more
  informative number and is genuinely small.

## What it changes
- The eggs-domain results rest on an oracle now shown to track documented reality (r 0.95), not a
  free-floating model artifact — a materially stronger footing for the FLF write-up than "our Sonnet
  panel said so."
- It surfaces a candidate *systematic* LLM miscalibration (residual "still unsettled" / mechanism-
  over-crediting bias) that an all-model pipeline cannot see itself — a concrete argument for keeping
  a thin external-grounding check in any production reputation loop, even a small one.
- It does **not** dissolve the deeper concern for hard domains: where no documented external record
  exists (novel or value-laden questions), the model-grounding problem is unbroken, and the honest
  output there stays "the camps," not "the anchor."

## Addendum — why did the 8-Sonnet oracle beat the 2-model panel vs external? (same-node check)

Scored on the *identical* 11 anchor-grade nodes (removing the set-size confound): oracle corr +0.94 /
mean err 0.15; panel +0.91 / 0.28. So the oracle's edge is real, not a node-set artifact — but the
per-node pattern says what kind of edge it is:
- **One shared miss dominates.** n029 ("dietary-cholesterol evidence is unsettled") is over-rated ~1.0
  by BOTH the oracle (3.99) and the panel (4.00) — a bias common to Sonnet, Fable, AND Opus. Drop it
  and both are near-perfect (oracle +0.995, panel +0.97). No number of same-generation voices fixes a
  bias they all share — the point of an external check.
- **The oracle's remaining edge is variance reduction.** On the other 10 nodes the panel is
  consistently ~0.2–0.3 off where the oracle is ~0.01–0.15 — exactly the wisdom-of-crowds pattern:
  averaging 8 competent voices gives a tighter central estimate than averaging 2 (SE ~1/√n → ~2×
  tighter for 8 vs 2, matching 0.15 vs 0.28). It reduces *idiosyncratic* noise, not shared bias.
- **Caveat both ways:** n=11 (10 without n029) is tiny — hold the magnitude loosely. And the external
  ref was authored by Fable, which should if anything favor the Fable-containing panel; the oracle wins
  anyway. Design read: anchor-forging wants BOTH many voices (variance ↓) AND cross-model/vendor
  diversity (shared-bias ↓) — our 2-model prototype had the diversity but too few voices; n029 shows
  even the diversity we had doesn't escape a whole-generation bias.

## Addendum 2 — the panel-size error curve (bootstrap over the 8 experts)

All C(8,k) subsets of the 8 Sonnet experts, each subset's mean scored vs the external reference
(`panel_size_curve.py`, chart `panel_size_curve.svg`). Mean abs error by panel size:

| k | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|--|--|--|--|--|--|--|--|
| MAE | .196 | .158 | .142 | .133 | .126 | .121 | .118 | .114 |
| % of max reduction | 0 | 47 | 66 | **78** | 86 | 92 | 96 | 100 |

Fits `MAE(k) = √(0.10² + 0.17²/k)` almost exactly → **irreducible floor 0.10, per-voice noise 0.17**.
Reading:
- The 1/√k variance-reduction law holds cleanly — persona-prompting successfully *decorrelated the
  noise* — but it decays into a **0.10 shared-bias floor** that no number of same-model voices touches
  (the full 8-voice oracle, 0.114, is already essentially at it).
- **Knee at k≈3–4:** k=4 captures 78% of the achievable reduction; each voice past ~5 buys <0.01 MAE
  while polishing against the floor. This nudges the earlier "4–6 sweet spot" toward its low end for a
  *same-model* panel.
- **The floor is exactly where diversity, not count, pays:** a different model has a different
  bias floor, so cross-model voices lower the wall the count-curve asymptotes to. Practical default
  reaffirmed: **~4 voices, spent on different models** — most of the variance reduction, and the seats
  go to lowering the floor rather than polishing against it. Caveat: the floor here is the Sonnet
  shared bias; n029 shows part of it is whole-generation and survives any panel — hence the thin
  external check stays.
