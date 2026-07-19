# eggs-p8 — bias × model, de-confounded: does camp-detection find *disposition* or *capability*?

*A balanced 2×2 (biased/neutral × haiku/sonnet, 7 raters each, 28 total), built to separate the two
axes that were entangled in eggs-p7, where the recovered camp axis tracked disposition (0.82) and
model (0.79) inseparably because bias was haiku-only. Here the SAME two disposition prompts run on
BOTH models, all blind (enforced Rating mode), all 79 nodes saturated. Oracle = eggs-p5 8-expert
panel; adjudication cross-checked against the independent Fable+Opus panel anchors. Reproduce:
`python3 eggs-p8/harness/analyze_p8.py`.*

## 1. Disposition dominates capability (2×2 accuracy)

Accuracy = correlation of a rater's node ratings with oracle truth:

| | haiku | sonnet | **row mean** |
|---|:--:|:--:|:--:|
| **biased** | 0.39 | 0.43 | **0.41** |
| **neutral** | 0.68 | 0.86 | **0.77** |
| **col mean** | 0.53 | 0.64 | |

- **Disposition main effect +0.36; model main effect +0.11** — disposition matters ~3× as much as
  model tier.
- **Capability does not rescue a biased rater.** biased-sonnet (0.43) ≈ biased-haiku (0.39): giving
  the bias a stronger model barely helps. And a biased frontier model (0.43) is **worse than a
  neutral weak one** (neutral-haiku 0.68). A shared directional prior degrades a rater more than a
  model-tier gap does, and raw capability doesn't reason its way out of a prior it's been given.
- **Capability helps when it isn't fighting a bias:** among neutral raters sonnet (0.86) clearly beats
  haiku (0.68) — the +0.13 interaction. So model tier is a real accuracy lever, but only second-order
  to disposition.

The design reading: this is why reputation must assess **disposition per contested region** and not
lean on any "these are the capable/high-tier raters" global proxy — a capable rater carrying a
topic-local bias is exactly the dangerous case (good general record, wrong here), and capability
alone won't surface or fix it.

## 2. The headline — camp-detection finds DISPOSITION, cleanly across model (p7's confound resolved)

Multi-restart spectral split (stable), oriented so cluster 1 = higher-accuracy side:

- **axis vs DISPOSITION (biased|neutral): 0.96** · **axis vs MODEL (haiku|sonnet): 0.54** (≈ chance)
- cluster-1 share per cell: biased-haiku **0.14**, biased-sonnet **0.00**, neutral-haiku **1.00**,
  neutral-sonnet **1.00**.

Both biased cells land together in one cluster *across models*, both neutral cells together in the
other *across models*. The split follows the **belief divide**, not the capability gap. This
decisively resolves the p7 ambiguity: the contested-region machinery detects and adjudicates a
shared *disposition*, not merely which model a rater is — exactly the thing we want it aimed at. (It
also means the "which camp" a probe assigns a newcomer to is a statement about their view, not their
horsepower.)

## 3. The Fable+Opus panel anchors work live — as well as the expert-derived ones

Adjudication/calibration on eggs-p8's contested cluster, **fair common held-out set** (7 items, flat
baseline +0.77), comparing anchors derived from the p5 expert oracle vs the independent Fable+Opus
panel (`anchors.json`):

| anchor source | calibrate full pool | calibrate biased-only (nc=0) |
|---|:--:|:--:|
| p5-panel (expert-derived) | +0.60 | +0.84 |
| **Fable+Opus panel** | **+0.74** | **+0.97** |

The panel anchors **match or beat** the expert-derived ones — while sharing only 3 nodes with that
set and containing **no Sonnet** (so they're genuinely independent of p8's Sonnet raters). Combined
with the deliberation's convergent validity (+0.98 vs the p5 oracle on anchor-grade nodes), this
confirms the panel-anchor mechanism end-to-end: a frontier-model panel can forge adjudication anchors
that drive the calibration machinery as well as our **Sonnet expert-panel** oracle does. (Crucial
caveat, easy to overstate: that oracle is itself a model panel, not humans — so this shows a
Fable+Opus panel agrees with a Sonnet panel, NOT that either tracks human/ground truth. The whole
competence chain remains model-grounded; breaking that grounding is a standing open thread.) (Earlier
per-source
numbers in `analyze_p8.py` §2 used *different* held-out sets per source — an apples-to-oranges
artifact; the common-held-out comparison above is the fair one.)

## 4. Ranking speed (E2)

Split-half per-item reliability r1: all-28 **0.069**, haiku 0.052, sonnet 0.087 (ref: homogeneous p5
crowd 0.013, strong-disposition p6 0.107). A population with a real disposition split ranks faster
than a homogeneous one; within it, the higher-capability tier is a bit faster still — consistent with
p7 and the general "heterogeneity speeds ranking" result.

## Honest limitations
- Small held-out sets (7 fair / 8–14 per-source items on one 79-node graph); treat the anchor deltas
  as directional. The disposition/model *main effects* rest on 28 raters × 79 nodes and are solid.
- Bias is prompt-induced and moderate. "Capability doesn't rescue bias" is shown for a clearly-stated
  prior; a subtler or capability-correlated real bias could interact differently — the claim is that
  raw capability is not *automatically* protective, not that capability never helps.
- The panel anchors were selected on eggs-p6's contested cluster (partial overlap with p8's), yet
  still calibrated p8 well — encouraging for transfer, but a same-cluster placement would be the
  stronger test.
- Model-family caveat persists for the p5 oracle (Sonnet) — which is exactly why the Sonnet-free panel
  cross-check matters, and it held.

## Where this leaves the program
Two of the three open weaknesses from prior rounds are now closed: the disposition/capability confound
(camp-detection tracks disposition, 0.96) and the anchor-supply/independence question (panel anchors
validated, and Sonnet-free). The reputation architecture's core commitments survive a de-confounded
test: **disposition, not capability, is what the machinery must and does find; assess it per region;
and anchors can be manufactured by a deliberating frontier panel when no ground-truth source exists.**
