#!/usr/bin/env python3
"""Report-vs-graph comparison signals for the covid-graph.

Reads the assessed graph and the recovered deep-research baseline and prints the
quantitative signals the COMPARISON.md write-up cites: the two answers' panel
Agreement, strongest support-chain product to each, the most-contested nodes
(dispersion), the weakest inferential links (edge support), and the cross-check
of the report's refuted claims against how the graph represents them.

Stdlib + the reasonable package only; re-derivable from the committed graph.
"""
import json, sys, statistics as st
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
from reasonable import queries, chain as C  # noqa

g = queries.load_graph(ROOT / "covid-graph")
byid = {n["id"]: n for n in g["nodes"]}


def txt(n):
    return next((p["text"] for p in n["phrasings"] if p["id"] == n["primary_phrasing"]),
                n["phrasings"][0]["text"])


def rule(t):
    print("\n" + "=" * 3, t)


rule("THE TWO ANSWERS (panel Agreement, 0-5)")
for a in ("n001", "n002"):
    ag = byid[a]["agreement"]
    print(f"  {a}: mean {ag['mean']:.2f}  sd {ag['stdev']:.2f}  (n={ag['n']})  {txt(byid[a])[:70]}")

rule("STRONGEST SUPPORT CHAIN TO EACH ANSWER (chain-rule product of node_A/5 x edge_A/5)")
for ans in ("n001", "n002"):
    best = None
    for r in g["nodes"]:
        if r["id"] == ans:
            continue
        res = C.compute(g, r["id"], ans, max_paths=4)
        if res["ok"]:
            for p in res["paths"]:
                if best is None or p["product"] > best["product"]:
                    best = p
    if best:
        print(f"  {ans}: product={best['product']:.4f}  via {' -> '.join(best['nodes'])}  "
              f"(weakest link {best['weakest_link']['id']} @ {best['weakest_link']['factor']:.2f})")

rule("MOST-CONTESTED NODES (highest panel dispersion = the genuine cruxes)")
rated = [(n, n["agreement"]) for n in g["nodes"] if n["agreement"]["stdev"] is not None]
for n, a in sorted(rated, key=lambda x: -x[1]["stdev"])[:8]:
    kind = "ANCHOR" if n.get("source_ref") else "reason"
    print(f"  sd {a['stdev']:.2f}  mean {a['mean']:.2f}  [{kind}]  {n['id']}: {txt(n)[:66]}")

rule("STRONGEST SHARED GROUND (high mean, low dispersion = facts both camps accept)")
for n, a in sorted([x for x in rated if x[1]["mean"] >= 4.5 and x[1]["stdev"] < 0.3],
                   key=lambda x: -x[1]["mean"])[:6]:
    print(f"  mean {a['mean']:.2f}  sd {a['stdev']:.2f}  {n['id']}: {txt(n)[:66]}")

rule("WEAKEST INFERENTIAL LINKS (lowest edge support = where the reasoning is thin)")
es = sorted([e for e in g["ground_edges"] if e["agreement"]["mean"] is not None],
            key=lambda e: e["agreement"]["mean"])
for e in es[:7]:
    print(f"  {e['agreement']['mean']:.2f}  {e['from']}->{e['to']}: "
          f"[{txt(byid[e['from']])[:34]}] => [{txt(byid[e['to']])[:34]}]")

rule("CROSS-CHECK: how the graph treats the claims the flat report's verifier REFUTED")
recovered = json.loads((HERE / "recovered" / "verified_claims.json").read_text())
refuted = [v for v in recovered if v["status"] == "refuted"]
# crude text-overlap match of each refuted report-claim to a graph node
import re
def toks(s): return set(re.findall(r"[a-z]{4,}", s.lower()))
for v in refuted:
    vt = toks(v["claim"])
    best = max(g["nodes"], key=lambda n: len(vt & toks(txt(n))))
    ov = len(vt & toks(txt(best)))
    ag = best["agreement"]
    tag = f"node {best['id']} mean {ag['mean']:.2f} sd {ag['stdev']:.2f}" if ov >= 6 else "no close node match"
    print(f"  report verdict {v['votes']} REFUTED -> graph: {tag}")
    print(f"      \"{v['claim'][:88]}\"")
