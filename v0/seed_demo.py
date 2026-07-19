#!/usr/bin/env python3
"""seed_demo.py -- lay down a small, deliberately TRIVIAL placeholder graph.

This is NOT a real analysis of the dev question ("Are eggs good for you?").
It exists only so the viewer and the CLI have something non-empty to show
while exercising every part of the grammar (grounds, a conjunction group,
an antithesis set, agreement, a competing title/phrasing, a friction flag).
The real hand-seed is a separate human step (BUILD-SPEC.md §4a).

Usage:
    python3 seed_demo.py --data DIR [--wipe]

`--data` is required (no default) -- name the graph directory explicitly,
e.g. `--data data/` for the repo's demo graph. This matches graph.py: an
operational finding from multi-agent runs was that a forgotten `--data`
silently fell through to a shared default and polluted the wrong graph.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from reasonable import ops

AGENTS = ["agent-01", "agent-02", "agent-03"]


def seed(data_dir: Path) -> None:
    def create(agent, text, **kw):
        res = ops.cmd_create_node(data_dir, agent, text, **kw)
        assert res.ok, res.errors
        return res.id

    def ground(agent, frm, to, group=None):
        res = ops.cmd_draw_ground(data_dir, agent, frm, to, group=group)
        assert res.ok, res.errors
        return res.id

    def antithesis(agent, node, set_id=None):
        res = ops.cmd_add_antithesis(data_dir, agent, node, set_id=set_id or "new")
        assert res.ok, res.errors
        return res.id

    def agree(agent, target):
        res = ops.cmd_agree(data_dir, agent, target)
        assert res.ok, res.errors

    # 10 trivial placeholder nodes -- "widget A supports widget B" style
    # claims, not real egg-nutrition content.
    n1 = create("agent-01", "Placeholder claim: widget A is thoroughly documented.",
                title="Widget A is documented")
    n2 = create("agent-01", "Placeholder claim: widget B depends on widget A being documented.",
                title="Widget B depends on A")
    n3 = create("agent-02", "Placeholder claim: widget C was reviewed by an independent panel.",
                title="Widget C was reviewed")
    n4 = create("agent-02", "Placeholder claim: widget D passed its test suite.",
                title="Widget D passed tests")
    n5 = create("agent-02", "Placeholder claim: widget E, built from C and D jointly, is production-ready.",
                title="Widget E is production-ready")
    n6 = create("agent-03", "Placeholder external-anchor: a fictional style guide recommends widget A.",
                kind="external_anchor", source="https://example.invalid/style-guide",
                title="Style guide recommends A")
    n7 = create("agent-01", "Placeholder rival claim: widget F is a better default than widget A.",
                title="Widget F is a better default")
    n8 = create("agent-03", "Placeholder rival claim: widget G is a better default than widget A.",
                title="Widget G is a better default")
    n9 = create("agent-02", "Placeholder claim: widget H is deprecated and should not be used.",
                title="Widget H is deprecated")
    n10 = create("agent-03", "Placeholder claim: widget I supersedes widget H.",
                 title="Widget I supersedes H")

    # Grounds / Dependents chain.
    ground("agent-01", n1, n2)              # A grounds B
    ground("agent-03", n6, n1)              # style guide anchor grounds A
    ground("agent-02", n10, n9)             # I grounds "H is deprecated"

    # Conjunction group: C and D jointly ground E.
    g = ground("agent-02", n3, n5, group="new")
    # draw-ground returns the *edge* id for the first member; join the same
    # group for the second member by reusing the group id stamped on that edge
    # (recomputed from the freshly-rebuilt graph rather than parsing g).
    from reasonable import queries
    graph = queries.load_graph(data_dir)
    gid = next(e["group"] for e in graph["ground_edges"] if e["id"] == g)
    ground("agent-02", n4, n5, group=gid)

    # Antithesis set: A, F, G are rival "best default" claims.
    s = antithesis("agent-01", n1)
    antithesis("agent-01", n7, set_id=s)
    antithesis("agent-03", n8, set_id=s)

    # Some agreement (author never agrees with their own object).
    agree("agent-02", _edge_from_to(data_dir, n1, n2))
    agree("agent-03", _edge_from_to(data_dir, n1, n2))
    agree("agent-02", f"set:{s}:{n7}")
    agree("agent-01", f"title:{n5}:t0")

    # Competing title + phrasing (norm: split/merge by drawing, not deleting).
    ops.cmd_propose_title(data_dir, "agent-03", n2, "B needs A documented first")
    ops.cmd_propose_phrasing(data_dir, "agent-02", n9,
                              "Placeholder claim: widget H should be retired in favor of widget I.")

    # A friction flag -- this is the primary deliverable of v0, not an
    # afterthought, so the demo always includes at least one.
    ops.cmd_flag_friction(
        data_dir, "agent-01",
        "Couldn't cleanly express that widget H's deprecation is CONDITIONAL on "
        "widget I's rollout finishing -- support-only grammar has no natural way "
        "to say 'this claim's strength depends on an event, not just on agreement'.",
        refs=[n9, n10],
    )

    ops.rebuild(data_dir)


def _edge_from_to(data_dir: Path, frm: str, to: str) -> str:
    from reasonable import queries
    graph = queries.load_graph(data_dir)
    for e in graph["ground_edges"]:
        if e["from"] == frm and e["to"] == to:
            return e["id"]
    raise LookupError(f"no edge {frm} -> {to}")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data", type=Path, required=True,
                    help="data directory to seed (REQUIRED -- no default; e.g. --data data/)")
    p.add_argument("--wipe", action="store_true", help="delete existing events.jsonl/graph.json first")
    args = p.parse_args(argv)

    if args.wipe:
        for name in ("events.jsonl", "graph.json", "audit.jsonl"):
            f = args.data / name
            if f.exists():
                f.unlink()

    events_file = args.data / "events.jsonl"
    if events_file.exists() and events_file.stat().st_size > 0 and not args.wipe:
        print(f"{events_file} already has content; pass --wipe to reseed from scratch.", file=sys.stderr)
        return 1

    seed(args.data)
    print(f"seeded demo graph into {args.data}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
