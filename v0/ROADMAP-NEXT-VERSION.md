# Roadmap — next-version moves for the assessment layer

> **Note (2026-07-19):** the current, full roadmap — including the items beyond the assessment
> layer — is [ROADMAP.md](../ROADMAP.md) at the repository root. This file remains as the dated,
> finding-by-finding engineering detail behind its Section 1.

*Logged 2026-07-15 after the eggs + covid adversarial runs (see `eggs-adversarial/FINDINGS.md` and
`covid-adversarial/FINDINGS.md`). These are the improvement steps the runs pointed to but that we are
**deliberately deferring** past the FLF deadline — the submission is better served by developing other
areas and by honestly describing what we've done and where it goes. This file IS that description of
direction; the code changes below are future work, not commitments for this submission.*

Ordered by leverage. Each entry: what it is, why (which finding it answers), rough cost, and the
failure mode it closes.

## Tier 1 — the defenses the runs proved we need

### 1. Verdict-certainty guardrail — DONE (prototyped + tested, 2026-07-15)
- **Status:** built and validated offline against every committed covid sweep, no new agent runs —
  `covid-adversarial/certainty_guard.py` + `run_certainty_guard.py`, written up in
  `covid-adversarial/FINDINGS.md`. Quiet on the honest baseline and on calibration-defended crude
  attacks; fires on the lab flip (~10–20%) and on the zoonosis over-certainty sleeper (~40%) whose
  calibrated MAE stays 0.32–0.49 (invisible to the dose-response metric).
- **What:** scores how *hard* a contested verdict has hardened (lead margin + frontier decisiveness vs
  the oracle warrant), not only where it sits, and flags *unwarranted* certainty on a question the
  oracle keeps live. Runtime inputs are only the aggregate + oracle reference (no attacker knowledge).
- **Why:** covid Findings #3/#4 — the pro-consensus sleeper can't flip the verdict so it manufactures
  false near-settlement, which calibration does **not** stop and MAE **hides**. Serves `main`'s open
  **minority-truth-survival / Semmelweis** thread.
- **Remaining (next version):** wire it into the live aggregator as a first-class flag/escalation;
  tune the sensitivity/false-positive tradeoff on more questions; test against an adaptive attacker.
- **Closes:** consensus-entrenchment / over-certainty capture (detection; correction still deferred).

### 2. Extremity / tightness second-stage detector (live component)
- **What:** after spectral camp-detection finds the suspicious *side*, apply a coordinated-extremity /
  tightness filter before flagging individual *raters* — so an honest same-side camp is not tarred with
  the bloc.
- **Why:** covid Finding #1 — on a camp-split question crude detection flags the whole lean (100%
  recall) but sweeps in honest same-side raters (precision ~0.5). The isolating signal exists and is
  strong (attacker crux-extremity 2.2 vs honest 0.66, a 3.3× gap), but it lives in analysis
  (`h4_diagnostic.py`), not in the pipeline.
- **Cost:** moderate. The signal is measured; the work is turning it into a two-stage detector with a
  calibrated extremity/tightness cut and precision/recall targets.
- **Closes:** false-positive flagging of honest minorities (mistaking belief for a bloc).

### 3. Denser, rotating, hard-to-predict anchors over the contested frontier
- **What:** expand anchor coverage of the un-anchored cruxes, rotate the anchor set, and keep it
  secret/unpredictable — with emphasis on the *leading* side's cruxes.
- **Why:** the sleeper's entire edge is knowing the anchor set and lying in the gaps
  (eggs + covid Finding H1). Secret, rotating anchors degrade a sleeper back toward the (defended)
  naive attack. The over-certainty attack (Tier-1 #1) operates on the leading side, so that side's
  cruxes need coverage too, not just the contested one.
- **Cost:** moderate-to-large (ongoing operational cost, plus anchor-forging compute). Fundamentally a
  coverage/economics problem, not an algorithm.
- **Closes:** the sleeper's anchor-gap exploit; caps the worst-case bound.

## Tier 2 — firm up the findings before leaning on them

### 4. Replicate the refusal asymmetry properly
- **What:** multiple questions, multiple models, larger n per arm.
- **Why:** covid Finding #2 (2/8 refused the contested push, 0/8 the mainstream push) is suggestive and
  in the expected direction, but it is small-n on one all-Sonnet question. It is currently reported as
  a signal, not a rate; a real claim needs replication.
- **Cost:** moderate (agent runs across a question set).
- **Closes:** the risk of over-reading a single-question artifact.

### 5. Adaptive / harder red-team
- **What:** an attacker that observes reputation scores and adapts; a sleeper that also *jitters* its
  target-claim lies to resist clustering.
- **Why:** every attacker so far is static and one-shot — a floor on attack strength, not a ceiling.
  Detection's 100% recall assumes the bloc coordinates tightly on the target claims; a jittering
  sleeper is the untested case that could stress it.
- **Cost:** large (a genuinely new harness).
- **Closes:** the "static-attacker" limitation named in both FINDINGS.

## Related design note
**`ORACLE-BUDGET-POLICY.md`** — where to spend scarce oracle-points at scale (both calibration and the
certainty guardrail can only act on oracle'd nodes). Triage by contestedness: verdict nodes first
(detection was carried by 2 oracle'd nodes), cruxes on demand for correction, a thin rotating anchor
layer, nothing on the uncontested tail. Oracle spend scales with contestedness, not graph size — the
scalability answer (FLF #4). Written up from the certainty-guardrail work below (#1).

## Tier 3 — breadth

### 6. Third case shape (black holes)
- **What:** run the assessment stack on the LHC black-hole graph (strong consensus with a vocal edge),
  partly built on `main` (`v0/swarm-blackholes*`).
- **Why:** completes three-shape coverage for the generalizability claim (FLF dim 2): eggs
  (genuine split) + covid (curated debate) + black holes (near-settled with an edge).
- **Cost:** moderate (graph exists; needs the oracle/honest/adversarial passes ported, which are now
  one-command each).
- **Closes:** the "two-domain" breadth limit.

---

## The through-line (why these and not others)
Both soft spots we found — the **sleeper in the anchor gaps** and the **over-certainty push toward the
existing consensus** — defeat calibration for the *same* reason: honest-on-anchors buys full trust. And
both were invisible to the metric we'd naively reach for (correlation hides level-shifts; MAE-to-oracle
hides consensus-entrenchment). So the next version's spine is: **(a) measure the right thing** (verdict
certainty, not just position), **(b) detect coordination by its shape** (extremity/tightness, not just
side), and **(c) shrink the gaps** (denser secret anchors). Correction alone was never going to be
enough; the durable design is correction + detection + escalation, with the metric chosen so the attack
can't hide in it.
