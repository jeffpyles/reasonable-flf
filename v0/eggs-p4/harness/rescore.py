#!/usr/bin/env python3
"""Re-score the FIXED eggs-p4 rating matrix under alternative reputation rules,
to test the FINDINGS.md hypothesis: alignment-to-consensus penalizes expertise;
a proper *information*-based score should not.

No new agent run. We read the frozen event log, build the rater x item matrix,
and score every rater three ways:

  1. ALIGN (baseline)  — the live system's rule: reward proximity to the
     (True_R-weighted) consensus mean. This is what put experts at the bottom.
  2. DS-RELIABILITY     — Dawid-Skene / Gaussian latent-truth with a per-rater
     additive BIAS and a per-rater PRECISION (reliability). Reward low
     idiosyncratic NOISE around each item's latent value, NOT agreement with the
     level: a rater may be systematically offset (bias absorbed) and still score
     high if they are consistent. Latent value is reliability-weighted, so
     reliable raters shape "truth" (a proper, information-rewarding rule).
  3. DISCRIMINATION     — how well a rater tracks item-to-item VARIATION
     (correlation with the leave-one-out item mean). Rewards using the scale to
     separate strong from weak items; a flat mid-clumper scores ~0.

Then the honest test: each score is compared against the HIDDEN competence
labels the mechanism never saw (expert/crowd tier, and care=high/mid/hasty) via
Spearman rank-correlation, plus the expert panel's mean percentile. A rule that
"finds reasonableness" should correlate POSITIVELY with hidden competence and
lift the expert panel off the bottom.
"""
import json
import math
import statistics as stats
from pathlib import Path

HERE = Path(__file__).resolve().parent
V0 = HERE.parent.parent
import sys
sys.path.insert(0, str(V0))
from reasonable import store, fold, queries  # noqa: E402

SCALE = 5.0


def build_matrix(data_dir):
    st = fold.fold(store.read_events(data_dir))
    # items[(target,dim)] = {agent: value}; only numeric (non-abstain)
    items = {}
    for target, dmap in st["ratings"].items():
        for dim, amap in dmap.items():
            cell = {a: v for a, v in amap.items() if v != "abstain"}
            if cell:
                items[(target, dim)] = cell
    return items


def align_scores(data_dir):
    """The live rule, isolated: 1 - mean|v - weighted_mean|/scale over an
    agent's ratings. Pull the True_R-weighted aggregate the system itself uses."""
    graph = queries.load_graph(str(data_dir))
    # reputation accounts already carry raw_r/true_r; but we want the pure
    # alignment term. Reconstruct from the aggregate means in the graph.
    # graph nodes/edges carry agreement.mean (True_R-weighted). Build a lookup.
    mean_of = {}
    for n in graph["nodes"]:
        a = n["agreement"]
        if a["n"]:
            mean_of[(n["id"], "A")] = a["mean"]
    for e in graph["ground_edges"]:
        a = e["agreement"]
        if a["n"]:
            mean_of[(e["id"], "A")] = a["mean"]
    # phrasing R/C and group A means live in the assess aggregate; recompute via assess
    from reasonable import assess
    st = fold.fold(store.read_events(data_dir))
    comp = assess.compute(st, queries.effective_config(data_dir).get("assessment"))
    agg = comp["aggregate"]  # (target,dim)->(mean,n)
    for (t, d), (m, n) in agg.items():
        if m is not None and n:
            mean_of[(t, d)] = m
    # per-agent alignment
    items = build_matrix(data_dir)
    diffs = {}
    for (t, d), cell in items.items():
        m = mean_of.get((t, d))
        if m is None or len(cell) < 2:
            continue
        for a, v in cell.items():
            diffs.setdefault(a, []).append(abs(v - m) / SCALE)
    return {a: 1.0 - sum(ds) / len(ds) for a, ds in diffs.items() if ds}, comp


def ds_reliability(items, iters=50, return_mu=False):
    """Gaussian Dawid-Skene: v[a,i] = mu[i] + bias[a] + N(0, 1/tau[a]).
    Returns (tau, bias, resid_sd[, mu]). Reliability-weighted latent value."""
    agents = sorted({a for cell in items.values() for a in cell})
    by_agent = {a: [] for a in agents}          # a -> [(item, v)]
    for it, cell in items.items():
        for a, v in cell.items():
            by_agent[a].append((it, v))
    # global variance for the Gamma prior (regularizes thin raters)
    allv = [v for cell in items.values() for v in cell.values()]
    gvar = stats.pvariance(allv) if len(allv) > 1 else 1.0
    a0, b0 = 2.0, 2.0 * gvar                    # prior mean precision ~ 1/gvar
    tau = {a: 1.0 / gvar for a in agents}
    bias = {a: 0.0 for a in agents}
    mu = {it: stats.mean(cell.values()) for it, cell in items.items()}
    for _ in range(iters):
        # E-step: reliability-weighted latent value (subtract each rater's bias)
        for it, cell in items.items():
            wsum = ssum = 0.0
            for a, v in cell.items():
                w = tau[a]
                wsum += w
                ssum += w * (v - bias[a])
            mu[it] = ssum / wsum if wsum else stats.mean(cell.values())
        # M-step: per-rater bias then precision from residual variance
        for a in agents:
            rs = by_agent[a]
            bias[a] = sum(v - mu[it] for it, v in rs) / len(rs)
            sse = sum((v - mu[it] - bias[a]) ** 2 for it, v in rs)
            n = len(rs)
            tau[a] = (n + 2 * a0) / (sse + 2 * b0)   # regularized precision
    resid_sd = {a: math.sqrt(1.0 / tau[a]) for a in agents}
    if return_mu:
        return tau, bias, resid_sd, mu
    return tau, bias, resid_sd


def align_debiased(items, mu, bias):
    """Bias-corrected alignment: 1 - mean_i |(v - bias_a) - mu_i|/scale. Isolates
    whether a rater's 'misalignment' is a calibratable CONSTANT offset (removed
    by bias_a) or genuine ITEM-SPECIFIC disagreement (survives). If experts rise
    here vs baseline align, their penalty was just a fixed offset."""
    diffs = {}
    for it, cell in items.items():
        if len(cell) < 2:
            continue
        for a, v in cell.items():
            diffs.setdefault(a, []).append(abs((v - bias[a]) - mu[it]) / SCALE)
    return {a: 1.0 - sum(ds) / len(ds) for a, ds in diffs.items() if ds}


def discrimination(items):
    """Pearson corr between a rater's values and the leave-one-out item mean,
    across items with >=3 other raters. Rewards tracking item-to-item signal."""
    by_agent = {}
    for it, cell in items.items():
        if len(cell) < 4:
            continue
        tot = sum(cell.values())
        n = len(cell)
        for a, v in cell.items():
            loo = (tot - v) / (n - 1)          # leave-one-out mean
            by_agent.setdefault(a, []).append((v, loo))
    out = {}
    for a, pairs in by_agent.items():
        if len(pairs) < 5:
            continue
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
    return num / (dx * dy) if dx > 0 and dy > 0 else 0.0


def spearman(pairs):
    """pairs: list of (score, label_rank). Spearman = Pearson on ranks."""
    if len(pairs) < 3:
        return None
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    return pearson(rank(xs), rank(ys))


def rank(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        avg = (i + j) / 2.0
        for k in range(i, j + 1):
            r[order[k]] = avg
        i = j + 1
    return r


def pct_rank(value, population):
    return round(sum(1 for x in population if x < value) / len(population), 3)


def main():
    data_dir = V0 / "eggs-p4"
    roster = json.loads((HERE / "roster.json").read_text())
    tier = {a["id"]: a["tier"] for a in roster["agents"]}
    care = {a["id"]: a.get("care") for a in roster["agents"]}
    # hidden competence rank: expert=3, high=2, mid=1, hasty=0
    care_rank = {a["id"]: (3 if a["tier"] == "expert" else {"high": 2, "mid": 1, "hasty": 0}[a["care"]])
                 for a in roster["agents"]}
    run_ids = set(tier)

    items = build_matrix(str(data_dir))
    align, comp = align_scores(str(data_dir))
    tau, bias, resid_sd, mu = ds_reliability(items, return_mu=True)
    disc = discrimination(items)
    align_db = align_debiased(items, mu, bias)

    true_r = {ac["agent"]: ac["true_r"] for ac in comp["accounts"]}

    methods = {
        "true_r (live)": true_r,
        "align (baseline)": align,
        "align_debiased": align_db,
        "ds_reliability": tau,
        "discrimination": disc,
    }

    report = {"n_items": len(items), "methods": {}}
    for name, sc in methods.items():
        # restrict to run agents present in this score
        pop = {a: sc[a] for a in run_ids if a in sc}
        vals = list(pop.values())
        experts = [v for a, v in pop.items() if tier[a] == "expert"]
        crowd = [v for a, v in pop.items() if tier[a] == "crowd"]
        # expert percentile within run population
        exp_pcts = [pct_rank(pop[a], vals) for a in pop if tier[a] == "expert"]
        sp = spearman([(pop[a], care_rank[a]) for a in pop])
        # leaderboard
        ranked = sorted(pop.items(), key=lambda kv: -kv[1])
        top = [(a, tier[a][:4], round(v, 3)) for a, v in ranked[:6]]
        bot = [(a, tier[a][:4], round(v, 3)) for a, v in ranked[-6:]]
        report["methods"][name] = {
            "expert_mean": round(stats.mean(experts), 4) if experts else None,
            "crowd_mean": round(stats.mean(crowd), 4) if crowd else None,
            "expert_minus_crowd": round(stats.mean(experts) - stats.mean(crowd), 4) if experts and crowd else None,
            "expert_median_pctile": round(stats.median(exp_pcts), 3) if exp_pcts else None,
            "spearman_vs_hidden_competence": round(sp, 3) if sp is not None else None,
            "n_scored": len(pop),
            "top6": top, "bottom6": bot,
        }

    (HERE / "rescore.json").write_text(json.dumps(report, indent=2))

    # human table
    print(f"eggs-p4 re-score — {report['n_items']} items, {len(run_ids)} run agents\n")
    print(f"{'method':<20} {'exp_mean':>9} {'crowd':>8} {'gap':>8} {'exp_pctile':>11} {'spearman_vs_care':>17}")
    for name, m in report["methods"].items():
        print(f"{name:<20} {str(m['expert_mean']):>9} {str(m['crowd_mean']):>8} "
              f"{str(m['expert_minus_crowd']):>8} {str(m['expert_median_pctile']):>11} "
              f"{str(m['spearman_vs_hidden_competence']):>17}")
    print("\nSpearman vs hidden competence: +1 = perfectly recovers care/expertise, 0 = blind, - = inverted.")
    print("expert_median_pctile: 0.10 = experts near bottom, 0.90 = experts near top.\n")
    for name, m in report["methods"].items():
        print(f"[{name}] top: {m['top6']}")
        print(f"[{name}] bottom: {m['bottom6']}\n")


if __name__ == "__main__":
    main()
