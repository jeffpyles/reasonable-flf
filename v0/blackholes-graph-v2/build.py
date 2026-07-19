#!/usr/bin/env python3
"""Build blackholes-graph-v2 -- the structural-pass rebuild of the black-holes graph.

Experimental parallel of `blackholes-graph/` (original untouched). The graph was already
structurally healthy; its one pathology was the safety-thesis hub (n001 had 12 direct grounds).
This pass is minimal and surgical, and applies the harness-learned discipline (limb texts are
category-level claims, not enumerations):

- DE-STAR n001 (12 grounds -> 5 limbs). The safety case already contained natural aggregator
  claims, so four existing nodes are REUSED as limbs (n007 production-needs-new-physics, n015
  would-evaporate, n022 layered-physical-case, n067 independent-reviews-converge) and only ONE new
  limb is created -- "the operating LHC has produced no black holes" -- for the direct-search
  material that lacked a head. The 12 top grounds re-route through these five; one redundant edge
  (n066 grounded both n001 and the verdict limb n067) is dropped.

Every evidence node and interpretive claim is carried VERBATIM from the original graph.json (no
fabricated physics). No nodes are removed and no antithesis sets change -- the four rival sets and
five conjunction groups were already clean. The 20-rater Sonnet Agreement panel is replayed onto
every surviving node (blackholes edges were never rated, so there are no edge ratings to carry);
the one new limb starts unrated for a Haiku quorum pass, which also fills R+C on all phrasings
(the original carried none) and conditional Agreement on all edges.

Run from v0/:  python3 blackholes-graph-v2/build.py   (wipes + rebuilds this dir)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reasonable import ops  # noqa: E402

DATA = Path(__file__).resolve().parent
ORIGINAL = DATA.parent / "blackholes-graph"
AUTHOR = "structure-pass"

# title refinements for the reused-as-limb nodes (text carried verbatim to preserve ratings)
NODE_EDITS = {
    "n007": {"title": "Production needs unconfirmed new physics"},
    "n015": {"title": "Any micro black hole would evaporate at once"},
    "n022": {"title": "The astrophysical safety case is layered"},
    "n067": {"title": "Independent expert reviews converge on no danger"},
}

# new limb node: logical name -> (kind, title, text)
NEW_NODES = {
    "L_EMPIRICAL": ("claim", "The operating LHC has produced no black holes",
        "Direct operation of the LHC has produced no black holes: its collisions yield only ordinary "
        "Standard-Model particle showers, and dedicated searches have found no black-hole signature."),
}

# old edge id -> new logical target: re-route n001's raw grounds through the five limbs
EDGE_RETARGET = {
    "e010": "n015",        # production/evaporation inseparable -> evaporation limb
    "e021": "n015",        # Hawking theoretically solid -> evaporation limb
    "e079": "n022",        # empirical layer not load-bearing -> layered-case limb
    "e059": "n067",        # formal reviewed verdict -> verdict limb
    "e063": "n067",        # contrarian bypassed peer review -> verdict limb
    "e050": "L_EMPIRICAL",  # LHC not uniquely powerful -> searches limb
    "e053": "L_EMPIRICAL",  # LHC produces ordinary particles -> searches limb
}
# edges dropped outright (redundant): n066 grounds n001 directly AND via n067
EDGE_DROP = {"e067"}
# new edges beyond the carried ones
NEW_EDGES = [("L_EMPIRICAL", "n001")]


def build():
    for f in ("events.jsonl", "graph.json"):
        p = DATA / f
        if p.exists():
            p.unlink()
    orig = json.load(open(ORIGINAL / "graph.json"))
    (DATA / "config.json").write_text(json.dumps({
        "question": ("Could a high-energy particle collider (the LHC) create a black hole that "
                     "destroys Earth?"),
        "rating_mode_only": True,
    }, indent=2) + "\n")

    id_map = {}
    for n in orig["nodes"]:
        oid = n["id"]
        edit = NODE_EDITS.get(oid, {})
        kind = edit.get("kind", n.get("kind", "claim"))
        if kind == "external_anchor":
            kind = "evidence"
        text = edit.get("text", n["phrasings"][0]["text"])
        title = edit.get("title") or (n["titles"][0]["text"] if n.get("titles") else None)
        source = n.get("source_ref") or None
        author = n.get("author", AUTHOR)
        res = ops.cmd_create_node(DATA, author, text, kind=kind, source=source, title=title)
        assert res.ok, (oid, res.errors)
        id_map[oid] = res.id
    for name, (kind, title, text) in NEW_NODES.items():
        res = ops.cmd_create_node(DATA, AUTHOR, text, kind=kind, title=title)
        assert res.ok, (name, res.errors)
        id_map[name] = res.id

    def nid(x):
        return id_map.get(x, x)

    # edges: carry originals (retargeted / dropped), preserving conjunction groups
    edge_map = {}
    group_ids = {}
    for e in orig["ground_edges"]:
        if e["id"] in EDGE_DROP:
            continue
        grp = e.get("group")
        author = e.get("author", AUTHOR)
        to = nid(EDGE_RETARGET.get(e["id"], e["to"]))
        if grp:
            g_arg = "new" if grp not in group_ids else group_ids[grp]
            res = ops.cmd_draw_ground(DATA, author, nid(e["from"]), to, group=g_arg)
            assert res.ok, (e["id"], res.errors)
            if grp not in group_ids:
                g = json.load(open(DATA / "graph.json"))
                group_ids[grp] = g["ground_edges"][-1].get("group")
        else:
            res = ops.cmd_draw_ground(DATA, author, nid(e["from"]), to)
            assert res.ok, (e["id"], res.errors)
        edge_map[e["id"]] = res.id
    for frm, to in NEW_EDGES:
        res = ops.cmd_draw_ground(DATA, AUTHOR, nid(frm), nid(to))
        assert res.ok, (frm, to, res.errors)

    # antithesis sets: carry verbatim (all four are genuine rivals)
    for s in orig["antithesis_sets"]:
        set_id = "new"
        for m in s["members"]:
            res = ops.cmd_add_antithesis(DATA, AUTHOR, nid(m["node"]), set_id=set_id)
            assert res.ok, (m, res.errors)
            if set_id == "new":
                set_id = res.id

    return id_map, edge_map


def replay_ratings(id_map, edge_map):
    events = [json.loads(line) for line in (ORIGINAL / "events.jsonl").open()]
    replayed = skipped = 0
    for e in sorted(events, key=lambda e: e["seq"]):
        if e["verb"] != "rate":
            continue
        p = e["payload"]
        tgt = p["target"]
        new = None
        if tgt.startswith("phrasing:"):
            _, node, pid = tgt.split(":")
            if node in id_map:
                new = f"phrasing:{id_map[node]}:{pid}"
        elif tgt.startswith("e") and tgt[1:].isdigit():
            new = edge_map.get(tgt)
        elif tgt in id_map:
            new = id_map[tgt]
        if new is None:
            skipped += 1
            continue
        res = ops.cmd_rate(DATA, e["agent"], new, p["dim"], float(p["value"]), bloc=p.get("bloc"))
        assert res.ok, (tgt, res.errors)
        replayed += 1
    print(f"ratings: {replayed} replayed, {skipped} skipped (new targets)")


if __name__ == "__main__":
    id_map, edge_map = build()
    replay_ratings(id_map, edge_map)
    print(f"built {len(id_map)} nodes into {DATA}")
