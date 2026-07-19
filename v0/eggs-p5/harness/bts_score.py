#!/usr/bin/env python3
"""Score the eggs-p5 run: does BTS lift the experts where alignment buried them?

Reads the fresh ratings (events.jsonl) + the sidecar meta-predictions
(predictions.jsonl), scores every rater under alignment, discrimination, and BTS,
and compares each to the hidden competence labels (tier/care). Headline: the
expert panel's percentile under alignment (the live rule, ~0.10 in eggs-p4) vs
under BTS.
"""
import json
import math
import statistics as stats
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
V0 = HERE.parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(V0))
import bts  # noqa: E402
from reasonable import store, fold  # noqa: E402

SCALE = 5.0


def load_ratings(data_dir):
    st = fold.fold(store.read_events(str(data_dir)))
    items = {}
    for target, dmap in st["ratings"].items():
        for dim, amap in dmap.items():
            cell = {a: v for a, v in amap.items() if v != "abstain"}
            if cell:
                items[(target, dim)] = cell
    return items


def load_predictions(data_dir):
    path = Path(data_dir) / "predictions.jsonl"
    preds = {}
    if not path.exists():
        return preds
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        r = json.loads(line)
        key = (r["target"], r["dim"])
        preds.setdefault(key, {})[r["agent"]] = r["pred"]   # last write wins
    return preds


def align_scores(items):
    diffs = {}
    for it, cell in items.items():
        if len(cell) < 2:
            continue
        m = stats.mean(cell.values())
        for a, v in cell.items():
            diffs.setdefault(a, []).append(abs(v - m) / SCALE)
    return {a: 1 - sum(d) / len(d) for a, d in diffs.items()}


def discrimination_scores(items):
    by = {}
    for it, cell in items.items():
        if len(cell) < 4:
            continue
        tot, n = sum(cell.values()), len(cell)
        for a, v in cell.items():
            by.setdefault(a, []).append((v, (tot - v) / (n - 1)))
    out = {}
    for a, pairs in by.items():
        if len(pairs) < 5:
            continue
        out[a] = pearson([p[0] for p in pairs], [p[1] for p in pairs])
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


def main():
    data_dir = V0 / "eggs-p5"
    roster = json.loads((HERE / "roster.json").read_text())
    tier = {a["id"]: a["tier"] for a in roster["agents"]}
    care_rank = {a["id"]: (3 if a["tier"] == "expert"
                           else {"high": 2, "mid": 1, "hasty": 0}[a["care"]])
                 for a in roster["agents"]}
    run_ids = set(tier)

    items = load_ratings(data_dir)
    preds = load_predictions(data_dir)
    btsres = bts.score(items, preds)

    methods = {
        "alignment": align_scores(items),
        "discrimination": discrimination_scores(items),
        "bts_info": {a: d["info"] for a, d in btsres.items()},
        "bts_full": {a: d["bts"] for a, d in btsres.items()},
    }

    # coverage
    n_rating_cells = sum(len(c) for c in items.values())
    n_pred_cells = sum(len(c) for c in preds.values())
    report = {"items_rated": len(items), "rating_cells": n_rating_cells,
              "prediction_cells": n_pred_cells, "methods": {}}

    print(f"eggs-p5 — {len(items)} rated (target,dim) items, {n_rating_cells} ratings, "
          f"{n_pred_cells} predictions\n")
    print(f"{'method':<16} {'exp_pctile':>11} {'crowd_pctile':>13} {'spearman_vs_competence':>23}")
    for name, sc in methods.items():
        pop = {a: sc[a] for a in run_ids if a in sc}
        if not pop:
            continue
        vals = list(pop.values())
        exp = [pctile(pop[a], vals) for a in pop if tier[a] == "expert"]
        crd = [pctile(pop[a], vals) for a in pop if tier[a] == "crowd"]
        sp = spearman([care_rank[a] for a in pop], [pop[a] for a in pop])
        exp_p = round(stats.mean(exp), 3) if exp else None
        crd_p = round(stats.mean(crd), 3) if crd else None
        report["methods"][name] = {"expert_pctile": exp_p, "crowd_pctile": crd_p,
                                    "spearman_vs_competence": round(sp, 3),
                                    "n_scored": len(pop)}
        print(f"{name:<16} {str(exp_p):>11} {str(crd_p):>13} {str(round(sp,3)):>23}")

    # does the prediction asymmetry BTS needs actually hold?
    # measure: mean prediction accuracy (neg-KL) for experts vs crowd
    acc = {"expert": [], "crowd": []}
    for (t, d), cell in items.items():
        if len(cell) < bts.DEFAULT_BINS.__len__() + 2:
            pass
        B = bts.n_bins()
        counts = [0.0] * B
        for a, v in cell.items():
            counts[bts.bin_of(v)] += 1
        s = sum(counts) or 1
        x = [c / s for c in counts]
        for a, pv in preds.get((t, d), {}).items():
            if a not in tier:
                continue
            pvn = [max(z, 1e-6) for z in pv]
            ss = sum(pvn); pvn = [z / ss for z in pvn]
            negkl = sum(x[j] * math.log((pvn[j] + 1e-6) / (x[j] + 1e-6)) for j in range(B))
            acc[tier[a]].append(negkl)
    report["prediction_accuracy_negKL"] = {
        "expert": round(stats.mean(acc["expert"]), 4) if acc["expert"] else None,
        "crowd": round(stats.mean(acc["crowd"]), 4) if acc["crowd"] else None,
    }
    pa = report["prediction_accuracy_negKL"]
    print(f"\nPrediction accuracy (-KL, higher=better crowd-modeling): "
          f"expert {pa['expert']}  crowd {pa['crowd']}  -> "
          f"{'experts predict the crowd BETTER (BTS asymmetry holds)' if (pa['expert'] or -9) > (pa['crowd'] or 9) else 'asymmetry does NOT hold'}")

    (HERE / "bts_score.json").write_text(json.dumps(report, indent=2))
    print("\nCompare expert_pctile: alignment (the live rule) vs bts_full is the headline.")


if __name__ == "__main__":
    main()
