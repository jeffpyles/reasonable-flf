# Cold-starting reasonableness at scale — what the data actually supports

*Six linked experiments (e1–e8 in this directory — probe-item selection folded into e5,
cross-run transfer into e1; all stdlib, all reproducible from the committed logs, run from
the repo root) on the fundamental question: in a good-faith
userbase, how do you reliably find the true signal-providers, how fast, and how does it
survive scale (millions of nodes/users, sparse ratings)? Adversarial concerns deliberately
out of scope. Builds on `review/REVIEW.md` (2026-07-10).*

---

## The five load-bearing results

**1. "Reasonableness" is two different quantities, with wildly different measurability.**
Within a homogeneous good-faith crowd (eggs-p5's 52 Haiku), per-rater competence differences
are barely a stable trait: split-half reliability of a ~10-item competence estimate is 0.11,
per-item reliability r1 ≈ 0.013, so a rater needs **~77 ratings for a 0.5-reliable estimate,
~180 for 0.7** (E2). No scoring rule can beat the reliability of the thing it estimates: at a
20-rating budget, *any* rule's correlation with true competence is capped at ~0.45. By
contrast, a systematic **disposition** (eggs-p6's biased-vs-evidence divide) has r1 ≈ 0.107 —
reliably detectable in **~8 ratings**, near-perfectly in 20 (E2, E3). The design consequence:
at realistic per-user budgets, reputation should classify *dispositions and tiers* (cheap,
reliable) and only slowly accumulate *fine quality rank* (expensive, noisy). Chasing a
fine-grained global ranking of similar-quality good-faith users at low n is measuring noise.

**2. The eggs-p4 "inversion" was mostly a label artifact; the true failure is tier burial.**
Re-baselined against oracle competence (E1; p4/p5 node ids align 79/79), crowd-only alignment
is **+0.11 — blind, not inverted** (the canonical −0.54 was driven by the care label, which
p5's own data shows anti-correlates with real competence). What *is* robust: experts stay at
the 11th percentile under alignment and rise to the 79th under discrimination. So the
pathology to design against is *burial of a sharper tier/disposition*, not systematic
inversion within the crowd — consistent with result 1: within-crowd differences are mostly
noise; the real signal lives at tier/disposition granularity.

**3. Protocol moves accuracy more than any scoring rule studied.** The same personas rating
the same nodes tracked truth at **0.52 in the p4 run vs 0.89 in the p5 run** (E1 matched-items
test). Candidate causes (not separable here): p4 rated mid-construction with visible prior
ratings/comments and mixed target types; p5 was a clean, independent, focused pass. Whatever
the mix, the elicitation-protocol lever (blind first-pass rating, social information hidden
until after commit) dwarfs every reputation-rule improvement measured in this whole
investigation — and it's nearly free. (It also matches the wisdom-of-crowds literature on
social influence degrading crowd accuracy.) Cross-run reputation transfer measured ~0 (E1),
but E2's ceiling shows that's expected attenuation at these budgets plus the protocol gap —
not proof there's no trait; the p6-style disposition transfers essentially perfectly.

**4. For contested regions, cluster-then-adjudicate is the efficient machine.** On p6,
unsupervised spectral clustering of the rater-agreement matrix finds the divide (axis
strength 0.83 vs 0.27 on the no-divide p5 control — the statistic detects real factions
without hallucinating them; tier accuracy 0.90) (E5). Then:
- **1 contested anchor adjudicates the right cluster 100% of the time** (2–3 for margin);
- adjudicated winning-cluster mean scores held-out corr **0.88** — matching the 10-anchor
  full-calibration recipe at **1/5 the oracle budget**;
- newcomers classify into a cluster from **1–3 probe items** (the max-separation items),
  *no oracle needed* — the oracle is spent once per divide, not per user.
Aggregator head-to-head under stress (E6): **calibration** (per-rater affine on anchors +
inverse-residual-variance mean, from `review/bias_correction.py`) needs **zero competent
raters** — it extracts truth from the 16 biased raters alone (held-out 0.89 at nc=0),
dissolving the "minimum 2–3 competent" floor — and degrades gracefully under wrong anchors,
but is unstable below ~10 anchors. **Cluster-adjudication** runs on 2 anchors but needs ≥2–3
competent raters to form a findable cluster. **Exclusion (γ=6)** matches both on clean
plentiful anchors but shatters on wrong ones (review: −0.8 at 3–4 bad of 10). They are
complementary along the two anchor-risk axes (few vs wrong); γ=6 exclusion is dominated and
should be retired as the default. All three pass the healthy-crowd harm check (p5: 0.933 flat
→ 0.934–0.937).

**5. At scale, anchors are worthless without routing — and one global reputation number is
structurally insufficient.** Sparse simulation (E8: 1200 users × 2400 items, 25% contested
with a 55% biased local majority, 30 contested anchors, eggs-calibrated noise): under pure
random assignment, essentially **no user ever rates 3 anchors** and the contested consensus
stays broken (0.34) at every density. Routing a ~20% probe slice of each user's budget
(≥3–5 anchor/probe ratings per user) flips contested accuracy to **0.80–0.92**, and
reputation then propagates: users who never touched an anchor get scored by tracking the
anchored consensus (rep~comp ≈ 0.5–0.6 at 2 hops), matching E3's dense-data finding that
disc-vs-**fixed**-consensus is the best newcomer signal (competent newcomers reach the ~85th
percentile in 4–6 ratings) while disc-vs-**raw**-consensus is actively harmful in split
populations (−0.2 to −0.4 at every budget). The trap the simulation exposes: biased-but-
diligent users rate the 75% uncontested items *well*, so any item-agnostic reputation gives
them good scores while contested items stay theirs. **Disposition must be assessed
per-contested-region (which the probe slice does directly); general diligence is the only
part that can be a global scalar.**

---

## The architecture these results converge on

Cold-start pipeline for a new user (total cost ~5 of their first ~20 ratings):
1. **Blind elicitation always**: rate before seeing scores/comments (result 3 — the cheapest
   accuracy win in the entire investigation; also what keeps ratings usable as independent
   signal for everything below).
2. **Probe slice**: route 3–5 of the first ratings to the active anchor/probe set for the
   region they're rating in. This immediately (a) classifies their disposition per contested
   cluster (result 1: ~8 ratings suffice; E5: often 1–3), (b) gives an anchor-agreement score
   where anchors exist.
3. **Ongoing**: score them by discrimination against the *anchored/adjudicated* consensus
   (never the raw one), shrunk by n/(n+K).
4. **Shrinkage that matches measured reliability**: the Spearman-Brown curve k·r1/(1+(k−1)·r1)
   *is* the spec's conf = n/(n+K) with **K = (1−r1)/r1**. So K is not a taste knob — it's
   estimable online from split-half reliability of each signal. Measured here: K ≈ 8 for
   disposition-type signals (the current default, coincidentally right), **K ≈ 76 for
   fine quality-rank** (the current default is ~10× too trusting at low n). Different
   reputation inputs need different K.

Contested-region machinery (runs per detected divide, not per item):
5. **Detect divides** with the spectral split-strength statistic on the local rater-agreement
   matrix (cheap; doesn't fire on healthy regions).
6. **Adjudicate** the divide with 2–3 contested anchors when available (E5). Where anchors
   are plentiful (~10+ per region), **calibrate raters** instead — it extracts signal even
   from a wholly-biased pool and tolerates anchor errors (E6). Show per-cluster consensus in
   the UI regardless (the v1.4 dispersion amendment's natural completion — for genuinely
   contested normative questions, adjudication may be impossible and the honest output *is*
   the cluster structure).
7. **Aggregate** with moderate concentration on the adjudicated/calibrated weights. Steep
   γ is unnecessary once calibration or adjudication has done the work, and it's the fragile
   ingredient (review findings).

Scale mechanics:
8. **Anchor supply is a routing problem, not just a sourcing problem** (result 5): a small
   anchor set works iff pushed into everyone's stream. Constructed reasoning-anchors
   (R-dimension items with provably-bad/good inference, per `review/REVIEW.md` §4.2) remain
   the most scalable supply; per-region contested anchors are the highest-value placement.
9. **Reputation propagates 2 hops fine** (anchors → exposed users → fixed consensus →
   everyone else), so the oracle budget stays O(anchors), not O(users) — and with
   cluster-adjudication, O(divides) (E5/E8).

What NOT to build (each disconfirmed here):
- Fine-grained global ranking of good-faith users at low budgets (E2 ceiling — it's noise).
- Newcomer scoring against the raw crowd consensus (E3 — harmful in exactly the populations
  where reputation matters).
- Level-agreement (alignment) as a quality signal in any variant (unchanged conclusion).
- γ=6-style hard exclusion as the default aggregator (dominated per E6 + review fragility).
- BTS as currently elicited (review §3.1: only 3/79 items even have a non-trivial
  surprisingly-popular decision; parked until prediction elicitation is first-class).

---

## E9 addendum — soft divides: where the machinery breaks (and doesn't)

Sweeping divide strength synthetically (e9: 24 partially-biased + 6 competent, 6 seeds/level;
biased perception pulled toward a shared wrong target with weight `bias_w`):

| bias_w | flat harm (corr) | detect strength | cluster acc | fix (2-anchor) | calib nc=0 |
|:--:|:--:|:--:|:--:|:--:|:--:|
| 0.0–0.35 | 0.98–0.99 (healthy) | 0.23–0.25 (null) | ~0.55 (no divide) | 0.96–0.99 | 0.89–0.99 |
| 0.50 | 0.92 | 0.25 | 0.55 | 0.88 | **0.01** |
| 0.65 | **0.11** | 0.25 (!) | 0.82 | **0.78** | 0.47 |
| 0.85 | −0.94 | 0.43 | 0.99 | 0.98 | 0.98 |

Four refinements to the architecture:
- **The flat consensus is more robust than feared**: with 80% of raters carrying a
  half-strength shared bias it still tracks truth at 0.92. The contested machinery is needed
  only past a fairly extreme threshold — the default site posture can stay simple.
- **The global spectral-strength trigger misses the transition zone**: at bias_w=0.65 harm is
  severe (0.11) but the strength statistic still reads null (0.25). The trigger should instead
  be **per-item bimodality/dispersion** — exactly the v1.4 histogram data — or a
  permutation-null-calibrated strength; the raw eigenvalue share is not sensitive enough.
  (Even so, in that zone clustering is imperfect (0.82) yet end-to-end repair still lifts
  0.11 → 0.78.)
- **Calibration's real failure mode is variance destruction, not softness**: at bias_w=0.5
  under this construction the biased perception becomes literally constant (0.5·q + 0.5·(5−q)
  = 2.5) — no affine map can recover rank information that no longer exists, hence 0.01;
  at 0.85 the perception is a strong *monotone distortion* and calibration inverts it
  perfectly again (0.98). Lesson: calibration recovers bias-as-transformation, not
  bias-as-information-loss. Cluster-adjudication survives the middle zone better; they remain
  complementary. (The exact w=0.5 null is an artifact of the b=5−q construction, but the
  qualitative boundary — recoverability requires the biased view to retain rank info — is
  general.)
- **False-positive machinery is nearly harmless**: running cluster-adjudication on healthy
  populations costs ≤0.04 corr (0.92→0.88 worst case). Firing the trigger too eagerly is
  cheap; missing a real divide is not — bias the trigger toward sensitivity.

## E10 addendum — the contested-item trigger is rating STDEV, not a bimodality score

The E9 recommendation ("fire the machinery on per-item bimodality") was directionally right about
*per-item* but wrong about *which statistic*. Pooling all 237 rated node-items across p5/p6/p7 and
labelling each by whether the flat consensus is actually far from oracle truth (`e10_trigger_tuning.py`):

- **Plain stdev is the trigger.** corr(stdev, |flat−truth|) = **+0.79**; a **stdev ≥ 0.7** threshold
  catches 87% of the genuinely-wrong items with **0% false fires** on the healthy p5 crowd (≥ 0.5 →
  97% recall at 4% false fire). Mean stdev cleanly ranks the regimes: p5 healthy 0.22, p7 soft 0.42,
  p6 strong 0.76.
- **Sarle's bimodality coefficient is a poor trigger** here: corr just +0.40, and even at the textbook
  0.555 cutoff it false-fires on 46% of healthy p5 items. At ~20–52 discrete-ish ratings on a 0–5
  scale, BC is too unstable to separate "two humps" from ordinary spread.
- **Consequence:** trigger the machinery on **stdev** (favor recall — E9 showed false fires cost
  ≤0.04 corr while misses are dangerous — so ~0.5–0.6 is defensible). The *display* distinction the
  v1.4 amendment wanted (contested-bimodal vs uncertain-wide) should NOT lean on BC; confirm
  "contested" by whether camp-detection returns a *stable* split (E9's multi-restart consensus), not
  by a moment-based shape score. Net: one cheap number (stdev) gates the expensive machinery; the
  clustering itself certifies whether a real divide exists.

## Honest limitations

- **LLM personas likely understate stable human variance.** Real crowds show durable
  individual skill differences (forecasting-tournament literature); prompted Haiku personas
  may be artificially homogeneous, making the E2 "fine rank is noise" ceiling too pessimistic
  for humans. The *method* transfers (measure r1, set K from it) even if the constants don't.
- One domain, one bias construction, oracle = a Sonnet expert panel that shares a model family
  with the competent tier (review §2.5). The E8 world, while calibrated to eggs parameters, is
  synthetic — its hawks are cleanly clusterable; real divides are softer and plural.
- p6's divide is maximal (competence 0.01 vs 0.89). Softer real divides will need more than
  1 anchor to adjudicate and more than 1 probe to classify; treat E5's constants as best-case.
- The protocol effect (0.52 vs 0.89) is observational across runs, not a controlled A/B; it
  confounds blind-vs-social with target-mix and graph maturity. It's the single most valuable
  thing to A/B in the next agent run.
- Held-out evaluation sets inherited from the p6 design are small (8 items); E8 compensates
  with scale but is synthetic. Adversarial behavior is entirely out of scope by request
  (`review/REVIEW.md` §4.4 sketches that program).

## Suggested next experiments (in value order)

1. **Protocol A/B run**: same population, blind vs social-visible rating — controlled test of
   the biggest lever found (result 3).
2. **Soft-divide stress test**: a p7 population with a *mild* shared bias (competence 0.4 vs
   0.8, overlapping clusters) — where do cluster detection (E5) and the probe classifier
   degrade, and does calibration still extract signal at nc=0 (E6)?
3. **Multi-region graph**: two contested clusters with different dispositions per user —
   validates per-region disposition + global-diligence factorization (result 5) on real
   agents rather than simulation.
4. **Online K estimation**: implement split-half reliability + K=(1−r1)/r1 in `assess.py` as
   the confidence constant, verify on p5/p6 logs that it reproduces E2's numbers from inside
   the system.
5. **Constructed R-anchor validation**: author ~10 known-answer reasoning items, check that
   R-anchor agreement predicts A-dimension competence (the transfer the whole anchor-supply
   strategy rests on).
