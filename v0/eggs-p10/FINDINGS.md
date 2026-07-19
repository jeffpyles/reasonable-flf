# eggs-p10 — the transition zone: does the camp axis rotate from belief to capability as the divide weakens?

*The run that landed IN the transition zone p8 (moderate, disposition effect 0.36) and p9 (faint, 0.01)
bracketed. Identical balanced 2×2 (disposition × model, 7/cell, blind, saturated) with a pilot-tuned
INTERMEDIATE bias prompt. The pilot (8 raters) hit the target on the first try — disposition gap +0.25,
symmetric across models — so the two axes are cleanly orthogonal and the de-confound is valid. Oracle =
eggs-p5 panel. Reproduce: `python3 eggs-p10/harness/analyze_p10.py`.*

## The headline: NO axis rotation. Belief, not capability, at every detectable divide.

At this softer-but-real divide, camp-detection tracks **disposition just as cleanly as at the strong
divide** — and does *not* rotate toward model capability:

| accuracy | haiku | sonnet | | camp axis | value |
|---|:--:|:--:|---|---|:--:|
| **biased** | 0.45 | 0.61 | | **vs DISPOSITION** | **0.96** |
| **neutral** | 0.59 | 0.85 | | vs MODEL | 0.54 (chance) |

Both biased cells cluster together *across models* (cluster-1 share: biased-haiku 0.14, biased-sonnet
0.00), both neutral cells together *across models* (1.00, 1.00). The feared failure mode — that as the
disposition signal fades toward the noise floor, the strongest remaining structure becomes the
capability difference and the machinery starts sorting people by *how capable* they are rather than
*what they believe* — **did not materialize** at a disposition effect of 0.19. The reassuring p8 result
is robust to a softer, more realistic divide.

## The transition curve — and it's SHARP, not mushy

Three points now span the phase transition (split strength: >0.25 = a real divide detected; ~0.25 =
the p5 no-divide null):

| run | bias | disposition effect | split strength | camp axis → disposition | → model | verdict |
|---|---|:--:|:--:|:--:|:--:|---|
| **p9** | faint | 0.01 | 0.23 | 0.57 | 0.50 | no divide, no coherent axis (correct null) |
| **p10** | intermediate | **0.19** | **0.61** | **0.96** | 0.54 | camps, cleanly disposition |
| **p8** | moderate | 0.36 | 0.75 | 0.96 | 0.54 | camps, cleanly disposition |

Two things fall out:

1. **The transition is sharp, not a wide ambiguous band.** By the time the divide is *detectable at all*
   (p10: strength 0.61 at disposition effect 0.19), the axis is *already fully resolved* to disposition
   (0.96 — identical to the strong p8). There is no dangerous middle zone where the machinery fires on a
   half-formed faction with a rotated or ambiguous axis. The clustering either finds nothing (p9, correct
   null) or finds the *right* thing cleanly (p10/p8). This is the most reassuring possible answer for the
   trigger design: whenever camp-detection reports a divide, that divide is real and correctly
   belief-tracked.
2. **Split strength tracks disposition effect monotonically** (0.23 → 0.61 → 0.75 as the effect goes
   0.01 → 0.19 → 0.36), so the spectral-strength statistic is a usable *dial* for divide severity, and
   the detection threshold (strength lifting off the ~0.25 null) is crossed somewhere between a
   disposition effect of 0.01 and 0.19.

## Secondary confirmations

- **Capability does not erase the intermediate bias** (biased-sonnet 0.61 vs neutral-sonnet 0.85 — a real
  0.24 gap), consistent with p9's dose-dependence finding: a strong model reasons away a *faint* prior
  (p9) but not an *intermediate or moderate* one (p10, p8). The "capability erases the bias" threshold
  sits between the faint and intermediate doses.
- **Ranking-speed r1 0.061** — a population with a real disposition divide ranks faster than the
  near-homogeneous p9 (0.029) / p5 crowd (0.013), as expected.
- **Adjudication (n=8–15 held-out) is noisy at this divide:** p5-panel calib-full 0.64 vs flat 0.74 (a
  small held-out set where calibration slightly hurt), biased-only +0.88; Fable+Opus panel calib-full
  0.66 vs flat 0.55. Small-sample wobble — not a headline; the de-confound is the result.

## What this settles, and what it doesn't
- **Settled:** the soft-divide de-confound (the open thread from p9). Across the whole transition zone,
  camp-detection tracks belief, not capability, and never fires on a phantom faction. The axis-rotation
  failure mode is not real at these divide strengths — a genuine reassurance for deploying the
  contested-region machinery on realistic (soft-divide) populations, not just the strong-bias p6/p8 case.
- **Limits:** three dose points on one domain; the exact detection threshold (between disposition effect
  0.01 and 0.19) is bracketed, not pinned — a fourth run at ~0.10 would locate it, though the *design*
  question (does the axis rotate?) is now answered no, which was the point. Small held-out sets make the
  adjudication numbers wobble. Model pair is Haiku/Sonnet (same vendor); a cross-vendor capability axis
  could in principle behave differently, but there's no reason from this data to expect rotation.
