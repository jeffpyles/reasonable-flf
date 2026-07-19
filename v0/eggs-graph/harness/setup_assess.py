#!/usr/bin/env python3
"""Stage-1.5 setup for the eggs-graph panel assessment.

Run AFTER the build workflow completes. Flips the dataset to enforced blind
Rating mode and writes one assignment file per panelist covering EVERY rateable
target: nodes, ground edges, and conjunction groups (all on dim A, bloc b1).

Assignment line format: <target>\tA\t<bloc>
  - node:  nNNN
  - edge:  eNNN
  - group: group:gNNN
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent          # v0/
DATA = ROOT / "eggs-graph"
BLOC = "b1"


def flip_rating_mode():
    cfg_path = DATA / "config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["rating_mode_only"] = True
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n")
    return cfg["rating_mode_only"]


def targets():
    g = json.loads((DATA / "graph.json").read_text())
    ts = [n["id"] for n in g["nodes"]]
    ts += [e["id"] for e in g["ground_edges"]]
    ts += [f"group:{gr['id']}" for gr in g["conjunction_groups"]]
    return ts


def main():
    panel = json.loads((HERE / "roster.json").read_text())["assess_panel"]
    ts = targets()
    adir = HERE / "assign"
    adir.mkdir(exist_ok=True)
    for a in panel:
        lines = [f"{t}\tA\t{BLOC}" for t in ts]
        (adir / f"{a['id']}.tsv").write_text("\n".join(lines) + "\n")
    rm = flip_rating_mode()
    n_nodes = sum(1 for t in ts if t.startswith("n"))
    n_edges = sum(1 for t in ts if t.startswith("e"))
    n_groups = sum(1 for t in ts if t.startswith("group:"))
    print(f"rating_mode_only={rm}; {len(ts)} targets "
          f"({n_nodes} nodes, {n_edges} edges, {n_groups} groups) x {len(panel)} panelists")


if __name__ == "__main__":
    main()
