# Black-holes oracle — results

*2026-07-17. Built a cross-model ground-truth oracle for blackholes-graph (4 panelists —
sonnet ×2 seeds, opus, fable — each independently scored all 69 nodes on the merits) and used it as a
**reference only**: scored the panel's accuracy and ran the certainty guardrail. It is NOT wired into
the graph config — calibration activation stays parked (see `archive/calibration-handoff/`). Reproduce:
`python3 blackholes-graph/oracle/score_panel.py`; rebuild the oracle with `aggregate_oracle.py`.*

## The oracle

- **Verdict, decisive:** n001 "LHC can't destroy Earth" = **4.70**, n002 "real risk of destruction" =
  **0.33**. A confident-answer case, as expected — the four models agree tightly (verdict sd ≤ 0.05).
- **40/40 evidence facts are firm calibration anchors** (cross-model sd ≤ 0.75). Their truths cluster
  in **[4.15, 4.88]** — high and narrow, because a well-established safety case has few genuinely
  mid-scale facts.
- **Catastrophe cruxes land low, correctly:** n068 (captured BH could accrete) = 1.35, n019 (Hawking
  radiation unconfirmed → evaporation defense may fail) = 1.90. The steelmanned catastrophe side is
  represented but judged weak. The other antithesis members (n020/n039/n041/n053/n054) sit ~4.2 — the
  safety-side interpretive claims are well-supported. So on this question the "contested" pairs are
  genuinely lopsided, not balanced.

## Panel accuracy (the payoff)

The 20-rater panel (4 Sonnet + 16 Haiku, from the depth pass) tracks the cross-model oracle **very
closely**:

| metric | value |
|---|---|
| MAE (panel vs oracle, 69 nodes) | **0.197** |
| correlation r | **0.912** |
| verdict n001 safe | panel 4.69 / oracle 4.70 |
| verdict n002 catastrophe | panel 0.46 / oracle 0.33 |

This is the confident-answer regime: when the question is genuinely settled, the assembled panel and an
independent 4-model oracle land in the same place. (Contrast the covid graph, where held-out MAE is 0.82
— a genuinely contested question is harder to pin, for panel and oracle alike.)

## Certainty guardrail — quiet, and that's correct

`graph.py assess --anchors ... --verdict n001,n002` → **guardrail QUIET** (verdict-score 0.0, frontier
0.021); belief-camp between-group dispersion 2% (no camps). The guardrail fires on *false* certainty —
a confident verdict sitting on a contested frontier. Here the confidence is *earned*: the frontier
isn't contested, so the guardrail stays silent. (On covid it FIRES, because covid's verdict is
genuinely unresolved.) The two cases together show the guardrail discriminates settled from unsettled
confidence rather than just penalizing all confidence.

## Note on calibration (parked)

The anchor truths cluster in [4.15, 4.88] — even tighter/higher than covid's [4.08, 4.70]. So wiring
this oracle in and calibrating would regress the graph, exactly as documented in `archive/calibration-handoff/`.
**RESOLVED (2026-07-17):** the Assessment thread shipped an identifiability guard — calibration now
declines when the anchor-truth spread is below 2.0 (BH's is 0.725), falling back to raw byte-identically
(`used_calibration: False`). So BH is anchor-free *by construction*; the oracle serves as a
scoring/guardrail reference, not an aggregation input, and wiring it would be safe-but-moot (discrimination
also declines on low spread). See `archive/calibration-handoff/README.md` RESOLVED + `archive/RESPONSE-calibration-handoff.md`.
