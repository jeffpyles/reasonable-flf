# Adversarial dose-response — where the assessment machinery breaks, and which defense fails first

*Defensive security research: we red-team our own aggregation to find its breaking point and harden
it. Done fully OFFLINE (no agent run) so the whole attacker-fraction curve and every attack type can
be swept cheaply and conservatively. Honest base: **42 real good-faith neutral raters** (pooled from
eggs-p8/p9/p10, blind, all 79 nodes). Attackers push the graph's verdict toward "eggs are dangerous"
(the real cholesterol-hawk direction; the naive attacker reuses REAL eggs-p6 hawk rating vectors).
Oracle = eggs-p5 panel. Reproduce: `python3 eggs-adversarial/adversarial_doseresponse.py`.*

## A methodology point first (belongs in the submission): correlation hides coordinated attacks

Our first pass scored consensus-vs-truth by **correlation** and every defense looked bulletproof to
60% attackers — a falsely reassuring result. Correlation is **offset-invariant**: a coordinated attack
that shoves *every* target claim toward one pole preserves the item ordering while destroying the
levels, so it is *invisible* to correlation (and to any ordering-based rule, e.g. discrimination) and
catastrophic under **MAE / verdict-flip**. Attack-resistance must be measured with level-sensitive,
verdict-level metrics. This is an assessment-layer lesson in its own right — the choice of evaluation
metric is itself an attack surface.

## The dose-response (MAE on target claims; breakdown ≈ MAE > ~1 / verdict-flips > 0)

Honest-only baseline: target-node MAE 0.58, 0% verdict-flips.

| attack | flat (no defense) breaks at | calibrated | superlinear γ4 | detection (recall) |
|---|:--:|:--:|:--:|:--:|
| **naive coordinated** | ~40–50% (flips→100% @60%) | **holds to 60%+** (MAE ≤0.26) | holds (≤0.17) | 100% |
| **jittered** (noise to evade) | ~30–40% | **holds to 60%+** (≤0.25) | holds (≤0.16) | 100% |
| **sybil** (identical clones) | ~40% | **holds to 60%+** (≤0.26) | holds (≤0.16) | 100% |
| **sleeper** (honest on anchors, lies off-anchor) | ~30% | **FAILS ~30%** (MAE→1.66) | **FAILS worse** (→1.62) | 100% |

Four findings:

1. **No defense → captured near parity.** Flat aggregation flips the target verdicts to 88–100% wrong
   once attackers reach ~40–50% of the pool. This is the "why you need the machinery at all" baseline.

2. **Calibration robustly defeats the unsophisticated attacks — even a 60% majority.** Naive,
   jittered, and sybil attackers all rate the *anchors* in their attack direction too, so per-rater
   anchor calibration fits them an inverted/garbage transfer function and neutralizes (or reverses)
   their influence. A coordinated bloc that lies *everywhere* is easy: the anchors catch it. Sybils are
   no worse than one attacker — cloning doesn't help, because all clones fail the anchors identically.

3. **The sleeper is the crux vulnerability, and it's a clean, general result.** An attacker who rates
   the anchors *honestly* and lies *only on the non-anchor contested claims* passes the calibration
   gate (good anchor fit → full trust) and pushes its lies straight through. Calibration breaks by
   ~30% sleepers; verdict-flips hit 100% by ~40%. **Calibration's protection is exactly as wide as the
   anchors' coverage of the contested space — a sophisticated attacker simply lies in the gaps between
   anchors.** And **superlinear/gated weighting makes sleepers *worse*** (MAE 1.44–1.62), because it
   concentrates influence on raters who look trustworthy on the anchors — which is precisely what a
   sleeper engineers. *Do not naively concentrate weight; against a sleeper it is an amplifier.*

4. **Detection is the backstop that holds when correction fails.** Spectral camp-detection flags the
   attacker bloc at **100% recall for every attack type, including sleepers** (precision 0.71–0.83 at
   10% attackers, rising to 1.0 by 20%). Even sleepers — who mimic different honest raters on their
   cover claims — still form a detectable cluster via their *coordinated* lies on the target claims.
   So the system can always **flag "there is an organized bloc here" for human/verifier review**, even
   at fractions where it cannot automatically correct the verdict. Detection and correction are
   separate capabilities, and detection is the more robust of the two.

## Design implications
- **Anchor coverage of the contested frontier is the single most important defense parameter.** The
  sleeper attack targets exactly the un-anchored contested claims; the mitigation is denser, rotating,
  hard-to-predict anchors over the contested space (constructed reasoning-anchors and panel anchors
  both help), accepting that full coverage is impossible.
- **Correction alone is insufficient; pair it with detection + escalation.** Camp-detection flagging a
  coordinated bloc → route those claims to human or formal-verifier adjudication is the robust design.
  Detection's 100% recall is the safety net under a sophisticated attack.
- **Superlinear weighting is a liability under sleepers** — prefer moderate calibration-weighted
  aggregation; reserve concentration for verified-anchor-rich regions.
- **Metric choice is a defense.** Score with verdict-level MAE, never correlation, or a level-shift
  attack passes unseen.

## Honest limitations
- **Worst-case sleeper knows the anchor set.** The sleeper here lies on exactly the non-anchor
  contested nodes — the optimal attack. A real attacker must *infer* the anchors; if anchors are secret
  and rotating, the sleeper degrades toward the (defended) naive attack. This is the conservative
  (pessimistic) bound, which is the right posture for a robustness claim.
- **Static, not adaptive.** Attackers don't observe reputation scores and adapt; a truly adaptive
  red-team is a harder, later test. Detection here also assumes the bloc coordinates tightly on target
  claims — a sleeper that also *jitters* its target-claim lies would be harder to cluster (untested).
- **Synthetic attackers (except the real p6 naive template).** They execute specified strategies, so
  they're a floor on attack strength, not a ceiling — but for finding a *defense's* breakdown fraction,
  a strong specified strategy is the right tool. The covid agent-run adds real-LLM-attacker realism.
- **One domain, LLM-persona honest base.** As throughout.

## Maps to the FLF assessment desiderata
Directly answers *"calibrating confidence that accounts for adversarial information environments,"*
demonstrates *"flag correlated evidence treated as independent"* (the sybil result), and the
detection-vs-correction split operationalizes *"distinguish what the debate settled from what it
merely performed settling"* — the machinery can say "this apparent consensus is a coordinated bloc,"
which is exactly a performed-settling detector.
