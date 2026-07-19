# Bayesian Truth Serum — scorer + synthetic validation

**Question:** the eggs-p4 re-score showed only *signal-tracking* (discrimination) recovers competence,
and even that weakly (+0.11) and endogenously — it can't crown a correct minority whose ordering the
crowd rejects. Meta-prediction (Bayesian Truth Serum, Prelec 2004) is the principled fix. Before
spending a fresh agent run to collect meta-predictions, we validated the scorer on synthetic data
where ground truth is known. Code: `harness/bts.py` (scorer), `harness/validate_bts.py` (validation).

## What BTS needs and how it scores

Each rater supplies two things per item: their **rating**, and a **meta-prediction** of how the rest
of the crowd will rate it (a distribution over low/mid/high buckets). Per item:
- `info` score = `log(actual_fraction / geometric-mean_predicted_fraction)` for the bucket you chose —
  reward for endorsing the **surprisingly popular** bucket (more common in the votes than the crowd
  collectively predicted). A correct minority can predict the majority but not vice-versa, so the
  correct answer is surprisingly popular even when it is not the plurality.
- `prediction` score = `−KL(actual ‖ your prediction)` — reward for accurately modelling the crowd.
- `bts = info + prediction`. Truth-telling is the equilibrium (you can't inflate info by lying about
  your rating without paying in prediction).

## Synthetic world

Known ground truth: each item has a TRUE quality `q` and an APPARENT quality `a`. On tricky items they
diverge (persuasive fallacy: `q` low, `a` high; ordering-inversion: `q` high, `a` low). Raters have a
hidden skill `s` (skill = seeing through appearance to truth); the blunt crowd also **compresses toward
the middle** (`gain<1`), which is what biases the consensus on every extreme item — the real eggs-p4
regime. Meta-predictions encode the one asymmetry BTS relies on: experts predict the crowd's (biased)
distribution well; crowd members predict via false consensus (others look like me).

## Results

Correlation of each rule's score with the hidden skill `s` (Spearman; +1 = perfectly recovers
competence), and the expert panel's mean percentile (0.9 = experts on top, 0.1 = buried).

**Base world (40 normal, 12 fallacy, 12 inversion):**

| rule | Spearman vs skill | expert pctile |
|---|:--:|:--:|
| alignment | +0.74 | 0.56 |
| discrimination | +0.92 | 0.89 |
| bts (info only) | +0.90 | 0.93 |
| **bts (full)** | **+0.95** | **0.92** |

BTS dominates. Per-item on the ordering-inversion items, alignment rates experts *worse* (distance
0.174 vs crowd 0.127) while BTS-info rates them far *better* (+0.267 vs +0.015).

**Sweep — as ordering-inversion items grow (crowd ordering increasingly wrong):**

| inversion items | alignment (sp / pctile) | discrimination | bts_full |
|---:|:--:|:--:|:--:|
| 0 | +0.85 / 0.74 | +0.93 / 0.89 | +0.93 / 0.92 |
| 30 | +0.72 / 0.47 | +0.92 / 0.85 | +0.96 / 0.88 |
| 100 | +0.54 / 0.29 | +0.92 / 0.79 | +0.96 / 0.85 |

**Alignment degrades steadily** (experts sink to the 29th percentile). **Discrimination stays robust** —
which corrected an overclaim of mine: as long as *some* competent raters exist (careful crowd + experts),
the leave-one-out mean is a decent truth-tracker, so tracking it still rewards competence. BTS holds.

**Decisive test — uniformly-fooled crowd (no careful raters), inversion-heavy:** the whole crowd shares
the bias, so the aggregate ordering itself is wrong and only the 8 experts track truth.

| rule | Spearman vs skill | expert pctile | verdict |
|---|:--:|:--:|:--|
| alignment | +0.08 | 0.19 | experts buried |
| discrimination | **−0.33** | **0.06** | experts buried (score inverts) |
| **bts (full)** | **+0.58** | **0.92** | **experts on top** |

This is the case BTS uniquely solves. When even the aggregate ordering is wrong, discrimination (which
scores agreement with that ordering) *inverts* and buries the experts at the 6th percentile — but BTS,
which never trusts the aggregate and instead exploits the prediction asymmetry, keeps the experts on top.

## What this establishes, honestly

- **BTS works and strictly dominates** in every regime tested — it is never worse than discrimination and
  is decisively better in the hardest one.
- **Discrimination is more robust than I first claimed.** For a crowd with a competent sub-population it
  is nearly as good as BTS and far cheaper (no extra field). BTS earns its keep specifically when the
  crowd is *uniformly* wrong, and as a **strategy-proof** rule (truth-telling equilibrium) — discrimination
  can be gamed by copying the consensus.
- **The one thing the synthetic cannot tell us:** whether *real* LLM raters actually exhibit the
  prediction asymmetry BTS depends on — do Sonnet experts genuinely predict the Haiku crowd better than
  the Haiku predict themselves? That is exactly what the eggs-p5 run is for.

## Next: eggs-p5

Collect real meta-predictions. Each rater, on each assigned item, also predicts the crowd's low/mid/high
split. Score with BTS; compare the expert percentile to eggs-p4's alignment (0.10). Kept as a **sidecar**
(`predictions.jsonl`) so the frozen core and the live reputation math are untouched until validated.
