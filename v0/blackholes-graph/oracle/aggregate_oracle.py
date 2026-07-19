#!/usr/bin/env python3
"""Aggregate the cross-model oracle panel into blackholes-graph/anchors.json.

Reads blackholes-graph/oracle/oracle_raw.json (the panel result: a list of
{panelist, scores:[{node,score}], ...}) and oracle/targets.json, and produces
blackholes-graph/anchors.json in the same schema as covid/anchors.json:

  - per-node oracle mean / sd / spread across the panelists
  - CALIBRATION ANCHOR set: anchor-class nodes whose panel agreement is tight
    (sd <= TIGHT). A fact with wide oracle spread is a weak anchor -> flagged.
  - reference VERDICT: oracle mean on the two top answers (n001 safe, n002 catastrophe).
"""
import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent          # blackholes-graph/oracle
BH = HERE.parent                                # blackholes-graph
TIGHT = 0.75  # max panel sd (on 0-5) for a fact to count as a firm calibration anchor


def main():
    raw = json.loads((HERE / "oracle_raw.json").read_text())
    tgt = json.loads((HERE / "targets.json").read_text())
    cls = {}
    for k in ("anchors", "cruxes", "verdict", "meta"):
        for nid in tgt.get(k, []):
            cls[nid] = k

    by_node = {}
    panelists = []
    for p in raw:
        panelists.append(p["panelist"])
        for s in p["scores"]:
            by_node.setdefault(s["node"], {})[p["panelist"]] = s["score"]

    nodes = {}
    for nid, d in by_node.items():
        vals = list(d.values())
        nodes[nid] = {
            "class": cls.get(nid, "?"),
            "oracle_mean": round(st.mean(vals), 3),
            "oracle_sd": round(st.pstdev(vals), 3) if len(vals) > 1 else 0.0,
            "spread": round(max(vals) - min(vals), 3),
            "panel": d,
        }

    anchor_facts = tgt["anchors"]
    firm = [n for n in anchor_facts if nodes.get(n, {}).get("oracle_sd", 9) <= TIGHT]
    weak = [n for n in anchor_facts if n not in firm]
    verdict = {n: nodes[n]["oracle_mean"] for n in tgt["verdict"] if n in nodes}

    out = {
        "panelists": panelists,
        "tight_threshold": TIGHT,
        "calibration_anchors": firm,
        "weak_anchor_facts": weak,
        "reference_verdict": verdict,
        "nodes": nodes,
    }
    (BH / "anchors.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"panelists: {panelists}")
    print(f"firm calibration anchors ({len(firm)}/{len(anchor_facts)}): {firm}")
    if weak:
        print(f"WEAK anchor facts (oracle sd > {TIGHT}, flagged not dropped): "
              + ", ".join(f"{n}(sd={nodes[n]['oracle_sd']})" for n in weak))
    print(f"reference verdict  n001 safe={verdict.get('n001')}  n002 catastrophe={verdict.get('n002')}")
    cruxes = [(n, nodes[n]["oracle_mean"], nodes[n]["oracle_sd"]) for n in tgt["cruxes"] if n in nodes]
    print("crux oracle means (should straddle the midpoint):")
    for n, m, sd in sorted(cruxes, key=lambda x: x[1]):
        print(f"   {n}: mean={m} sd={sd}")


if __name__ == "__main__":
    main()
