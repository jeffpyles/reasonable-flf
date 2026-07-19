# Dispersion regimes — when rating spread is a contested signal, and when it's noise

*Prompted by the fermi/main thread's `v0/archive/dispersion-handoff/` finding that rating dispersion is a
low-reliability contested signal. Re-assessed from the assessment-layer side; the result reconciles it
with our own `coldstart-lab` E10 ("the contested-item trigger is stdev") and sharpens both. Reproduce
the belief-camp half here: `python3 dispersion-regimes/regimes.py` (the lens numbers are from the fermi
handoff package).*

## The three regimes

| panel | between-group variance share | dispersion → contestedness |
|---|:--:|:--:|
| **our covid** — deliberate zoo/lab **belief-camps** (good-faith) | **82%** | strong (corr stdev↔error **+0.70**) |
| **eggs-p8** — biased vs neutral **camps** | 32% | real (corr **+0.50**) |
| **fermi covid** — bayes/domain/ev/skeptic **lenses** (good-faith) | 16% | none (AUC 0.42, reliability 0.37) |

## The finding
Dispersion's value depends entirely on **what generates it**, and the **between-group variance fraction
is the diagnostic**:

- **Belief-camp dispersion** (raters who disagree about what's *true*) → valid, tracks consensus error,
  and it **survives rater-offset removal** (the signal is in the node×camp interaction, exactly what
  spectral camp-detection reads).
- **Lens/style dispersion** (raters who differ in *emphasis*, not belief) → invalid; it's removable
  per-rater offset + noise. On the fermi panel, removing per-rater offsets roughly *doubled* the weak
  separation (AUC 0.42 → 0.60) — i.e. raw dispersion there was reliably measuring rater idiosyncrasy,
  not contestedness (reliable-but-invalid).

It is **not** "good-faith vs biased": our covid panel is good-faith and still shows a strong signal,
because its diversity is *belief* (zoonosis vs lab-leak), not *lens*.

## Reconciliation with coldstart-lab E10
E10's stdev worked because its dispersion was camp-driven (a biased belief split correlated with error);
the fermi panel's failed because its dispersion was lens-driven. Both correct. The unifying principle:
**the signal is the correlation structure across raters (camps), and raw stdev is a good proxy only when
that structure dominates the spread.** In a well-formed graph, disagreement is externalized into
antithesis structure, so per-node spread on a good node is low by design — which is why the reliable
"where is this contested" signal is **structural + correlational**, not per-node variance.

## What changed as a result (now live)
The corrected contested signal is in the package: `reasonable/assessment.py`
`detect_camps` (spectral belief-camp split + `between_group_fraction` diagnostic) and `camp_contested`
(nodes the camps disagree on), exposed as `graph.py assess`. And the phase-2 `lifecycle.py` contested
trigger **has been swapped** from raw stdev to STRUCTURAL contestedness (antithesis membership) as the
reliable primary signal, stdev demoted to a conservative secondary net (`test_lifecycle.py`; on eggs-p8
this correctly flagged 15 antithesis members the old stdev trigger missed). `main`'s PHASE2-SPEC needs
the matching definition update (see archive/MERGE-HANDOFF §5).

## Cross-vendor and human panels (the forward view)
Both add **more dispersion**, and its *latent* value rises — but only through calibration + camp-detection:
- **Cross-vendor AI:** adds genuine belief/knowledge diversity (valuable; lowers the shared-bias floor,
  the one thing that catches whole-generation biases) *and* vendor style/scale offsets (noise that
  inflates raw dispersion). Calibrate out the per-vendor offset first, then the residual belief-
  disagreement is the signal.
- **Open human rating:** the richest belief-camps *and* the worst noise (trolls, scale misuse,
  coordinated brigades) together. Raw per-node dispersion gets *less* usable; the correlation-structure
  reading gets *more* essential — it's what separates a coherent camp (correlated) from incoherent noise
  (uncorrelated) from an attack (correlated + extreme — the H4 extremity signal). Humans are also the one
  thing that breaks the model-on-model circularity, so a genuine human belief-split is the gold-standard
  contested signal — but only extractable with camp-detection + the adversarial defenses.

Net: more dispersion, higher *latent* signal, realized only via **calibrate + read the camp structure**,
never raw stdev — and the between-group fraction is how a panel measures, on itself, which regime it's in.
