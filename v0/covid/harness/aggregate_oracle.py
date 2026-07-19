#!/usr/bin/env python3
"""Aggregate the cross-model oracle panel into anchors.json.

Reads covid/oracle_raw.json (the panel workflow result: a list of
{panelist, scores:[{node,score}], ...}) and produces covid/anchors.json:

  - per-node oracle mean / sd / spread across the 4 panelists
  - the CALIBRATION ANCHOR set: nodes classified as anchor facts (targets.json)
    whose panel agreement is tight (sd <= TIGHT). A fact with wide oracle spread
    is a weak anchor and is flagged (reported, not silently used).
  - the reference VERDICT: oracle mean on the two top answers (n001 zoonosis,
    n002 lab-leak). Because the top question is genuinely unresolved, this is the
    baseline the adversarial run must not let collapse into false certainty.
"""
import json
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
COVID = HERE.parent
TIGHT = 0.75  # max panel sd (on 0-5) for a fact to count as a firm calibration anchor


def main():
    raw = json.loads((COVID / "oracle_raw.json").read_text())
    tgt = json.loads((HERE / "targets.json").read_text())
    cls = {}
    for k in ("anchors", "cruxes", "verdict", "meta"):
        for nid in tgt[k]:
            cls[nid] = k

    # collect per-node scores across panelists
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
    (COVID / "anchors.json").write_text(json.dumps(out, indent=2) + "\n")

    print(f"panelists: {panelists}")
    print(f"firm calibration anchors ({len(firm)}/{len(anchor_facts)}): {firm}")
    if weak:
        print(f"WEAK anchor facts (oracle sd > {TIGHT}, flagged not dropped): "
              + ", ".join(f"{n}(sd={nodes[n]['oracle_sd']})" for n in weak))
    print(f"reference verdict  n001 zoonosis={verdict.get('n001')}  n002 lab-leak={verdict.get('n002')}")
    # crux spread summary (are the contested cruxes really near-midpoint / disputed?)
    cruxes = [(n, nodes[n]["oracle_mean"], nodes[n]["oracle_sd"]) for n in tgt["cruxes"] if n in nodes]
    print("crux oracle means (should straddle the midpoint, both camps represented):")
    for n, m, sd in sorted(cruxes, key=lambda x: x[1]):
        print(f"   {n}: mean={m} sd={sd}")


if __name__ == "__main__":
    main()
