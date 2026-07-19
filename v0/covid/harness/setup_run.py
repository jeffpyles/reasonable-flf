#!/usr/bin/env python3
"""Stage-1.5 setup for the covid rating run: flip the dataset to enforced blind
Rating mode and write per-agent assignment files.

- Honest raters (hon-*): assigned ALL nodes, dim A, bloc b1, mark HONEST (rate from
  their own worldview — the mark is only meaningful for sleepers).
- Sleepers (slp-*): assigned ALL nodes, dim A, bloc b1, with a 4th-column playbook
  mark from targets.json: HONEST on the anchor facts, PUSH-UP / PUSH-DOWN on the
  contested cruxes per sleeper_direction (up->toward 5, down->toward 0), steering
  toward a confident lab-leak verdict.

Assignment line format: <nid>\\tA\\t<bloc>\\t<mark>
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
COVID = ROOT / "covid"


def flip_rating_mode():
    cfg = json.loads((COVID / "config.json").read_text())
    cfg["rating_mode_only"] = True
    (COVID / "config.json").write_text(json.dumps(cfg, indent=2) + "\n")
    return cfg["rating_mode_only"]


def all_node_ids():
    ids = []
    for line in (COVID / "events.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e["verb"] == "create_node":
            ids.append(e["payload"]["id"])
    return ids


def main():
    nodes = all_node_ids()
    roster = json.loads((HERE / "roster.json").read_text())["agents"]
    tgt = json.loads((HERE / "targets.json").read_text())
    honest_set = set(tgt["sleeper_honest"])
    direction = tgt["sleeper_direction"]

    adir = HERE / "assign"
    adir.mkdir(exist_ok=True)
    for a in roster:
        lines = []
        for nid in nodes:
            if a["role"] == "sleeper":
                if nid in honest_set:
                    mark = "HONEST"
                else:
                    d = direction.get(nid)
                    # targets.json direction is lab-oriented; a zoo-push bloc flips it.
                    if a.get("direction") == "zoo":
                        d = {"up": "down", "down": "up"}.get(d, d)
                    mark = "PUSH-UP" if d == "up" else "PUSH-DOWN" if d == "down" else "HONEST"
            else:
                mark = "HONEST"
            lines.append(f"{nid}\tA\t{a['bloc']}\t{mark}")
        (adir / f"{a['id']}.tsv").write_text("\n".join(lines) + "\n")

    rm = flip_rating_mode()
    # sanity: every sleeper-direction / honest node is a real node id
    unknown = (set(honest_set) | set(direction)) - set(nodes)
    print(f"rating_mode_only={rm}; {len(nodes)} nodes; {len(roster)} agents assigned")
    print(f"sleeper: {len(honest_set)} honest-marked, {len(direction)} push-marked "
          f"({sum(1 for v in direction.values() if v=='up')} up / "
          f"{sum(1 for v in direction.values() if v=='down')} down)")
    if unknown:
        print(f"WARNING unknown node ids in targets.json: {sorted(unknown)}")


if __name__ == "__main__":
    main()
