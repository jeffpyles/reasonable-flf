#!/usr/bin/env python3
"""Build eggs-graph-v2 -- the structural-pass rebuild of the eggs graph.

Experimental parallel of `eggs-graph/` (original untouched). Eggs was already
structurally healthy (0 hubs, atomic claims, real evidence nodes), so this pass
is conservative and surgical -- the point is to remove the specific cruft and
apply the same standard, NOT to reinvent a careful evidence graph:

- DROP the one bundled root, n002 ("does not raise CVD risk AND provides real
  benefits") -- two independent claims. It was already half-decomposed into
  n065 (the risk half) + n066 (the benefits half); this pass retires the
  bundle and promotes those two to first-class.
- Re-home the nodes that only supported n002 through now-ghosted edges (their
  support flows to the risk-NO half n065 or the benefits summary n066), and
  wire up the interpretive leaves that supported nothing (n014, n039, n040).
- LAYER the benefits: evidence -> n058/n059/n060 -> n066 -> the ought, instead
  of benefit claims hanging directly off the ought.
- TYPE the two value conclusions as `ought` (n063 reasonable-to-eat, n064
  precaution), trim each to its ought, and give each an explicit value premise
  (Hume-clean, ought grounds ought) -- fixing the is/ought bundle flagged as
  friction f17 on the original.
- DE-SCAFFOLD titles: drop the "Rival:" prefix that leaked build-scaffolding
  into n033/n037, and drop the "eggs are bad for your health" framing from
  n001's title (the node is the risk claim; "bad for health" is the ought).
- DROP all 14 already-ghosted edges and the spurious/duplicate sets (s2, s10).

Every evidence node and interpretive claim is carried VERBATIM from the
original graph.json (no fabricated science). The 20-rater Sonnet Agreement
panel is replayed onto every surviving proposition and edge; dropped/new
targets start unrated for a Haiku quorum pass to fill.

Run from v0/:  python3 eggs-graph-v2/build.py   (wipes + rebuilds this dir)
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from reasonable import ops  # noqa: E402

DATA = Path(__file__).resolve().parent
ORIGINAL = DATA.parent / "eggs-graph"
AUTHOR = "structure-pass"

DROP_NODES = {"n002"}

# id -> field overrides (text/title/kind). Everything else carried verbatim.
NODE_EDITS = {
    "n001": {"title": "Eggs meaningfully raise CVD and mortality risk"},
    "n033": {"title": "Some meta-analyses find a CVD-specific mortality signal"},
    "n037": {"title": "Heterogeneity may reflect real dose/susceptibility differences"},
    "n063": {"kind": "ought",
             "title": "Eating eggs is reasonable for most people",
             "text": "For most people, eating eggs in moderation is a reasonable dietary choice."},
    "n064": {"kind": "ought",
             "title": "Precaution is warranted for most people",
             "text": "A precautionary approach to egg and dietary-cholesterol intake is warranted "
                     "for most people."},
}

# new nodes: logical name -> (kind, title, text)
NEW_NODES = {
    # two intermediate limbs under the "unresolved" synthesis, so its 9 grounds
    # become a layered tree instead of a star (same de-star as the debate pass).
    "LIMB_NOTRIAL": ("claim", "No trial evidence on real clinical endpoints",
        "The trial evidence that could settle egg causation on hard clinical endpoints is absent "
        "or measures only surrogate markers."),
    "LIMB_OBS": ("claim", "Observational evidence can't pin down causation",
        "The available observational and subgroup evidence cannot establish whether eggs causally "
        "affect health outcomes for most people."),
    "VAL_REASONABLE": ("ought", "Value: benefits justify a modest unproven risk",
        "A food with real nutritional benefits and only modest, unproven risks is a reasonable "
        "thing to eat."),
    "VAL_PRECAUTION": ("ought", "Value: limit exposure under unresolved harm",
        "When a plausible health harm is genuinely unresolved, limiting exposure is prudent, "
        "especially for higher-risk groups."),
}

# old edge id -> new logical target: reroute the unresolved node's direct grounds
# through the two limbs (keeps the conjunction group g1 intact on LIMB_NOTRIAL).
EDGE_RETARGET = {
    "e040": "LIMB_NOTRIAL",   # no long-term RCTs (g1)
    "e041": "LIMB_NOTRIAL",   # RCT impractical (g1)
    "e046": "LIMB_NOTRIAL",   # surrogate-endpoint RCTs
    "e042": "LIMB_OBS",       # observational evidence mixed
    "e044": "LIMB_OBS",       # association != causation
    "e045": "LIMB_OBS",       # residual confounding
}

# edges to DROP beyond the ghosts + n002-touching ones (benefits now layer via n066)
EDGE_DROP = {"e065", "e066"}

# new edges (from, to) by logical/real id -- re-homing + layering + value premises
NEW_EDGES = [
    ("n004", "n065"),          # modest LDL rise -> no meaningful CVD risk
    ("n011", "n065"),          # dietary cholesterol limited effect -> no meaningful CVD risk
    ("n014", "LIMB_OBS"),      # responder variation -> observational can't pin down causation
    ("n040", "LIMB_OBS"),      # T2D risk = confounding -> observational can't pin down causation
    ("LIMB_NOTRIAL", "n048"),  # limb -> unresolved
    ("LIMB_OBS", "n048"),      # limb -> unresolved
    ("n066", "n063"),          # benefits summary -> reasonable to eat
    ("n065", "n063"),          # low risk -> reasonable to eat
    ("n038", "n064"),          # T2D subgroup finding -> precaution (un-ghosts e069)
    ("n039", "n064"),          # T2D risk real causal -> precaution
    ("VAL_REASONABLE", "n063"),
    ("VAL_PRECAUTION", "n064"),
]

# antithesis sets to keep (genuine rivals), n002 swapped to n065 in the root set
SETS = [
    ["n001", "n065", "n048"],   # s1: the risk question (raises / doesn't / unresolved)
    ["n008", "n009", "n011"],   # s3: what drives serum cholesterol
    ["n032", "n033"],           # s4: which mortality endpoint
    ["n034", "n035"],           # s5: mortality signal causal vs confounding
    ["n036", "n037"],           # s6: heterogeneity confounding vs real
    ["n039", "n040"],           # s7: T2D risk causal vs confounding
    ["n061", "n062"],           # s8: cap removal exoneration vs still-uncertain
    ["n063", "n064"],           # s9: the ought value-crux
]


def build():
    for f in ("events.jsonl", "graph.json"):
        p = DATA / f
        if p.exists():
            p.unlink()
    orig = json.load(open(ORIGINAL / "graph.json"))
    (DATA / "config.json").write_text(json.dumps({
        "question": ("Are eggs bad for your health? (Does egg / dietary-cholesterol consumption "
                     "meaningfully raise cardiovascular-disease and mortality risk for most "
                     "people?)"),
        "rating_mode_only": True,
    }, indent=2) + "\n")

    obyid = {n["id"]: n for n in orig["nodes"]}
    id_map = {}   # old node id -> new node id
    author_of = {}

    # --- nodes: carry verbatim in original order, applying edits, skipping drops ---
    for n in orig["nodes"]:
        oid = n["id"]
        if oid in DROP_NODES:
            continue
        edit = NODE_EDITS.get(oid, {})
        kind = edit.get("kind", n.get("kind", "claim"))
        # normalize legacy external_anchor -> evidence for new builds
        if kind == "external_anchor":
            kind = "evidence"
        text = edit.get("text", n["phrasings"][0]["text"])
        title = edit.get("title") or (n["titles"][0]["text"] if n.get("titles") else None)
        source = n.get("source_ref") or None
        author = n.get("author", AUTHOR)
        res = ops.cmd_create_node(DATA, author, text, kind=kind, source=source, title=title)
        assert res.ok, (oid, res.errors)
        id_map[oid] = res.id
        author_of[res.id] = author

    # --- new nodes ---
    for name, (kind, title, text) in NEW_NODES.items():
        res = ops.cmd_create_node(DATA, AUTHOR, text, kind=kind, title=title)
        assert res.ok, (name, res.errors)
        id_map[name] = res.id
        author_of[res.id] = AUTHOR

    def nid(x):
        return id_map.get(x, x)

    # --- edges: carry live originals (minus ghosts / n002 / EDGE_DROP), then new ---
    edge_map = {}   # old edge id -> new edge id
    group_ids = {}  # old group id -> new group id
    for e in orig["ground_edges"]:
        if e.get("demoted") or e.get("ghost_eligible"):
            continue
        if e["id"] in EDGE_DROP:
            continue
        if e["from"] in DROP_NODES or e["to"] in DROP_NODES:
            continue
        grp = e.get("group")
        author = e.get("author", AUTHOR)
        to = nid(EDGE_RETARGET.get(e["id"], e["to"]))
        if grp:
            g_arg = "new" if grp not in group_ids else group_ids[grp]
            res = ops.cmd_draw_ground(DATA, author, nid(e["from"]), to, group=g_arg)
            assert res.ok, (e["id"], res.errors)
            if grp not in group_ids:
                # group id is derivable from the graph; re-read to capture it
                g = json.load(open(DATA / "graph.json"))
                group_ids[grp] = g["ground_edges"][-1].get("group")
        else:
            res = ops.cmd_draw_ground(DATA, author, nid(e["from"]), to)
            assert res.ok, (e["id"], res.errors)
        edge_map[e["id"]] = res.id

    for frm, to in NEW_EDGES:
        res = ops.cmd_draw_ground(DATA, AUTHOR, nid(frm), nid(to))
        assert res.ok, (frm, to, res.errors)

    # --- antithesis sets ---
    for members in SETS:
        set_id = "new"
        for m in members:
            res = ops.cmd_add_antithesis(DATA, AUTHOR, nid(m), set_id=set_id)
            assert res.ok, (m, res.errors)
            if set_id == "new":
                set_id = res.id

    return id_map, edge_map


def replay_ratings(id_map, edge_map):
    # Old ids retyped to `ought`: their original A ratings were TRUTH ratings of
    # an is/ought bundle (and the original graph had already era-sealed them for
    # exactly this reason). An ought is rated on ENDORSEMENT, not truth, so those
    # ratings must NOT carry -- the node starts fresh for an endorsement pass.
    rating_reset = {oid for oid, ed in NODE_EDITS.items() if ed.get("kind") == "ought"}
    events = [json.loads(line) for line in (ORIGINAL / "events.jsonl").open()]
    replayed = skipped = reset = 0
    for e in sorted(events, key=lambda e: e["seq"]):
        if e["verb"] != "rate":
            continue
        p = e["payload"]
        tgt = p["target"]
        if tgt in rating_reset:
            reset += 1
            continue
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
    print(f"ratings: {replayed} replayed, {skipped} skipped (dropped/new), "
          f"{reset} reset (retyped to ought -> endorsement pass)")


if __name__ == "__main__":
    id_map, edge_map = build()
    replay_ratings(id_map, edge_map)
    print(f"built {len(id_map)} nodes into {DATA}")
