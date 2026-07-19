#!/usr/bin/env python3
"""Seed eggs-p9 from the shared eggs scaffold (p6 events minus ratings), write
the enforced-blind config, and generate the saturated assignment (every agent
rates all 79 nodes, dim A). Run once after gen_roster_personas.py, before the
workflow. Mirrors setup_p7.py.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
HERE = Path(__file__).resolve().parent
P9 = ROOT / "eggs-p9"


def seed_scaffold():
    src = (ROOT / "eggs-p6/events.jsonl").read_text().splitlines()
    kept, seq = [], 0
    for line in src:
        if not line.strip():
            continue
        e = json.loads(line)
        if e["verb"] == "rate":
            continue
        seq += 1
        e["seq"] = seq
        kept.append(json.dumps(e))
    (P9 / "events.jsonl").write_text("\n".join(kept) + "\n")
    cfg = json.loads((ROOT / "eggs-p6/config.json").read_text())
    cfg = {"rating_mode_only": True, **cfg}   # enforced blind Rating mode
    (P9 / "config.json").write_text(json.dumps(cfg, indent=2) + "\n")
    return len(kept)


def gen_assignment():
    roster = json.loads((HERE / "roster.json").read_text())
    nodes = [json.loads(l)["payload"]["id"]
             for l in (P9 / "events.jsonl").read_text().splitlines()
             if json.loads(l)["verb"] == "create_node"]
    adir = HERE / "assign"
    adir.mkdir(exist_ok=True)
    for a in roster["agents"]:
        (adir / f"{a['id']}.tsv").write_text("\n".join(f"{nid}\tA\tb1" for nid in nodes) + "\n")
    return len(roster["agents"]), len(nodes)


if __name__ == "__main__":
    ns = seed_scaffold()
    na, nn = gen_assignment()
    print(f"seeded eggs-p9: {ns} scaffold events; enforced blind; assignment {na} agents x {nn} nodes")
