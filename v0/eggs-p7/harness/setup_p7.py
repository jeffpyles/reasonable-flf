#!/usr/bin/env python3
"""Seed eggs-p7 from the shared eggs graph scaffold, then generate the saturated
assignment (every agent rates all 79 nodes on dim A). Run once before the agent
workflow.

The scaffold (79 nodes + edges + antitheses + comments, NO ratings) is copied
from eggs-p6's event log — the structural events are identical graph content and
carry stable node ids that the eggs-p5 expert oracle is keyed to. Only the
`rate` events are dropped, giving a clean graph for the p7 raters to rate fresh.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
HERE = Path(__file__).resolve().parent
P7 = ROOT / "eggs-p7"


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
    (P7 / "events.jsonl").write_text("\n".join(kept) + "\n")
    # config: p6's phase2 knobs + enforced blind Rating mode (ASSESSMENT-SPEC
    # §7 v1.5). rating_mode_only makes every rater-facing read verb blind with
    # no CLI opt-out, so blindness is imposed on the dataset rather than left to
    # each agent's flags -- the standing posture for all prototype build/rate runs.
    import json as _json
    cfg = _json.loads((ROOT / "eggs-p6/config.json").read_text())
    cfg = {"rating_mode_only": True, **cfg}
    (P7 / "config.json").write_text(_json.dumps(cfg, indent=2) + "\n")
    return len(kept)


def gen_assignment():
    roster = json.loads((HERE / "roster.json").read_text())
    nodes = [json.loads(l)["payload"]["id"]
             for l in (P7 / "events.jsonl").read_text().splitlines()
             if json.loads(l)["verb"] == "create_node"]
    adir = HERE / "assign"
    adir.mkdir(exist_ok=True)
    for a in roster["agents"]:
        rows = [f"{nid}\tA\tb1" for nid in nodes]
        (adir / f"{a['id']}.tsv").write_text("\n".join(rows) + "\n")
    return len(roster["agents"]), len(nodes)


if __name__ == "__main__":
    n_struct = seed_scaffold()
    n_agents, n_nodes = gen_assignment()
    print(f"seeded eggs-p7: {n_struct} scaffold events; "
          f"assignment for {n_agents} agents x {n_nodes} nodes (saturated)")
