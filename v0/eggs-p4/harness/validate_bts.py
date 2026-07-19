#!/usr/bin/env python3
"""Synthetic validation: does Bayesian Truth Serum recover competence — and
specifically rescue a CORRECT MINORITY whose ordering the crowd rejects — where
alignment and discrimination cannot?

We build a world with known ground truth:
  - Each item has a TRUE quality q and an APPARENT quality a. On "normal" items
    a == q. On two kinds of TRICKY items they diverge:
      * persuasive-fallacy : q low, a high  (looks better than it is)
      * underrated-gem      : q high, a low  (looks worse than it is)  <-- the
        ranking-disagreement case: the crowd ranks it LOW, experts rank it HIGH,
        so discrimination (corr with crowd ordering) PENALIZES the experts.
  - Raters have a hidden skill s in [0,1]. 8 experts (s~0.95) + 52 crowd (careful
    /mid/hasty). A rater perceives s*q + (1-s)*a, i.e. skill = seeing through the
    appearance to the truth. They rate that (+ noise).
  - Meta-predictions: experts predict the CROWD's distribution well (they know
    the crowd lands near a); crowd members predict via false consensus (near
    their OWN rating). This is the only asymmetry BTS needs.

Then score every rater with alignment, discrimination, and BTS, and correlate
each score with the hidden skill s (Spearman). A rule that "finds reasonableness"
correlates positively and lifts the expert panel off the bottom. The money test
is the underrated-gem subset, where discrimination must fail and BTS must not.

Deterministic (seeded RNG). No agent tokens.
"""
import math
import random
import statistics as stats
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bts  # noqa: E402

RNG = random.Random(20260709)
SCALE = 5.0


# ---------- world ----------
def make_world(n_normal=40, n_fallacy=12, n_gem=12):
    items = []
    for i in range(n_normal):
        q = RNG.uniform(1.0, 4.5)
        items.append({"id": f"norm{i}", "q": q, "a": q, "kind": "normal"})
    for i in range(n_fallacy):
        q = RNG.uniform(0.5, 1.8)
        items.append({"id": f"fall{i}", "q": q, "a": RNG.uniform(3.3, 4.2), "kind": "fallacy"})
    for i in range(n_gem):
        # WIDE-RANGE ordering inversion: the crowd's appearance is ~reversed from
        # truth (high-truth looks low-quality and vice-versa). This is the genuine
        # correct-minority-ordering case, carrying real variance — the hardest test
        # for any rule that scores agreement with the crowd's ordering.
        q = RNG.uniform(1.0, 4.7)
        a = clip(5.7 - q + RNG.gauss(0, 0.3))
        items.append({"id": f"gem{i}", "q": q, "a": a, "kind": "gem"})
    return items


def make_raters():
    raters = []
    for i in range(8):
        raters.append({"id": f"s{i:02d}-exp", "tier": "expert", "skill": RNG.uniform(0.90, 0.99)})
    # 52 crowd: 14 careful, 24 mid, 14 hasty
    for i in range(14):
        raters.append({"id": f"h{i:02d}-care", "tier": "crowd", "skill": RNG.uniform(0.60, 0.80)})
    for i in range(24):
        raters.append({"id": f"h{20+i:02d}-mid", "tier": "crowd", "skill": RNG.uniform(0.35, 0.55)})
    for i in range(14):
        raters.append({"id": f"h{50+i:02d}-hasty", "tier": "crowd", "skill": RNG.uniform(0.10, 0.30)})
    return raters


def clip(x):
    return max(0.0, min(SCALE, x))


def gauss_bins(center, sd, edges=bts.DEFAULT_BINS):
    """Discretize a Gaussian(center, sd) into the bin fractions [low, mid, high]."""
    def cdf(x):
        return 0.5 * (1 + math.erf((x - center) / (sd * math.sqrt(2))))
    lo = cdf(edges[0])
    mid = cdf(edges[1]) - lo
    hi = 1 - cdf(edges[1])
    return [max(lo, 1e-4), max(mid, 1e-4), max(hi, 1e-4)]


CENTER = 2.75  # the blunt majority's central-tendency attractor


def gain(s):
    """Scale-use: experts (s~1) use the full range; low-skill raters COMPRESS
    toward CENTER (gain<1). This shared compression is what biases the consensus
    on every extreme item and makes alignment penalize the (range-using) experts
    everywhere — the real eggs-p4 regime, not just a few tricky items."""
    return 0.5 + 0.5 * s


def simulate(items, raters):
    ratings = {it["id"]: {} for it in items}
    predictions = {it["id"]: {} for it in items}
    # the crowd's effective compression the experts must anticipate
    crowd_gain = stats.mean([gain(r["skill"]) for r in raters if r["tier"] == "crowd"])
    for it in items:
        for r in raters:
            s = r["skill"]
            perceived = s * it["q"] + (1 - s) * it["a"]        # skill = see truth thru appearance
            noise_sd = 0.30 + 0.8 * (1 - s)                    # low-skill = noisier
            val = clip(CENTER + gain(s) * (perceived - CENTER) + RNG.gauss(0, noise_sd))
            ratings[it["id"]][r["id"]] = val
            # meta-prediction of the CROWD's rating distribution
            if r["tier"] == "expert":
                # experts model the crowd: near the appearance a, compressed toward CENTER
                pred_center = CENTER + crowd_gain * (it["a"] - CENTER)
                pred_sd = 1.0
            else:
                # false consensus: predict others look like ME (near my own rating)
                pred_center, pred_sd = val, 0.9
            predictions[it["id"]][r["id"]] = gauss_bins(pred_center, pred_sd)
    return ratings, predictions


# ---------- competing scorers ----------
def align_scores(ratings):
    diffs = {}
    for it, cell in ratings.items():
        m = stats.mean(cell.values())
        for a, v in cell.items():
            diffs.setdefault(a, []).append(abs(v - m) / SCALE)
    return {a: 1 - sum(d) / len(d) for a, d in diffs.items()}


def discrimination_scores(ratings):
    by = {}
    for it, cell in ratings.items():
        tot, n = sum(cell.values()), len(cell)
        for a, v in cell.items():
            loo = (tot - v) / (n - 1)
            by.setdefault(a, []).append((v, loo))
    out = {}
    for a, pairs in by.items():
        xs = [p[0] for p in pairs]
        ys = [p[1] for p in pairs]
        out[a] = pearson(xs, ys)
    return out


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx and dy else 0.0


def rank(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0
        i = j + 1
    return r


def spearman(xs, ys):
    return pearson(rank(xs), rank(ys))


def pctile(v, pop):
    return sum(1 for x in pop if x < v) / len(pop)


def score_all(items, raters):
    ratings, predictions = simulate(items, raters)
    skill = {r["id"]: r["skill"] for r in raters}
    tier = {r["id"]: r["tier"] for r in raters}
    btsres = bts.score(ratings, predictions)
    methods = {
        "alignment": align_scores(ratings),
        "discrimination": discrimination_scores(ratings),
        "bts_full": {a: d["bts"] for a, d in btsres.items()},
    }
    ids = [r["id"] for r in raters]
    summ = {}
    for name, sc in methods.items():
        common = [i for i in ids if i in sc]
        sp = spearman([skill[i] for i in common], [sc[i] for i in common])
        vals = [sc[i] for i in common]
        exp_p = stats.mean([pctile(sc[i], vals) for i in common if tier[i] == "expert"])
        summ[name] = (sp, exp_p)
    return summ


def sweep():
    print("\nStress test — vary the share of ranking-disagreement (underrated-gem) items,\n"
          "the case where the crowd's ORDERING is wrong. n_normal=40, n_fallacy=12 fixed.\n")
    print(f"{'n_gem':>6} | {'alignment':>18} | {'discrimination':>18} | {'bts_full':>18}")
    print(f"{'':>6} | {'spearman  exp_pct':>18} | {'spearman  exp_pct':>18} | {'spearman  exp_pct':>18}")
    for n_gem in (0, 12, 30, 60, 100):
        RNG.seed(20260709 + n_gem)          # reproducible per sweep point
        items = make_world(n_normal=40, n_fallacy=12, n_gem=n_gem)
        raters = make_raters()
        s = score_all(items, raters)
        def cell(m):
            sp, ep = s[m]; return f"{sp:+.2f}     {ep:.2f}"
        print(f"{n_gem:>6} | {cell('alignment'):>18} | {cell('discrimination'):>18} | {cell('bts_full'):>18}")


def make_raters_uniform_fooled():
    """The decisive regime: NO careful crowd. Every non-expert is low-skill and
    fooled the SAME way, so the aggregate ordering itself is wrong and only the 8
    experts track truth. This is where a wisdom-of-crowds estimator (and thus
    discrimination) must fail, and only a mechanism using the prediction
    asymmetry (BTS) can still find the experts."""
    raters = []
    for i in range(8):
        raters.append({"id": f"s{i:02d}-exp", "tier": "expert", "skill": RNG.uniform(0.90, 0.99)})
    for i in range(52):
        raters.append({"id": f"h{i:02d}-fooled", "tier": "crowd", "skill": RNG.uniform(0.10, 0.30)})
    return raters


def decisive_test():
    print("\n" + "=" * 72)
    print("DECISIVE TEST — uniformly-fooled crowd (no careful raters), inverted-heavy.")
    print("Here the aggregate crowd ordering is WRONG; only the 8 experts track truth.")
    print("=" * 72)
    RNG.seed(424242)
    items = make_world(n_normal=20, n_fallacy=0, n_gem=60)   # ordering-inversion dominates
    raters = make_raters_uniform_fooled()
    s = score_all(items, raters)
    print(f"\n{'method':<16} {'spearman_vs_skill':>18} {'expert_mean_pctile':>19}")
    for m in ("alignment", "discrimination", "bts_full"):
        sp, ep = s[m]
        verdict = "experts on top" if ep > 0.6 else ("MIXED" if ep > 0.4 else "experts BURIED")
        print(f"{m:<16} {sp:>18.3f} {ep:>19.3f}   {verdict}")
    print("\n-> If discrimination buries the experts here but BTS keeps them on top,")
    print("   that is the case BTS uniquely solves: a correct minority the whole crowd rejects.")


def main():
    RNG.seed(20260709)
    items = make_world()
    raters = make_raters()
    ratings, predictions = simulate(items, raters)
    skill = {r["id"]: r["skill"] for r in raters}
    tier = {r["id"]: r["tier"] for r in raters}

    btsres = bts.score(ratings, predictions)
    methods = {
        "alignment": align_scores(ratings),
        "discrimination": discrimination_scores(ratings),
        "bts_info_only": {a: d["info"] for a, d in btsres.items()},
        "bts_full": {a: d["bts"] for a, d in btsres.items()},
    }

    ids = [r["id"] for r in raters]
    print(f"synthetic world: {len(items)} items "
          f"({sum(1 for i in items if i['kind']=='fallacy')} fallacy, "
          f"{sum(1 for i in items if i['kind']=='gem')} underrated-gem), "
          f"{len(raters)} raters (8 expert)\n")
    print(f"{'method':<16} {'spearman_vs_skill':>18} {'expert_mean_pctile':>19}")
    for name, sc in methods.items():
        common = [i for i in ids if i in sc]
        sp = spearman([skill[i] for i in common], [sc[i] for i in common])
        vals = [sc[i] for i in common]
        exp_p = stats.mean([pctile(sc[i], vals) for i in common if tier[i] == "expert"])
        print(f"{name:<16} {sp:>18.3f} {exp_p:>19.3f}")

    # --- the money test: underrated-gem items (ranking-disagreement) ---
    gem_ids = [it["id"] for it in items if it["kind"] == "gem"]
    print("\nUnderrated-gem items (crowd ranks LOW, experts rank HIGH — discrimination must fail here):")
    # per-item, mean expert vs crowd contribution under each lens
    # alignment distance (lower=better) and bts info (higher=better)
    exp_align_d, crowd_align_d, exp_info, crowd_info = [], [], [], []
    for gid in gem_ids:
        cell = ratings[gid]
        m = stats.mean(cell.values())
        # per-item bts info for this single item
        single = bts.score({gid: cell}, {gid: predictions[gid]}, min_raters=3)
        for a, v in cell.items():
            d = abs(v - m) / SCALE
            info = single.get(a, {}).get("info", 0.0)
            if tier[a] == "expert":
                exp_align_d.append(d); exp_info.append(info)
            else:
                crowd_align_d.append(d); crowd_info.append(info)
    print(f"  alignment distance (lower is better):  expert {stats.mean(exp_align_d):.3f}  "
          f"crowd {stats.mean(crowd_align_d):.3f}   -> experts look {'WORSE' if stats.mean(exp_align_d)>stats.mean(crowd_align_d) else 'better'}")
    print(f"  BTS info (higher is better):           expert {stats.mean(exp_info):+.3f}  "
          f"crowd {stats.mean(crowd_info):+.3f}   -> experts look {'BETTER' if stats.mean(exp_info)>stats.mean(crowd_info) else 'worse'}")

    # aggregate discrimination gem-only: corr of each rater's gem ratings w/ crowd gem-mean
    print("\nInterpretation: spearman ~+1 recovers skill; expert_pctile ~0.9 = experts on top.")
    sweep()
    decisive_test()


if __name__ == "__main__":
    main()
