#!/usr/bin/env python3
"""Snapshot the eggs-p4 run after a round: the headline question is whether the
Sonnet experts RISE (rewarded for sharper judgment) or stay PENALIZED (blunter-
majority consensus pulls them below the crowd, as in eggs-p3).

Writes snapshots/r{N}.json (machine) + snapshots/r{N}.md (human). Reads the
reputation accounts via the package and the graph.json for states/depths.
"""
import argparse
import json
import statistics as stats
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
V0 = HERE.parent.parent          # .../v0
sys.path.insert(0, str(V0))
from reasonable import queries   # noqa: E402


def pct_rank(value, population):
    """Fraction of the population strictly below `value` (0..1)."""
    if not population:
        return None
    below = sum(1 for x in population if x < value)
    return round(below / len(population), 3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--roster", default=str(HERE / "roster.json"))
    args = ap.parse_args()

    data_dir = Path(args.data).resolve()
    graph = queries.load_graph(str(data_dir))
    roster = json.loads(Path(args.roster).read_text())
    model_of = {a["id"]: a["model"] for a in roster["agents"]}
    tier_of = {a["id"]: a["tier"] for a in roster["agents"]}
    lens_of = {a["id"]: a.get("lens") for a in roster["agents"]}

    accounts = queries.reputation(graph)
    # only accounts that belong to THIS run's roster (ignore legacy p3 raters)
    run_accts = [a for a in accounts if a["agent"] in model_of]
    for a in run_accts:
        a["model"] = model_of[a["agent"]]
        a["tier"] = tier_of[a["agent"]]

    all_true = [a["true_r"] for a in run_accts]
    experts = [a for a in run_accts if a["tier"] == "expert"]
    crowd = [a for a in run_accts if a["tier"] == "crowd"]

    def summarize(group):
        if not group:
            return None
        tr = [a["true_r"] for a in group]
        rr = [a["raw_r"] for a in group]
        return {
            "n": len(group),
            "mean_true_r": round(stats.mean(tr), 4),
            "median_true_r": round(stats.median(tr), 4),
            "mean_raw_r": round(stats.mean(rr), 4),
            "mean_conf": round(stats.mean([a["confidence"] for a in group]), 3),
            "mean_n_assessments": round(stats.mean([a["n_assessments"] for a in group]), 1),
        }

    # expert rank: where does each expert sit in the whole run population?
    expert_ranks = sorted(
        [{"agent": a["agent"], "true_r": round(a["true_r"], 4),
          "raw_r": round(a["raw_r"], 4),
          "pctile": pct_rank(a["true_r"], all_true)} for a in experts],
        key=lambda x: -x["true_r"])

    # leaderboard extremes
    ranked = sorted(run_accts, key=lambda a: -a["true_r"])
    top = [{"agent": a["agent"], "tier": a["tier"], "true_r": round(a["true_r"], 4)} for a in ranked[:8]]
    bottom = [{"agent": a["agent"], "tier": a["tier"], "true_r": round(a["true_r"], 4)} for a in ranked[-8:]]

    # coverage + lifecycle states over rateable A-items (nodes, ungrouped edges, groups)
    node_states = Counter(n["agreement"]["state"] for n in graph["nodes"])
    edge_states = Counter(e["agreement"]["state"] for e in graph["ground_edges"])
    depths = ([n["agreement"]["n"] for n in graph["nodes"]]
              + [e["agreement"]["n"] for e in graph["ground_edges"]])
    depths_sorted = sorted(depths)
    contested = [
        {"id": n["id"], "mean": round(n["agreement"]["mean"], 2),
         "stdev": round(n["agreement"].get("stdev") or 0, 2), "n": n["agreement"]["n"]}
        for n in graph["nodes"] if n["agreement"]["state"] == "contested"]

    out = {
        "round": args.round,
        "graph": {"nodes": len(graph["nodes"]), "edges": len(graph["ground_edges"]),
                  "groups": len(graph.get("conjunction_groups", [])),
                  "events": graph.get("meta", {}).get("event_count")},
        "population": {"in_run": len(run_accts),
                       "with_ratings": sum(1 for a in run_accts if a["n_assessments"] > 0)},
        "HEADLINE_expert_vs_crowd": {
            "expert": summarize(experts), "crowd": summarize(crowd),
            "expert_minus_crowd_true_r": (
                round(summarize(experts)["mean_true_r"] - summarize(crowd)["mean_true_r"], 4)
                if experts and crowd else None),
            "verdict": None},
        "expert_ranks": expert_ranks,
        "true_r_variance": {
            "stdev": round(stats.pstdev(all_true), 4) if len(all_true) > 1 else 0,
            "min": round(min(all_true), 4) if all_true else None,
            "max": round(max(all_true), 4) if all_true else None},
        "leaderboard": {"top8": top, "bottom8": bottom},
        "coverage": {
            "rateable_A_items": len(depths),
            "depth_min": depths_sorted[0] if depths else 0,
            "depth_median": depths_sorted[len(depths_sorted) // 2] if depths else 0,
            "depth_mean": round(stats.mean(depths), 1) if depths else 0,
            "items_ge_15": sum(1 for d in depths if d >= 15)},
        "lifecycle": {"nodes": dict(node_states), "edges": dict(edge_states)},
        "contested_nodes": contested,
    }
    h = out["HEADLINE_expert_vs_crowd"]
    if h["expert_minus_crowd_true_r"] is not None:
        h["verdict"] = ("experts REWARDED (above crowd)" if h["expert_minus_crowd_true_r"] > 0
                        else "experts PENALIZED (below crowd)")

    snapdir = HERE / "snapshots"
    snapdir.mkdir(exist_ok=True)
    (snapdir / f"r{args.round}.json").write_text(json.dumps(out, indent=2))

    # human summary
    e, c = summarize(experts), summarize(crowd)
    md = [f"# eggs-p4 snapshot — round {args.round}", "",
          f"Graph: {out['graph']['nodes']} nodes, {out['graph']['edges']} edges, "
          f"{out['graph']['groups']} groups, {out['graph']['events']} events.",
          f"Coverage: {out['coverage']['rateable_A_items']} A-items, median depth "
          f"{out['coverage']['depth_median']}, {out['coverage']['items_ge_15']} items ≥15 ratings.", "",
          "## HEADLINE — do experts rise?",
          f"- Expert mean True_R: **{e['mean_true_r'] if e else 'n/a'}** (raw_r {e['mean_raw_r'] if e else 'n/a'})",
          f"- Crowd  mean True_R: **{c['mean_true_r'] if c else 'n/a'}** (raw_r {c['mean_raw_r'] if c else 'n/a'})",
          f"- Expert − crowd: **{h['expert_minus_crowd_true_r']}** → {h['verdict']}", "",
          "## Expert ranks (percentile in full population)"]
    for er in expert_ranks:
        md.append(f"- {er['agent']}: True_R {er['true_r']}, pctile {er['pctile']}")
    md += ["", f"True_R spread: stdev {out['true_r_variance']['stdev']}, "
           f"range {out['true_r_variance']['min']}–{out['true_r_variance']['max']}",
           f"Contested nodes: {len(contested)} — " + ", ".join(f"{x['id']}({x['mean']})" for x in contested)]
    (snapdir / f"r{args.round}.md").write_text("\n".join(md))

    print(json.dumps({"round": args.round,
                      "expert_mean_true_r": e["mean_true_r"] if e else None,
                      "crowd_mean_true_r": c["mean_true_r"] if c else None,
                      "expert_minus_crowd": h["expert_minus_crowd_true_r"],
                      "verdict": h["verdict"],
                      "depth_median": out["coverage"]["depth_median"],
                      "items_ge_15": out["coverage"]["items_ge_15"],
                      "nodes": out["graph"]["nodes"], "events": out["graph"]["events"]}, indent=2))


if __name__ == "__main__":
    main()
