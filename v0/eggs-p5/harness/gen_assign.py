#!/usr/bin/env python3
"""Per-round sortition assignment for the eggs-p4 volume run.

Reads the CURRENT graph.json + the append-only events.jsonl, enumerates every
rateable (target, dim) pair, and hands each one a fresh set of eligible raters
until it reaches this round's cumulative depth target -- excluding the item's
author (can't self-rate) and anyone who already rated it in a prior round.
Load-balanced (each round spreads slots to the least-loaded eligible agents)
and fully deterministic (hash of round/target/dim/agent -- no wall-clock RNG).

Rateable items:
  - every node            -> (n###, "A")               author = node.author
  - every UNGROUPED edge  -> (e###, "A")               author = edge.author
      (grouped member edges are abstained; the group is the rateable unit)
  - every conjunction grp -> ("group:g#", "A")         author = group.author
  - every node's primary phrasing -> ("phrasing:n###:p#", "R") and (..., "C")
                                                        author = phrasing.author

Usage:  gen_assign.py --data <dir> --roster roster.json --round N
                      --target-depth D [--max-per-agent M] [--nblocs 3]
Writes: <harness>/assign/r{N}/{agent}.tsv   (lines: target<TAB>dim<TAB>bloc)
        <harness>/assign/r{N}/_coverage.json (per-item depth report)
"""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent


def h(*parts) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest(), 16)


def load_graph(data_dir: Path) -> dict:
    return json.loads((data_dir / "graph.json").read_text())


def rateable_items(g: dict, nodes_only: bool = False):
    """Yield (target, dim, author) for every rateable pair in the graph.
    nodes_only: restrict to node Agreement items (cleanest expert-vs-crowd axis;
    keeps depth high under a limited rating budget)."""
    for n in g["nodes"]:
        yield (n["id"], "A", n.get("author"))
        if nodes_only:
            continue
        pid = n.get("primary_phrasing")
        if pid:
            pauthor = next((p.get("author") for p in n.get("phrasings", []) if p.get("id") == pid), None)
            yield (f"phrasing:{n['id']}:{pid}", "R", pauthor)
            yield (f"phrasing:{n['id']}:{pid}", "C", pauthor)
    if nodes_only:
        return
    for e in g["ground_edges"]:
        if e.get("group"):
            continue  # grouped member edge -> abstain; rate the group instead
        yield (e["id"], "A", e.get("author"))
    for grp in g.get("conjunction_groups", []):
        yield (f"group:{grp['id']}", "A", grp.get("author"))


def existing_raters(data_dir: Path):
    """(target, dim) -> set(agents) who already have a rating recorded."""
    seen = defaultdict(set)
    path = data_dir / "events.jsonl"
    if not path.exists():
        return seen
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        ev = json.loads(line)
        if ev.get("verb") != "rate":
            continue
        p = ev.get("payload", {})
        tgt, dim, agent = p.get("target"), p.get("dim"), ev.get("agent")
        if tgt and dim and agent:
            seen[(tgt, dim)].add(agent)
    return seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--roster", default=str(HERE / "roster.json"))
    ap.add_argument("--round", type=int, required=True)
    ap.add_argument("--target-depth", type=int, required=True)
    ap.add_argument("--max-per-agent", type=int, default=40)
    ap.add_argument("--nblocs", type=int, default=3)
    ap.add_argument("--nodes-only", action="store_true",
                    help="restrict to node Agreement items (deep single-pass BTS run)")
    args = ap.parse_args()

    data_dir = Path(args.data).resolve()
    g = load_graph(data_dir)
    roster = json.loads(Path(args.roster).read_text())
    agent_ids = [a["id"] for a in roster["agents"]]

    items = list(rateable_items(g, nodes_only=args.nodes_only))
    already = existing_raters(data_dir)

    # per-round load counter, seeded so rounds spread differently
    load = defaultdict(int)
    assignments = defaultdict(list)  # agent -> [(target, dim, bloc)]
    coverage = {}

    # NEEDIEST-FIRST: items with the least existing coverage get first pick of
    # the (capped) slot budget, so the emptiest items fill before well-covered
    # ones. Deterministic tie-break by hash -> identical on resume.
    items_sorted = sorted(
        items, key=lambda it: (len(already.get((it[0], it[1]), set())),
                               h(args.round, it[0], it[1])))

    for target, dim, author in items_sorted:
        prior = already.get((target, dim), set())
        cur_depth = len(prior)
        need = max(0, args.target_depth - cur_depth)
        # eligible: not author, not already rated, under per-agent cap
        eligible = [a for a in agent_ids
                    if a != author and a not in prior and load[a] < args.max_per_agent]
        # order eligibles by (current load asc, then stable hash) -> load balance
        eligible.sort(key=lambda a: (load[a], h(args.round, target, dim, a)))
        chosen = eligible[:need]
        for a in chosen:
            bloc = "b%d" % (h("bloc", target, dim, a) % args.nblocs + 1)
            assignments[a].append((target, dim, bloc))
            load[a] += 1
        coverage[f"{target}:{dim}"] = {
            "prior": cur_depth, "added": len(chosen),
            "target": args.target_depth, "reached": cur_depth + len(chosen),
            "short": max(0, need - len(chosen)),
        }

    outdir = HERE / "assign" / f"r{args.round}"
    outdir.mkdir(parents=True, exist_ok=True)
    # clear stale files
    for f in outdir.glob("*.tsv"):
        f.unlink()
    for a in agent_ids:
        lines = assignments.get(a, [])
        # stable per-agent order
        lines.sort(key=lambda x: (x[1], x[0]))
        (outdir / f"{a}.tsv").write_text(
            "".join(f"{t}\t{d}\t{b}\n" for t, d, b in lines))
    (outdir / "_coverage.json").write_text(json.dumps(coverage, indent=2))

    # summary
    loads = [len(assignments.get(a, [])) for a in agent_ids]
    shorts = sum(1 for c in coverage.values() if c["short"] > 0)
    reached = [c["reached"] for c in coverage.values()]
    reached.sort()
    med = reached[len(reached) // 2] if reached else 0
    print(json.dumps({
        "round": args.round, "target_depth": args.target_depth,
        "items": len(items), "total_new_ratings": sum(loads),
        "per_agent_min": min(loads), "per_agent_max": max(loads),
        "per_agent_mean": round(sum(loads) / len(loads), 1),
        "items_short_of_target": shorts,
        "median_reached_depth": med,
        "min_reached_depth": min(reached) if reached else 0,
    }, indent=2))


if __name__ == "__main__":
    main()
