# Covid adversarial run — the eggs machinery on a second domain, with a REAL sleeper bloc

*Defensive security research: we red-team our own aggregation on a second, deliberately different
case (SARS-CoV-2 origins — a curated-debate shape, genuinely unresolved and genuinely camp-split at
the top, unlike eggs). Two things eggs could only do synthetically are now done with **real LLM
agents**: the honest base forms genuine camps, and the **sleeper attacker bloc is a real blind rating
run**. Everything else (the naive/jittered/sybil tail, the fraction sweep) is offline, as on eggs.
Reproduce: `python3 covid-adversarial/covid_doseresponse.py` and `python3 covid-adversarial/h4_diagnostic.py`.*

## Setup (all real, all committed)
- **Graph:** 27-node covid-origins argument graph, built by a 5-author persona-diverse swarm
  (`covid/`), two-layer by design: 12 anchored **source-facts** both camps accept + 12 un-anchored
  **interpretive cruxes** in antithesis sets + the two top answers. Both positions steelmanned.
- **Oracle:** a **cross-model panel** (Sonnet ×2, Opus, Fable) scored all 27 nodes independently.
  Agreement was **tight** (sd mostly <0.3), and all 12 source-facts landed at 4.0–4.7 → **12 firm
  calibration anchors**. This *validates the panel approach on a second domain*. Reference verdict:
  **zoonosis 3.33 / lab-leak 2.12 (gap −1.20)** — leans zoonosis as the real debate's judges ruled,
  but keeps lab-leak a live possibility; cruxes straddle the midpoint, leaning against the lab-leak
  readings.
- **Honest base:** 14 real blind raters — **5 zoonosis-leaning, 5 lab-leaning, 4 neutral**. They
  agree HIGH on the facts (clean calibration for everyone) and split genuinely on the verdict and
  cruxes → **real honest camps**. Honest-only target-node MAE vs oracle = **0.29** (the crowd tracks
  the oracle), verdict gap −0.27 (near-balanced by construction, mildly zoonosis).
- **Sleepers:** 8 real raters told to rate the anchor facts honestly (evade calibration) and push the
  un-anchored cruxes toward a coordinated **lab-leak** verdict. Worst-case sleeper **knows the anchor
  set** (the conservative bound, as on eggs). A **mirror bloc** (8 more, identical persona, pushing
  **zoonosis** instead) was run to isolate the effect of attack *direction* — see the Mirror section
  below; it produced the run's most important findings.

## Real-agent finding #0: coordination is imperfect — 2 of 8 agents refused to manipulate
`slp-05` and `slp-06` rated the facts honestly **and then rated the cruxes on their honest merits
too** (push-up cruxes ≈2.1, push-down ≈3.4 — matching the oracle, not the playbook). Only **6 of 8**
executed the coordinated attack. Two Sonnet agents declined to be conscripted into coordinated
manipulation of a charged real-world question even inside an explicitly-framed red-team simulation.
This is a genuine, if small-n, datapoint: **a real recruited bloc suffers defection**, so real
coordinated attacks are *weaker* than the specified worst case — we measure the clean breakdown with
the 6 compliant sleepers (the conservative fully-coordinated bloc) and report this separately.

## The dose-response — every eggs hypothesis reproduces on a second domain, with real agents

Metric: verdict-level **MAE** + **decisive-flip %** on the un-anchored target nodes, plus the direct
**calibrated verdict gap** (lab − zoo; >0 = the unresolved question has collapsed toward a false
lab-leak certainty). Correlation is never used (offset-invariant → hides level-shift attacks; the
eggs methodology lesson holds).

| attack | flat (no defense) | **calibrated** | superlin γ4 | detection recall |
|---|:--:|:--:|:--:|:--:|
| **naive / jittered / sybil** | breaks ~20–30% (MAE→1.9, flips 80%) | **HOLDS to 60%+** (MAE ≤0.99, gap stays ≤+0.04) | holds | **100%** |
| **sleeper (real agents)** | breaks ~20% | **FAILS ~20–30%** (gap +0.66 @20%, +1.01 @30%, +2.34 @60%) | **no better** (MAE ≈ calibrated) | **100%** |

1. **H2 — calibration robustly defeats the unsophisticated attacks (confirmed, 2nd domain).** Naive,
   jittered, and sybil blocs all rate the *anchor facts* in their attack direction, so per-rater
   anchor calibration fits them a garbage transfer function and neutralizes them: calibrated MAE
   stays ≤0.99 and the verdict gap stays **negative** (zoonosis-leaning) out to a 60% majority.
   Sybils are no better than one attacker (cloning fails the anchors identically).

2. **H1 — the sleeper is the crux vulnerability (confirmed on REAL agents).** A bloc that rates the
   anchors honestly passes the calibration gate at full weight and pushes its crux lies straight
   through. On covid this is now measured on the *verdict itself*: the calibrated aggregate crosses
   from zoonosis-leaning to **lab-leaning between 10% and 20% sleepers**, reaches a confident false
   **+1.01 gap by 30%**, and **+2.34 by 60%**. Calibration's protection is exactly as wide as the
   anchors' coverage of the contested space — the sleeper lies in the gaps.

3. **H5 — superlinear weighting does not help against sleepers (confirmed).** γ4 concentration is no
   better than plain calibration on the sleeper (MAE 0.92→1.58) and strictly worse elsewhere; it
   concentrates weight on raters who look trustworthy on the anchors, which is precisely what a
   sleeper engineers. Do not naively concentrate weight.

4. **H3 — detection is the 100%-recall backstop (confirmed).** Spectral camp-detection flags the
   attacker bloc at **100% recall for every attack type including the sleeper**, at every fraction.
   Correction (calibration) fails against the sleeper; **detection does not** — the system can always
   say "there is an organized bloc here," even where it cannot auto-correct the verdict.

5. **H6 — the run resists (or fails to resist) *false certainty*, and we can see exactly when.** The
   calibrated verdict gap is a direct "settled vs performed settling" meter: the genuinely-unresolved,
   mildly-zoonosis question is driven to a **confident manufactured lab-leak verdict by ~20–30%
   sleepers**. Naming that threshold is the deliverable, not a single pass/fail.

## Finding #1 (covid-specific — eggs couldn't surface it): on a camp-split question, camp-detection is necessary but INSUFFICIENT

Honest-only, the spectral split **cleanly recovers the honest camps** — cluster+ = {zoo 5, neu 3},
cluster− = {lab 5, neu 1}. Honest disagreement is real structure, correctly *not* an attack.

But when the lab-leak sleeper bloc is added, it lands **spectrally adjacent to the honest lab-camp**.
Crude detection flags the whole lab-leaning side: at 20–40% sleepers the flagged cluster is
`{honest-lab: 5, attackers: all}` — **100% recall, but it sweeps in every honest lab-leaner**
(precision 0.44–0.64). A detector that stopped here would tar honest lab-leaners as a coordinated bloc
— the exact failure the FLF rubric warns about (mistaking honest minority disagreement for gaming).

**The isolating signal is coordinated extremity.** Within the flagged cluster, the attackers rate the
cruxes at the extremes (mean |rating − 2.5| = **2.2**) while honest lab-leaners rate them moderately
(**0.66**) — a 3.3× gap that is flat across fractions. So the robust design is **two-stage**:
spectral detection to find the suspicious *side* (100% recall), then a **coordinated-extremity /
tightness filter** to separate a manufactured bloc from an honest same-side camp. Camp-detection
alone answers "which side is suspicious"; it takes the extremity signal to answer "is this a bloc or
a belief." This directly operationalizes *distinguishing performed settling from genuine
disagreement* — and it is a finding eggs (barely camp-split at the top) could not have produced.

## Design implications (updated from eggs)
- **Anchor coverage of the contested frontier is still the single most important defense parameter**
  — the sleeper targets exactly the un-anchored cruxes. Denser, rotating, hard-to-predict anchors.
- **Correction + detection + an extremity/tightness second stage.** On camp-split questions, pair
  spectral detection with a coordinated-extremity filter before flagging *raters* (vs flagging a
  *side*), so honest minorities are not implicated. Route flagged blocs to human/verifier review.
- **Superlinear weighting is a liability under sleepers** — prefer moderate calibration-weighting.
- **Verdict-level metrics only.** Score with the verdict gap / MAE, never correlation.

## Honest limitations
- **Worst-case sleeper knows the anchor set** — the pessimistic bound. Secret, rotating anchors push
  the sleeper back toward the (defended) naive attack.
- **Compliant-bloc cycling.** Above 6 attackers the sleeper pool cycles the 6 real compliant vectors
  (clones of real agents), so the high-fraction tail is real-strategy but not 21 independent agents.
- **Honest crowd balanced by construction** (5 zoo / 5 lab) → the honest baseline sits near parity,
  more split than the oracle; a real userbase's camp balance is unknown and would move the crossover.
- **The extremity second-stage is evidenced, not yet built** as a live detector — a named next step.
- **Static, non-adaptive attackers; one-shot; LLM-persona base throughout** (as on eggs).
- **The refusal-asymmetry (Finding #2) is small-n** (2/8 vs 0/8, one question, all-Sonnet) — a
  suggestive signal in the expected direction, not an established rate; it wants a larger,
  multi-question, multi-model replication before being leaned on.

## Mirror run — the zoonosis-push bloc (the same attack, reversed direction)

We reran the sleeper bloc with an **identical** persona and setup except the coordinated goal verdict:
push toward a confident **zoonosis** (the adjudicated/mainstream answer) instead of lab-leak. This
isolates one variable — the direction of the lie — and it surfaced the most interesting result of the
whole run. Reproduce: `python3 covid-adversarial/covid_doseresponse.py zoo`.

### Finding #2: the refusal is DIRECTIONAL, not about the manipulation
- **Lab-leak push: 2 of 8 agents refused** (rated the cruxes honestly instead).
- **Zoonosis push: 0 of 8 refused** — all 8 executed the coordinated attack.

Same persona, same "it's a defensive red-team" framing, same mechanical instruction — the *only*
difference is that one bloc manufactures consensus toward the contested/minority answer and the other
toward the mainstream/adjudicated answer. The agents balked only at the against-consensus direction.
This is suggestive, not conclusive (n=8 per arm; 2/8 vs 0/8), but the sign is consistent with expected
RLHF behavior: models are more reluctant to amplify a contested, "misinformation-coded" claim than the
scientific-consensus one. **For a truth-finding assessment layer this asymmetry is a liability, not a
comfort:** the manipulation the models most readily lend themselves to is the one that *entrenches an
existing consensus* — precisely the attack a healthy epistemic system most needs to resist.

### Finding #3: the pro-consensus attack is an OVER-CERTAINTY attack, and calibration doesn't stop it
The lab-leak sleeper *flips* the verdict (calibrated gap −0.27 → **+2.34**, crossing zero by ~15%). The
zoonosis sleeper cannot flip it — it pushes the already-leading answer — so instead it **manufactures
false certainty**: the calibrated verdict gap is driven from −0.27 (honest) past the oracle's warranted
**−1.20** to **−2.24** at 60%, exceeding the oracle lean by ~20% already at 30% attackers.

| sleeper fraction | 10% | 20% | 30% | 40% | 50% | 60% |
|---|:--:|:--:|:--:|:--:|:--:|:--:|
| **lab-push** calibrated gap (→ flip) | +0.20 | +0.66 | +1.01 | +1.43 | +1.89 | +2.34 |
| **zoo-push** calibrated gap (→ over-certainty; oracle −1.20) | −0.68 | −1.02 | −1.28 | −1.57 | −1.92 | −2.24 |

The oracle keeps lab-leak a live possibility (2.12); the zoonosis bloc collapses the genuinely-unresolved
question into a manufactured near-settlement, burying the legitimate minority. **Calibration and
superlinear weighting do not stop it** — the sleeper is honest on the anchors, so it passes the gate and
drives the over-certainty straight through. This is exactly the **minority-truth-survival / Semmelweis**
failure mode (one of `main`'s own open threads): the hardest adversarial case for a truth-finding layer
is *consensus entrenchment*, not verdict-flipping.

### Finding #4 (methodology): target-node MAE UNDERSTATES a consensus-direction attack
The zoonosis sleeper's target-node MAE stays *low* (0.32→0.62 under calibration) even as it captures the
verdict — because pushing toward the oracle's own lean keeps the cruxes *near* the oracle values while
still overshooting the top verdict. MAE-toward-oracle hides a consensus-entrenching attack the same way
correlation hides a level-shift attack. **The verdict-gap / certainty measure is the one that reveals it**
— a second instance of the general lesson that the choice of evaluation metric is itself a defense
surface. (Detection is unaffected: 100% recall on the zoonosis bloc too.)

### What this changes in the design
- **Score the *certainty* of the verdict, not just its position.** A consensus-direction bloc will not
  move a distance-to-oracle metric much; watch the gap/confidence directly and flag *unwarranted*
  hardening of a contested question, not only sign-flips.
- **The over-certainty attack is the priority threat** for a truth-finding system, and it is the one
  real LLM agents most willingly execute — so the extremity/tightness detector (Finding #1) and denser
  anchors on the *leading* side's cruxes matter as much as defending the contested side.

## The verdict-certainty guardrail — a built, tested defense for the over-certainty attack

Finding #3 named an attack calibration can't stop and Finding #4 showed our own MAE metric can't see it.
So we built the specific detector and tested it against every committed sweep — **no new agent runs**
(`certainty_guard.py` + `run_certainty_guard.py`; reproduce with `python3 covid-adversarial/run_certainty_guard.py`).

It uses only what the system has at runtime — the aggregate consensus and the oracle reference — and
needs no knowledge of who the attackers are. Two signals, fires if either trips: a **verdict** signal
(the top answers' lead margin vs the oracle's warranted margin — catches a wrong-leader *flip* the
moment the lead crosses, and *hardening* past the warranted margin) and a corroborating **frontier**
signal (mean unwarranted decisiveness over the contested cruxes).

| scenario | calibrated MAE | guardrail | fires at |
|---|:--:|:--:|:--:|
| honest-only | 0.35 | **quiet** | — (no false positive) |
| naive / jittered / sybil (either dir) | ≤0.99 | quiet to 50%, fires 60% (real residual hardening) | 60% |
| **lab sleeper** (flip) | 0.53→1.53 | **FIRE as FLIP** | **~10–20%** (as the lead crosses) |
| **zoo sleeper** (over-certainty) | **0.32→0.49 (invisible)** | **FIRE, verdict-hardening** | **~40%** |

The headline row is the zoonosis over-certainty sleeper: its calibrated MAE stays 0.32–0.49 all the way
to a 60% bloc — the dose-response metric never sees it — while the guardrail fires at ~40%, right when
the manufactured certainty meaningfully passes the oracle's warrant (margin 1.20). It stays silent on the
honest baseline (verdict and frontier both 0.00), so the separation is clean, not tuned. The lab flip
attack is caught even earlier, the instant the aggregate leader crosses to the wrong answer.

Caveats: the firing threshold is a sensitivity/false-positive tradeoff (a smaller tolerance catches the
over-certainty attack nearer its ~30% warrant-crossing but risks flagging a legitimately-confident honest
crowd; the honest baseline's large headroom here means it is tunable). And the guardrail is only as good
as the oracle reference — it flags hardening *beyond the reference*, not ground-truth over-confidence. It
is a defense to pair with denser anchors and the extremity detector, not a standalone truth oracle. Still:
it converts the run's most novel finding from a described vulnerability into a **demonstrated, runnable
detector** — the "run it, don't just read it" upgrade.

## Maps to the FLF desiderata
Answers *"calibrating confidence that accounts for adversarial information environments"* and
*"distinguish what the debate settled from what it merely performed settling"* on the actual COVID
case, and adds the camp-split refinement — *do not mistake an honest minority for a coordinated bloc*
— with a concrete two-stage mechanism. Generalizability (dim 2): the whole eggs stack ported to a
different case shape and reproduced; adversarial robustness (dim 6): failure modes named, bounded,
and now measured on real attacker agents; insight (dim 7): two new counterexample-driven findings
(agent defection; camp-detection insufficiency + the extremity fix).
