#!/usr/bin/env python3
"""Deterministic structural metrics for the elicitation experiment.

Compares three builds of the SAME debate question on structure-quality metrics:
  - v1 naive:   the original debate-graph (a Sonnet flow WITHOUT the harness)
  - harnessed:  elicit-harness/out-debate (Sonnet flow WITH the skeleton-first harness)
  - v2 hand:    debate-graph-v2 (hand-built target)

Agent-judged metrics (bundled-node rate, non-rival-set rate) come from the probe
workflow and are merged in by report.py. This file is the no-LLM half.

Run from v0/:  python3 elicit-harness/compare.py
"""
import json
import subprocess
from pathlib import Path

V0 = Path(__file__).resolve().parent.parent
GRAPHS = {
    "v1 naive":   "debate-graph",
    "harness v1": "elicit-harness/out-debate",
    "harness fix": "elicit-harness/out-debate-fix",
    "v2 hand":    "debate-graph-v2",
}


def lint(data):
    out = subprocess.run(["python3", "graph.py", "lint", "--data", data, "--json"],
                         cwd=V0, capture_output=True, text=True)
    return json.loads(out.stdout)


def metrics(data):
    g = json.loads((V0 / data / "graph.json").read_text())
    nodes = g["nodes"]
    edges = [e for e in g["ground_edges"] if not (e.get("demoted") or e.get("ghost_eligible"))]
    sets = [s for s in g["antithesis_sets"] if not s.get("demoted")]
    live_nodes = [n for n in nodes if not (n.get("demoted") or n.get("ghost_eligible"))]
    indeg = {}
    for e in edges:
        indeg[e["to"]] = indeg.get(e["to"], 0) + 1
    # roots = nodes that support nothing (out-degree 0)
    outdeg = {}
    for e in edges:
        outdeg[e["from"]] = outdeg.get(e["from"], 0) + 1
    roots = [n["id"] for n in live_nodes if outdeg.get(n["id"], 0) == 0]
    li = lint(data)
    return {
        "nodes": len(live_nodes),
        "edges": len(edges),
        "sets": len(sets),
        "max_indegree": max(indeg.values()) if indeg else 0,
        "hubs(>=8)": li["summary"]["hub_nodes"],
        "orphans": li["summary"]["orphan_nodes"],
        "question_shaped": li["summary"]["question_shaped_nodes"],
        "roots(out=0)": len(roots),
        "ought_nodes": sum(1 for n in live_nodes if n.get("kind") == "ought"),
        "median_title_words": _median(
            [len((n["titles"][0]["text"]).split()) for n in live_nodes if n.get("titles")]),
        "titled_pct": round(100 * sum(1 for n in live_nodes if n.get("titles")) / max(1, len(live_nodes))),
        "bundle_proxy_pct": round(100 * bundle_proxy_rate(data)[0] / max(1, len(live_nodes))),
    }


import re
# Deterministic, reproducible bundle proxy (noise-free, unlike the LLM probe).
# Crude but stable: flags a node whose text carries an explicit inference marker
# (", so ", "therefore", "because") or a mid-sentence clause-joining " and "/"; ".
# Undercounts subtle bundles and overcounts a few list-nodes, but it is IDENTICAL
# every run, so deltas between graphs are real rather than judge noise.
_INFER = re.compile(r",\s*so\s|\btherefore\b|\bbecause\b|;\s", re.I)
def _bundle_proxy(text):
    if _INFER.search(text):
        return True
    # a mid-sentence " and " joining two clauses (both sides have a verb-ish word)
    for m in re.finditer(r"\sand\s", text):
        before, after = text[:m.start()], text[m.end():]
        if len(before.split()) >= 4 and re.search(r"\b(is|are|was|were|has|have|does|do|can|will|would|"
                                                  r"cannot|meaningfully|reflects|shows|means|raises)\b", after):
            return True
    return False


def bundle_proxy_rate(data):
    g = json.loads((V0 / data / "graph.json").read_text())
    live = [n for n in g["nodes"] if not (n.get("demoted") or n.get("ghost_eligible"))]
    flagged = [n["id"] for n in live if _bundle_proxy(n["phrasings"][0]["text"])]
    return len(flagged), len(live)


def _median(xs):
    if not xs:
        return None
    xs = sorted(xs)
    n = len(xs)
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


if __name__ == "__main__":
    rows = {name: metrics(data) for name, data in GRAPHS.items()}
    keys = list(next(iter(rows.values())).keys())
    w = max(len(k) for k in keys) + 1
    header = f"{'metric':<{w}}" + "".join(f"{name:>14}" for name in rows)
    print(header)
    print("-" * len(header))
    for k in keys:
        print(f"{k:<{w}}" + "".join(f"{str(rows[n][k]):>14}" for n in rows))
    (Path(__file__).resolve().parent / "metrics-deterministic.json").write_text(
        json.dumps(rows, indent=2) + "\n")
    print("\nwrote metrics-deterministic.json")
