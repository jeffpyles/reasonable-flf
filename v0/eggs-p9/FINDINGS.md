# eggs-p9 — the soft-bias 2×2: the faint bias dissolved, and capability's protection is dose-dependent

*Intended as the soft-divide version of eggs-p8's bias×model de-confound: the identical balanced 2×2
(disposition × model, 7/cell, blind, saturated) but with a FAINT bias prompt (p7 `lean_slight`
strength) instead of p8's moderate one, to test whether "camp-detection tracks disposition, not model"
survives E9's hard transition zone. Oracle = eggs-p5 panel. Reproduce:
`python3 eggs-p9/harness/analyze_p9.py`.*

## Headline: the faint bias barely registered — this is ~no divide, not a soft one

| accuracy | haiku | sonnet | row |
|---|:--:|:--:|:--:|
| **mild_biased** | 0.64 | 0.87 | 0.76 |
| **neutral** | 0.69 | 0.86 | 0.77 |
| col | 0.66 | 0.87 | |

- **Disposition main effect collapsed to +0.01** (p8's was +0.36). The `lean_slight`-strength prompt
  did not produce a real disposition; mild_biased raters are as accurate as neutral ones.
- **Model main effect rose to +0.20 and now dominates** — not because model suddenly matters more, but
  because removing the disposition variable leaves capability as the only source of accuracy variance.

## The genuinely useful finding — capability's protection against bias is DOSE-DEPENDENT

Line up the two runs' Sonnet cells:

| bias strength | biased-sonnet | neutral-sonnet | biased-sonnet vs biased-haiku |
|---|:--:|:--:|:--:|
| **p9 faint** | 0.87 | 0.86 | 0.87 vs 0.64 — capability **erased** the bias |
| **p8 moderate** | 0.43 | 0.86 | 0.43 vs 0.39 — capability **could not** rescue it |

So the p8 conclusion needs a dose qualifier: **a strong model reasons its way out of a *faint* prior
but not a *moderate* one.** On Sonnet the mild bias vanished entirely (0.87 ≈ neutral 0.86); on Haiku
the same mild prompt still cost 0.05 (0.64 vs 0.69) — the weaker model can't fully shrug it off. This
is a real, non-obvious refinement: "does capability blunt bias?" is not yes/no but a threshold —
capability neutralizes weak priors and is helpless against entrenched ones, which is exactly the
regime where the reputation machinery has to earn its keep.

## Camp detection correctly read NULL — a clean negative control on real agents

Split strength **0.23** — at (even slightly below) the p5 no-divide control (0.27), and far under p8's
0.75. Axis-vs-disposition 0.57, axis-vs-model 0.50 — both at chance; all four cells split ~50/50. The
clustering **did not hallucinate a faction** where none exists. This is the good-behavior half of the
E5/E9 trigger story, now confirmed on a real mixed-model agent population, not just the p5 crowd: no
real divide → no detected divide → no machinery fired.

Consistent with that, the flat consensus is already excellent (p5-anchor held-out flat **+0.95**),
calibration leaves it essentially unchanged (+0.94) — the healthy-crowd harm check passes again — and
ranking-speed r1 is **0.029** overall (near the homogeneous p5 crowd's 0.013), with within-model r1 ≈
0 (no stable competence gradient to finely rank inside a single model at this bias level).

## What this does and doesn't settle

- **Settled:** capability's bias-protection is dose-dependent (the refinement above); camp-detection
  doesn't false-fire on a near-homogeneous real population.
- **NOT settled — the intended question.** Because the faint prompt produced ~no divide rather than a
  *soft* one, the de-confound at a genuine soft divide (does the axis stay on disposition, or rotate to
  model, in E9's transition zone?) is still open. The two bias strengths now sampled **bracket** that
  zone without landing in it: p8 (moderate, disposition effect 0.36, strength 0.75) and p9 (faint,
  0.01, 0.23). The transition zone is roughly a disposition effect of ~0.15–0.25, which would need an
  *intermediate* prompt — a p10 between these two strengths.
- **Methodological lesson:** bias-prompt strength does not map linearly to divide strength, and
  capability interacts with it (the same prompt is a real bias on Haiku, ~none on Sonnet). Hitting a
  target divide strength is itself a calibration problem; the honest move for p10 is to tune the prompt
  against a quick pilot (a few raters, check the disposition gap) before spending a full run.

## Honest limitations
- One prompt strength, and it undershot the target — this is a null-divide result, informative but not
  the planned soft-divide test.
- Small held-out sets and one domain, as throughout.
- The dose-dependence claim rests on a p8↔p9 cross-run comparison (same design, different runs); clean,
  but two points on the dose axis, not a curve.
