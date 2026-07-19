# eggs-p5 expert-saturation + density sweep — density helps BTS, but isn't sufficient

**Setup:** sent all 8 experts back to rate + predict every remaining node item, raising expert density
from ~13% (~2/item under sortition) to ~38% (~7-8/item). 1,653 ratings + 1,653 predictions total.

## Saturation result (expert percentile, 0.10 = buried, 0.90 = on top)

| rule | before (~13% experts) | after (~38% experts) |
|---|:--:|:--:|
| alignment | 0.181 | 0.217 |
| discrimination | 0.179 | 0.235 |
| bts (info) | 0.167 | 0.229 |
| **bts (full)** | **0.150** | **0.402** |

Density helps every rule, but **helps BTS most** — bts_full expert percentile more than doubled (0.15 →
0.40). The density hypothesis from the first run is confirmed directionally: the correct-minority answer
becomes more "surprisingly popular" when more experts hold it.

## Density sweep — expert recovery vs expert fraction per item

k experts kept per item (+ all crowd), scored:

| experts/item | expert frac | align pct | disc pct | **bts pct** | bts spearman | exp−crowd info |
|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| 1 | 0.07 | 0.07 | 0.04 | 0.12 | −0.62 | −0.08 |
| 2 | 0.13 | 0.08 | 0.07 | 0.26 | −0.57 | −0.10 |
| 3 | 0.19 | 0.13 | 0.08 | 0.33 | −0.56 | −0.13 |
| 4 | 0.24 | 0.16 | 0.12 | 0.32 | −0.55 | −0.07 |
| 5 | 0.28 | 0.15 | 0.14 | 0.30 | −0.55 | −0.07 |
| 6 | 0.32 | 0.17 | 0.18 | 0.29 | −0.56 | −0.12 |
| 7 | 0.35 | 0.19 | 0.20 | 0.38 | −0.48 | −0.05 |
| 8 | 0.38 | 0.22 | 0.24 | 0.40 | −0.46 | −0.05 |

## What it says

- **Smooth, monotonic, no sharp threshold.** Expert recovery climbs steadily with density — there is no
  cliff at "25%" or any single number. Returns keep accruing right up to the 38% ceiling we could reach
  with 8 experts. Practical implication for the assignment rule: **there is no "enough" plateau below
  ~40% — pack as much reputation-weighted quality into a contested item's rater set as you can afford.**
- **BTS benefits most from density** (0.12 → 0.40 across the sweep, vs alignment 0.07 → 0.22). Density is
  disproportionately the BTS lever, consistent with its "surprisingly popular" logic needing minority mass.
- **But density alone is NOT sufficient.** Even at 38% experts, bts_full only reaches the 40th percentile,
  the per-item expert info advantage stays slightly *negative* (−0.05), and overall competence-recovery
  (bts spearman) stays negative (−0.46). BTS mitigates the burial but does not flip to favoring experts at
  any achievable density here.

## Reverse sweep — there is an OPTIMAL mix, not "more experts is better"

Keeping all experts and progressively removing crowd (expert fraction → 1.0):

| crowd/item | expert frac | bts expert pct | bts spearman | exp−crowd info |
|:--:|:--:|:--:|:--:|:--:|
| 15 | 0.38 | 0.40 | −0.46 | −0.05 |
| 6 | 0.57 | 0.56 | −0.28 | **+0.04** |
| 4 | 0.66 | 0.65 | −0.03 | +0.06 |
| 3 | 0.73 | **0.67** (peak) | +0.16 | +0.09 |
| 2 | 0.80 | 0.63 | +0.22 | +0.07 |
| 1 | 0.89 | 0.61 | +0.37 | +0.11 |
| 0 | 1.00 | **0.44** (collapse) | 0.00 | undefined |

**Not monotonic.** Experts start *winning* the surprisingly-popular reward around **~57%** expert
fraction, BTS expert-percentile **peaks near ~66–73%**, then declines and **collapses at 100%**. The
collapse is diagnostic: BTS needs a **mix** — a majority whose collective prediction can be *surprised*
by an informed minority. Remove the crowd entirely and there is no one left to surprise and no
competence spread to detect. **The assignment-rule target is therefore an optimum (a slight-to-two-thirds
majority of reputation-weighted quality raters per contested item), not "maximize expert fraction."**
(Forward + reverse sweep both reproducible via `harness/bts_density_sweep.py`.)

## Why density isn't enough (ties back to the run diagnosis)

Two of the three original causes are unfixed by density: (1) the **multi-bucket info score still rewards
the concentrated majority bucket** — at 38% experts the crowd is still the 62% plurality; (2) the
**aggregate prediction asymmetry still fails** (experts −0.47 vs crowd −0.33) because both tiers self-
anchor and generic-predict on easy items. Density raises the minority's mass but doesn't change the
scoring shape or the elicitation quality.

## Recommendations

1. **For sortition/assignment:** density is a real, monotonic lever — weight contested-item blocs toward
   high-reputation raters aggressively; there's no threshold to stop at below ~40%. (And drop replicate
   blocs, which fight density — see the reputation-design notes.)
2. **BTS still needs its scoring/elicitation fixes**, not just density: a **per-item surprisingly-popular
   decision** (or minority-weighted info term) instead of a per-rater multi-bucket average, and **first-
   class prediction elicitation** with explicit "predict a specific naive persona" framing. A future run
   should combine high density *with* those fixes before BTS is judged.
3. **Discrimination remains the cheapest validated win** and should still be implemented first.
