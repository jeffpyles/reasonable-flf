# reputation-lab

A self-contained workspace for experimenting with **reputation scoring** in the *Reasonable* argument-
mapping project. 

**Start here:** [`FINDINGS-SYNTHESIS.md`](FINDINGS-SYNTHESIS.md) — the current, complete synthesis of the
investigation (what we killed, the validated stack, cold-start & scale, adversarial robustness, the
calibration identifiability guard).

## Layout

```
FINDINGS-SYNTHESIS.md        CURRENT complete synthesis — read first (the map for the whole investigation)
ASSESSMENT-SPEC.md           the frozen assessment contract (reputation model + amendments)
AGENT-GUIDE.md               rater-facing rules (how agents rate)
SITE-VARIANTS-CONCEPT.md     vision note: open/in-house site variants, benchmarks, the reality-refereed (math) frontier
ROADMAP-NEXT-VERSION.md      deferred improvement steps the adversarial runs pointed to (next version, post-deadline)
ORACLE-BUDGET-POLICY.md      where to spend scarce oracle-points at scale: triage by contestedness (scalability)
archive/                     retired scaffolding + resolved handoffs/responses; see archive/README.md
reasonable/                  core package: store, fold, assess (True_R), assessment (calibration + camp-
                             detection + certainty guardrail, LIVE), queries, ...
graph.py                     CLI: rate / reputation / assess / rebuild / stats / get-node / ...
dispersion-regimes/          when rating spread is a contested signal vs noise (belief-camp vs lens); reconciles
                             the fermi dispersion-handoff with coldstart E10 (README + regimes.py)
eggs-p3/ … eggs-p10/          the experiment datasets (event logs + graphs + per-run harness + findings)
review/                      fresh-eyes critique of the above + 4 offline experiments (REVIEW.md)
coldstart-lab/               cold-start & scale: reliability ceilings, newcomer budgets,
                             cluster-adjudication, sparse propagation (FINDINGS.md)
eggs-p8-deliberation/        Fable+Opus panel-anchor forging + validation (FINDINGS.md)
eggs-external-check/          does the model oracle track the documented real-world record? (FINDINGS.md)
eggs-adversarial/            adversarial dose-response: attacker-fraction breakdown + defenses (FINDINGS.md)
covid/                       2nd-domain graph (SARS-CoV-2 origins, curated-debate shape): swarm build +
                             cross-model oracle/anchors + real honest-camp & sleeper rating runs (harness/)
covid-adversarial/          covid dose-response + H4 diagnostic: the eggs stack generalized, with a REAL
                             sleeper bloc; two new findings (agent defection; camp-detection insufficiency) (FINDINGS.md)
sources/eggs/                source material for the "Are eggs good for you?" graph
sources/covid/               source pack for the covid-origins graph (index.json + BRIEFING.md)
```

Each `eggs-pN/` holds `events.jsonl` (append-only log — the source of truth), `graph.json` (derived
snapshot), `harness/` (the run + analysis scripts and personas), and its `*-FINDINGS.md` write-ups.

## Quickstart (run from this directory)

```bash
# reproduce the core scoring-rule comparison on the eggs-p4 log
python3 eggs-p4/harness/rescore.py

# the biased-bootstrap recipe (anchors + superlinear weighting) and the minimum competent count
python3 eggs-p6/harness/analyze_p6.py
python3 eggs-p6/harness/min_competent_fraction.py

# inspect a graph / reputation directly
python3 graph.py stats --data eggs-p6 --json
python3 graph.py reputation --data eggs-p4 --json
```

Python 3, standard library only (no third-party deps). The scripts read the committed event logs; nothing
needs a network or an agent run to reproduce the analyses. New agent-driven runs use the `workflow_*.js`
harnesses (Claude Code Workflow) plus the `gen_*`/`snapshot`/`predict` helpers in each `harness/`.

The full research narrative and per-run numbers live in the `*-FINDINGS.md` files, indexed from the spec's
dataset table.
