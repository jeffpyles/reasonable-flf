# eggs-p5 — Bayesian Truth Serum on real agents: a diagnosed negative result

**Headline:** BTS did **not** rescue the experts on real data. It is not a free lunch — the synthetic
win depended on assumptions that did not hold with real LLM raters under sortition. The result is
negative but richly diagnosed, and it points at concrete (non-trivial) fixes rather than abandoning
the idea.

## The run

60 agents (52 Haiku crowd + 8 Sonnet experts) each rated 79 node-Agreement claims **and** predicted how
the rest of the crowd would rate each (low/mid/high split), on a clean copy of the eggs graph. All 60
returned: **1,184 ratings + 1,184 paired predictions**. Meta-predictions were kept in a sidecar
(`predictions.jsonl`); the frozen core and live reputation math were never touched.

## Result — no rescue

Expert-panel percentile (0.10 = buried, 0.90 = on top) and Spearman vs hidden competence:

| rule | expert pctile | crowd pctile | Spearman vs competence |
|---|:--:|:--:|:--:|
| alignment | 0.181 | 0.539 | −0.61 |
| discrimination | 0.179 | 0.540 | −0.67 |
| bts (info only) | 0.167 | 0.542 | −0.44 |
| **bts (full)** | **0.150** | 0.544 | −0.68 |

BTS left the experts at the bottom — if anything slightly *below* alignment. The blunt-majority
consensus reproduced the eggs-p4 pathology (all rules negative vs competence), and BTS did not undo it.

## Why — three stacked causes, each measured

**1. The prediction asymmetry did not hold in aggregate — but it DID hold where it matters.**
Aggregate crowd-modeling accuracy (−KL): experts −0.44, crowd −0.36 — experts were *worse*. Cause:
**both tiers predict "others will rate like me"** (corr of predicted-crowd-mean with own rating: experts
0.73, crowd 0.93). Self-anchoring is *accurate for the majority* (the crowd IS the typical rater, so it
tracks the actual crowd at 0.91) and *inaccurate for the minority* (experts' own view is atypical, so it
tracks the crowd at only 0.72). BUT — restricted to the experts' **14 "sharp low" calls** (where they
rated ≥0.4 below the crowd, the fallacy-type items BTS should reward), they correctly predicted the crowd
would rate higher **11 of 14 times** and recovered **81% of the true crowd–self gap**. So the premise —
*the informed minority can predict the majority* — is empirically supported on the items that matter; it
is just swamped in the aggregate by generic predictions on the many easy items.

**2. Sortition starves the "surprisingly popular" signal.** BTS's info reward requires the correct-
minority answer to appear in the votes *more than predicted* — i.e. the informed minority must be
**concentrated** on an item. But sortition spreads the 8 experts ~**2 per 15-rater item** (8 items got
zero experts). Two of fifteen can never make an answer "popular." Concentrating helps the experts' info
score (sparse −0.14 → dense +0.23) but not enough (see cause 3). **Sortition (spread for coverage) and
BTS (needs overlap) are in direct tension** — a real design finding.

**3. The multi-bucket info score structurally favors the concentrated majority.** Even on items with
≥3 experts, expert info (+0.23) stayed below crowd info (+0.37): the actual rating distribution is more
concentrated than people's (hedged) predictions, so the *majority* bucket is itself "surprisingly
popular" and the plurality banks the reward. A per-rater, multi-bucket info average is the wrong shape;
Prelec's surprisingly-popular is a per-**item binary decision** (which answer beats its prediction most),
not a per-rater bucket average.

## What this does and doesn't mean

- **It doesn't refute BTS.** The core premise held on the diagnostic subset (81% gap recovery), and
  density visibly improved the expert signal. The mechanism was starved, not disproven.
- **It does show BTS is not free.** It needs, together: (a) the informed raters **concentrated** on shared
  contested items (not sortition-spread), (b) **first-class prediction elicitation** — here it was a
  secondary bolt-on and experts gave generic distributions on easy items (within-rater prediction stdev
  0.35 vs the crowd's 0.55), and (c) a **surprisingly-popular scoring formulation** (per-item SP decision,
  or a minority-weighted info term) rather than a per-rater multi-bucket average.
- **Honest caveats:** model-as-expertise proxy; single run; the prediction task was low-stakes/secondary
  so expert effort on it was likely throttled; legacy eggs-p4 comments were present as context.

## Where this leaves the reputation thread

Ranked by evidence, from this whole investigation:
1. **Signal-tracking (discrimination) remains the best cheap, validated lever** — it recovered competence
   on the eggs-p4 log (+0.11 where alignment was −0.64) and is robust whenever a competent sub-population
   exists. It needs no new data and no meta-prediction. **This is the one to implement first.**
2. **BTS is promising but not yet demonstrated on real data.** Before more runs it needs the three fixes
   above. The cheapest next test: a small **concentrated** run where all 8 experts + the high-care crowd
   rate the *same* ~15 contested items, prediction made a first-class step, scored with a per-item SP rule.
3. **External anchor items** (claims with a defensible known answer) remain the surest way to break the
   endogeneity, independent of meta-prediction working.
