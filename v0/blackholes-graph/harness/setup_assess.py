#!/usr/bin/env python3
"""Stage-1.5 setup for the blackholes-graph tiered assessment.

Run AFTER the build completes. Flips the dataset to enforced blind Rating mode and
writes one assignment file per rater (reference Sonnet arm + cheap Haiku arm),
covering every NODE (the tiering test's primary signal; edges are out of scope for
this comparison). Bloc = 'ref' for Sonnet, 'cheap' for Haiku so the two arms are
separable in the fold.

Assignment line: <nid>\tA\t<bloc>
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent          # v0/
DATA = ROOT / "blackholes-graph"


def flip_rating_mode():
    cfg_path = DATA / "config.json"
    cfg = json.loads(cfg_path.read_text())
    cfg["rating_mode_only"] = True
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n")
    return cfg["rating_mode_only"]


def node_ids():
    g = json.loads((DATA / "graph.json").read_text())
    return [n["id"] for n in g["nodes"]]


def main():
    roster = json.loads((HERE / "roster.json").read_text())
    raters = roster["assess_reference_sonnet"] + roster["assess_cheap_haiku"]
    nodes = node_ids()
    adir = HERE / "assign"
    adir.mkdir(exist_ok=True)
    for a in raters:
        bloc = "cheap" if a["model"] == "haiku" else "ref"
        lines = [f"{nid}\tA\t{bloc}" for nid in nodes]
        (adir / f"{a['id']}.tsv").write_text("\n".join(lines) + "\n")
    rm = flip_rating_mode()
    ns = sum(1 for a in raters if a["model"] == "sonnet")
    nh = sum(1 for a in raters if a["model"] == "haiku")
    print(f"rating_mode_only={rm}; {len(nodes)} nodes x {len(raters)} raters "
          f"({ns} sonnet ref, {nh} haiku cheap)")


if __name__ == "__main__":
    main()
