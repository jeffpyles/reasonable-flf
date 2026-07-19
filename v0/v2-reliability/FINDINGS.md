# v2 flagship graphs — rating reliability, and setting `confirm` from data

*Assessment thread, 2026-07-18. Question from the Review thread: the four `*-graph-v2`
flagships are fully rated but many aggregates sit below `confirm=15` and read amber/provisional —
what's the cheapest way to round them out to "real statistical confidence"? Is flooding more blind
Haiku raters (deficit ≈6.5k ratings, ~2.2M tokens) the move?*

**Answer: no. The graphs are already at confidence; the amber is a threshold artifact. Set `confirm`
from measured reliability (= 8) and rebuild — zero new ratings.**

## Method

For each graph, per node-Agreement (dim A) target we have `{agent: value}`. Two measures
(`splithalf.py`, 300 seeded resamples/point, unweighted means — the graphs are anchor-free, so the
published True_R-weighted aggregate ≈ the plain mean):

- **Relative reliability** — split each target's raters into two disjoint halves, mean each, Pearson-
  correlate the half-means *across targets*, Spearman-Brown up → reliability of a *p*-rater aggregate's
  ordering of nodes.
- **Absolute precision** — SEM = per-target stdev / √n: how tightly each mean is pinned on 0–5.

## Results

| graph | targets | rater n (min/med/max) | reliability @ n=8 | @ median n | SEM @ median n | pooled rater sd |
|---|---|---|---|---|---|---|
| covid-graph-v2 | 133 | 12 / 28 / 28 | 0.87 | **0.96** | 0.12 | 0.58 |
| eggs-graph-v2 | 69 | 8 / 20 / 20 | 0.94 | **0.98** | 0.10 | 0.40 |
| blackholes-graph-v2 | 70 | 8 / 20 / 20 | 0.93 | **0.97** | 0.10 | 0.35 |
| debate-graph-v2 | 45 | 8 / 12 / 12 | 0.92 | **0.96** | 0.11 | 0.33 |

- Every graph clears **0.8 reliability by n=4–6** and **0.9 by n=6–12**; at current median depth they
  are **0.96–0.98**, with means pinned to **±0.10–0.12**.
- The `n=8` floor is already **0.87–0.94** reliable / **SEM ≤0.21**.
- Median depth is already **20–28** (not 8) — the "deficit" was only a minority of low-coverage targets,
  and those are statistically solid too.

## Decision: `confirm = 8` (and a separate finding about the amber)

`confirm=15` is a round "= three blocs" default, not a measured bar. At **n=8** every graph is ≥0.87
reliable and SEM ≤0.21, and it matches the cold-start result that coarse quantities stabilize by ~8
(K≈8; `FINDINGS-SYNTHESIS.md` §3). Applied to the four v2 graphs (persisted in each `config.json`).

**What `confirm=8` actually buys — it unmasks genuine *contested* structure** that `confirm=15` was
hiding as provisional (a node can't read contested until n ≥ confirm):

| graph | confirm=15 (contested / settled / provisional) | confirm=8 |
|---|---|---|
| covid-graph-v2 | 33 / 44 / 56 | **39** / 44 / 50 |
| eggs-graph-v2 | 15 / 0 / 54 | **18** / 0 / 51 |
| blackholes-graph-v2 | 12 / 0 / 58 | 12 / 0 / 58 |
| debate-graph-v2 | 0 / 0 / 45 | **15** / 0 / 30 |

Most striking: `debate-graph-v2` went from *everything amber* to **15 contested** — those nodes were
genuinely contested all along, masked only because n<15.

**But the residual amber is NOT a coverage problem — it's the heat/cold gate.** `settled` requires
converged **and cold** (`is_cold`: node heat below `cold_factor` × site-median heat). Across all four
graphs, **every** provisional node has n ≥ confirm — 100% heat-gated, 0% coverage-gated — and three of
four graphs have **zero** settled nodes. These graphs were **batch-built** in one burst, so their heat
is uniform and nothing reads "cold." The cold signal is a *live-site "attention has moved on"* model; on
a **static, built-for-submission snapshot** it's essentially undefined, which is why converged,
high-reliability nodes still read provisional.

So reducing amber further is a **lifecycle-semantics decision, not a rating-depth one** (more ratings do
nothing here). Options for a static submission artifact: **(a)** accept it — "contested + provisional
(converged, live)" is an honest reading for a truth-finding tool; or **(b)** rebuild with a high
`--cold-factor` so converged nodes settle (the existing knob effectively drops the inapplicable cold
gate for a static artifact — no code change). This is a call for the Graphs/lifecycle owner, flagged
separately; it does not affect the reliability result above.

Flooding more *same-persona* Haiku raters would have been the worst value per token: they are correlated
(effective n ≪ raw n), and on anchor-free graphs the reputation signal is `align`, so more agreeing
raters just pull the weighted mean toward the plain majority mean and inflate cheap-rater reputation.
If more confidence were ever wanted, diverse lenses (not volume) are the lever.

## Reproduce (from `v0/`)
```
python3 v2-reliability/splithalf.py
```
