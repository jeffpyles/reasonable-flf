"""Read-verb implementations (BUILD-SPEC.md §2 "Read verbs").

All queries operate on a freshly folded graph.json-shaped dict (see
fold.to_graph_json) rather than trusting the on-disk graph.json file, so
reads are correct even if a rebuild was somehow skipped.
"""
from __future__ import annotations

import json
from collections import deque
from pathlib import Path

from . import assess, lifecycle, store
from .fold import DEFAULT_QUESTION, fold, is_evidence_kind, to_graph_json


def load_graph(data_dir) -> dict:
    events = store.read_events(data_dir)
    state = fold(events)
    config = store.read_config(data_dir)
    graph = to_graph_json(
        state,
        question=config.get("question", DEFAULT_QUESTION),
        assessment_config=config.get("assessment"),
        phase2_config=config.get("phase2"),
    )
    return attach_layers(attach_sources(graph, data_dir))


def resolve_source_map(data_dir) -> dict:
    """Map every source-ref an Evidence node might cite to a display record
    ``{title, url}`` -- so the source (the study) can be NAMED on the node
    body (FLF: make load-bearing evidence visible). Two ref namespaces, both
    read here, deterministically:
      - the graph's own build manifest ``<data_dir>/harness/sources.json``
        (``{id, title, url, ...}``) -- the ``s0N`` tokens the flagship builds cite;
      - the curated pack(s) ``<data_dir>/../sources/<pack>/index.json``
        (``ref_id -> citation``, ``url``) -- the AGENT-GUIDE §6 pack refs.
    Both are merged (the two namespaces don't collide); a ref that resolves to
    neither is later displayed as its own raw string. Missing/unreadable files
    are skipped silently (a --source may be free text with no manifest)."""
    out: dict[str, dict] = {}
    data_dir = Path(data_dir)
    pack_root = data_dir.resolve().parent / "sources"
    if pack_root.is_dir():
        for pack_dir in sorted(p for p in pack_root.iterdir() if p.is_dir()):
            idx = pack_dir / "index.json"
            if not idx.is_file():
                continue
            try:
                entries = json.loads(idx.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            for e in entries:
                rid = e.get("ref_id")
                if rid:
                    out[rid] = {"title": e.get("citation", rid), "url": e.get("url")}
    manifest = data_dir / "harness" / "sources.json"
    if manifest.is_file():
        try:
            m = json.loads(manifest.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            m = None
        if isinstance(m, dict):
            for s in m.get("sources", []):
                sid = s.get("id")
                if sid:
                    out[sid] = {"title": s.get("title", sid), "url": s.get("url")}
    return out


def attach_sources(graph: dict, data_dir) -> dict:
    """Bake a resolved ``source`` record onto every Evidence node in a graph
    dict, so the viewer can name the study on the node body (FLF requirement).
    Mutates and returns ``graph``. Conditional: only Evidence nodes that carry
    a ``source_ref`` gain the field, so non-evidence nodes and source-free
    graphs stay byte-identical. Shape: ``{"ref", "title", "url"}`` -- ``title``
    falls back to the raw ref (self-describing free-text sources, e.g. debate),
    ``url`` is ``null`` when unknown."""
    smap = resolve_source_map(data_dir)
    for n in graph.get("nodes", []):
        if not is_evidence_kind(n.get("kind", "")):
            continue
        ref = n.get("source_ref")
        if not ref:
            continue
        hit = smap.get(ref, {})
        n["source"] = {"ref": ref, "title": hit.get("title", ref), "url": hit.get("url")}
    return graph


def attach_layers(graph: dict) -> dict:
    """Bake a per-node ``layer`` (support-depth) onto every node, so the viewer
    can seed initial x-positions before its force sim runs (evidence/sources at
    layer 0 on the left, dependents increasing to the right). Kahn longest-path
    over the non-demoted ground edges (support flows from -> to, so
    ``layer[to] = max(layer[from]) + 1``); nodes with no live incoming ground
    edge are layer 0. Deterministic (ties broken by node id). Cyclic inputs
    degrade gracefully -- any node left unresolved by a cycle stays at its
    partial layer, and the viewer's own force sim is the cyclic fallback."""
    nodes = [n["id"] for n in graph.get("nodes", [])]
    edges = [(e["from"], e["to"]) for e in graph.get("ground_edges", []) if not e.get("demoted")]
    indeg = {nid: 0 for nid in nodes}
    out = {nid: [] for nid in nodes}
    for f, t in edges:
        if f in indeg and t in indeg:
            indeg[t] += 1
            out[f].append(t)
    layer = {nid: 0 for nid in nodes}
    # Kahn longest-path; process in sorted id order for determinism.
    ready = sorted(nid for nid in nodes if indeg[nid] == 0)
    seen = set(ready)
    while ready:
        u = ready.pop(0)
        for v in out[u]:
            if layer[u] + 1 > layer[v]:
                layer[v] = layer[u] + 1
            indeg[v] -= 1
            if indeg[v] == 0 and v not in seen:
                seen.add(v)
                # keep the frontier sorted so ties resolve deterministically
                ready.append(v)
                ready.sort()
    for n in graph.get("nodes", []):
        n["layer"] = layer.get(n["id"], 0)
    return graph


def reputation(graph: dict, agent: str | None = None):
    """ASSESSMENT-SPEC.md §6 `reputation` read verb: the whole accounts
    table, or one agent's account (None if that agent is unknown)."""
    accounts = graph.get("accounts", [])
    if agent is None:
        return accounts
    for a in accounts:
        if a["agent"] == agent:
            return a
    return None


def effective_config(data_dir) -> dict:
    """ASSESSMENT-SPEC.md §6 `show-config` read verb: the config actually in
    effect -- `<data>/config.json`'s raw content with every missing
    `assessment` knob filled in from its documented default."""
    raw = store.read_config(data_dir)
    return {
        "question": raw.get("question", DEFAULT_QUESTION),
        "assessment": assess.resolve_config(raw.get("assessment")),
        # PHASE2-SPEC.md §1: the phase-2 lifecycle/heat/bloc/nudge knobs,
        # same "missing config -> documented defaults" convention as
        # `assessment` above.
        "phase2": lifecycle.resolve_config(raw.get("phase2")),
        # ASSESSMENT-SPEC.md §7 (v1.5): when true, the graph is in enforced
        # Rating mode -- every rater-facing read verb (get-node, neighborhood,
        # list-comments) is blinded regardless of any CLI flag, so blindness
        # is a condition imposed on the dataset, not an agent's opt-in.
        "rating_mode_only": bool(raw.get("rating_mode_only", False)),
    }


def rating_mode_only(data_dir) -> bool:
    """Is enforced blind Rating mode switched on for this dataset? (config.json
    top-level `rating_mode_only`). When true there is NO CLI way to un-blind a
    rater read -- the escape hatch for analysis/experimenters is reading
    graph.json directly, which agents don't do."""
    return bool(store.read_config(data_dir).get("rating_mode_only", False))


# --- PHASE2-SPEC.md §1/§8: sealed read surfaces -----------------------------
#
# graph.json itself ALWAYS carries the real numbers plus `state` (sealing is
# a read-surface convention only, per §1: "the log is public anyway"). These
# helpers are applied by the read verbs named in §8 (get-node, neighborhood,
# search, list-sets) to mask any block whose `state` is "sealed", UNLESS the
# caller passed `--include-sealed`. Masking never touches graph.json on
# disk -- it's a pure, per-call presentation transform over an already-loaded
# graph dict.

def _mask_block(block: dict | None, include_sealed: bool) -> dict | None:
    if include_sealed or not block or block.get("state") != "sealed":
        return block
    return {"mean": None, "pending": True, "n": block.get("n", 0)}


def _mask_quality(quality: dict, include_sealed: bool) -> dict:
    return {
        "R": _mask_block(quality.get("R"), include_sealed),
        "C": _mask_block(quality.get("C"), include_sealed),
    }


def mask_node(node: dict, include_sealed: bool) -> dict:
    """A copy of one `nodes[]` record with its own `agreement`/`quality`
    blocks, its phrasings' `scores`, and its comments' `scores` masked when
    sealed (PHASE2-SPEC.md §1/§8)."""
    if include_sealed:
        return node
    out = dict(node)
    out["agreement"] = _mask_block(node.get("agreement"), include_sealed)
    out["quality"] = _mask_quality(node.get("quality", {}), include_sealed)
    out["phrasings"] = [
        dict(p, scores=_mask_quality(p.get("scores", {}), include_sealed))
        for p in node.get("phrasings", [])
    ]
    out["comments"] = [
        dict(c, scores=_mask_quality(c.get("scores", {}), include_sealed))
        for c in node.get("comments", [])
    ]
    return out


def mask_edge(edge: dict, include_sealed: bool) -> dict:
    """A copy of one `ground_edges[]` record with its `agreement` and its
    comments' `scores` masked when sealed."""
    if include_sealed:
        return edge
    out = dict(edge)
    out["agreement"] = _mask_block(edge.get("agreement"), include_sealed)
    out["comments"] = [
        dict(c, scores=_mask_quality(c.get("scores", {}), include_sealed))
        for c in edge.get("comments", [])
    ]
    return out


# --- Rating mode (ASSESSMENT-SPEC.md §7 "Reading vs Rating mode"): a blind
# read that hides every consensus CUE so a rater forms an independent judgment
# before seeing how others landed. Reading mode (rating_mode=False, the default)
# shows all cues as before. This exists because relying on the rater to "not
# look" fails when the read verb surfaces the aggregate: get-node returns
# agreement.mean/n/stdev and the comment thread, both of which anchor a rater.
# What Rating mode blinds, per (target, dim) the rater is about to judge:
#   - every rated aggregate: node/edge `agreement` (A), `quality` (R/C), and
#     each phrasing's/title's `scores` (R/C/A), all nulled to `hidden`;
#   - the whole comment thread (and comment_count): 30 of eggs-p6's carried
#     comments stated explicit rating values ("...rated low (1.3)"), so comments
#     are a rating cue and are removed until Reading mode;
#   - rating `heat` (activity implies contestedness).
# It deliberately leaves node/phrasing/title/edge TEXT, Ground/Dependent
# STRUCTURE, antithesis membership, and edge typing intact -- you must read the
# claim and its support to rate it; those are not consensus-on-this-rating cues.
# The v0 structural `agrees`/`strength`/`belonging` counts are left as-is: they
# are the separate structural-consensus layer, not the graded rating the rater
# is producing (masking them too is a future knob if wanted).
_HIDDEN_BLOCK = {"mean": None, "n": 0, "stdev": None, "state": "hidden", "hidden": True}


def _blind_block(block: dict | None) -> dict | None:
    if block is None:
        return None
    return dict(_HIDDEN_BLOCK)


def _blind_quality(quality: dict | None) -> dict:
    q = quality or {}
    return {"R": _blind_block(q.get("R")), "C": _blind_block(q.get("C"))}


def _blind_scores(scores: dict | None) -> dict:
    """A phrasing/title/comment `scores` block may carry any of R/C/A."""
    s = scores or {}
    return {dim: _blind_block(s.get(dim)) for dim in s} or {}


def blind_node(node: dict) -> dict:
    """Rating-mode copy of a `nodes[]` record: text + structure kept, every
    rating aggregate and the comment thread removed."""
    out = dict(node)
    out["agreement"] = _blind_block(node.get("agreement"))
    out["quality"] = _blind_quality(node.get("quality"))
    out["heat"] = None
    out["comments"] = []
    out["comment_count"] = 0
    out["phrasings"] = [dict(p, scores=_blind_scores(p.get("scores")))
                        for p in node.get("phrasings", [])]
    out["titles"] = [dict(t, scores=_blind_scores(t.get("scores")))
                     for t in node.get("titles", [])]
    return out


def blind_edge(edge: dict) -> dict:
    """Rating-mode copy of a `ground_edges[]` record: inference/typing + endpoints
    kept, graded Agreement and the comment thread removed."""
    out = dict(edge)
    out["agreement"] = _blind_block(edge.get("agreement"))
    out["heat"] = None
    out["comments"] = []
    out["comment_count"] = 0
    return out


def _index_nodes(graph: dict) -> dict:
    return {n["id"]: n for n in graph["nodes"]}


def _resolve_id(items: list[dict], item_id) -> str | None:
    if item_id is None:
        return None
    for it in items:
        if it["id"] == item_id:
            return it["text"]
    return None


def primary_title_text(node: dict) -> str | None:
    return _resolve_id(node["titles"], node["primary_title"])


def primary_phrasing_text(node: dict) -> str | None:
    return _resolve_id(node["phrasings"], node["primary_phrasing"])


def node_display_text(node: dict) -> str | None:
    """Node's title, falling back to its primary phrasing -- used to resolve
    a typing's trunk-node reference to readable text (FORUMS-SPEC.md §3)."""
    return primary_title_text(node) or primary_phrasing_text(node)


def primary_typing_text(nodes_index: dict, edge: dict) -> str | None:
    """Resolve an edge's primary_typing id to its trunk-node title (falling
    back to phrasing) or its free-text label -- FORUMS-SPEC.md §3: "resolved
    to the trunk node's title or the label text"."""
    tyid = edge.get("primary_typing")
    if not tyid:
        return None
    for t in edge.get("typings", []):
        if t["id"] != tyid:
            continue
        if t.get("node"):
            n = nodes_index.get(t["node"])
            return node_display_text(n) if n else None
        return t.get("label")
    return None


def _augment_edge(nodes_index: dict, e: dict) -> dict:
    """Copy of a ground_edges record with the read-verb-only convenience
    fields FORUMS-SPEC.md §3 asks get-node/neighborhood to include: a
    comment_count and the primary typing resolved to display text."""
    out = dict(e)
    out["comment_count"] = len(e.get("comments", []))
    out["primary_typing_text"] = primary_typing_text(nodes_index, e)
    return out


def get_node(graph: dict, node_id: str, include_sealed: bool = False,
             rating_mode: bool = False) -> dict | None:
    nodes = _index_nodes(graph)
    node = nodes.get(node_id)
    if node is None:
        return None

    # Rating mode blinds the RAW records directly (not via mask_node/mask_edge):
    # it hides every graded cue regardless of sealed state, and blinding the raw
    # record also covers score dims mask_*'s sealed path doesn't touch (e.g. a
    # phrasing's v1.3 belonging-A). Reading mode keeps the existing sealed-mask.
    ground_edges = [e for e in graph["ground_edges"] if e["to"] == node_id]
    dependent_edges = [e for e in graph["ground_edges"] if e["from"] == node_id]
    if rating_mode:
        grounds = [blind_edge(_augment_edge(nodes, e)) for e in ground_edges]
        dependents = [blind_edge(_augment_edge(nodes, e)) for e in dependent_edges]
    else:
        grounds = [mask_edge(_augment_edge(nodes, e), include_sealed) for e in ground_edges]
        dependents = [mask_edge(_augment_edge(nodes, e), include_sealed) for e in dependent_edges]
    sets = [s for s in graph["antithesis_sets"] if any(m["node"] == node_id for m in s["members"])]

    node_out = dict(node)
    node_out["comment_count"] = len(node.get("comments", []))
    node_out = blind_node(node_out) if rating_mode else mask_node(node_out, include_sealed)

    return {
        "node": node_out,
        "grounds": grounds,        # edges where this node is supported BY `from`
        "dependents": dependents,  # edges where this node supports `to`
        "antithesis_sets": sets,
        "rating_mode": rating_mode,
    }


def neighborhood(graph: dict, node_id: str, depth: int = 1, include_sealed: bool = False,
                 rating_mode: bool = False) -> dict | None:
    nodes = _index_nodes(graph)
    if node_id not in nodes:
        return None

    edges = graph["ground_edges"]
    adjacency: dict[str, list[dict]] = {}
    for e in edges:
        adjacency.setdefault(e["from"], []).append(e)
        adjacency.setdefault(e["to"], []).append(e)

    visited = {node_id: 0}
    order = [node_id]
    q = deque([node_id])
    while q:
        cur = q.popleft()
        d = visited[cur]
        if d >= depth:
            continue
        for e in adjacency.get(cur, []):
            other = e["to"] if e["from"] == cur else e["from"]
            if other not in visited:
                visited[other] = d + 1
                order.append(other)
                q.append(other)

    node_ids = set(visited.keys())
    sub_nodes = [
        {
            "id": nid,
            "kind": nodes[nid]["kind"],
            "primary_title": nodes[nid]["primary_title"],
            "primary_title_text": primary_title_text(nodes[nid]),
            "primary_phrasing": nodes[nid]["primary_phrasing"],
            "primary_phrasing_text": primary_phrasing_text(nodes[nid]),
            "comment_count": 0 if rating_mode else len(nodes[nid].get("comments", [])),
            # ASSESSMENT-SPEC.md §6: "get-node/neighborhood outputs gain the
            # scores/agreement/quality fields" -- get-node already inherits
            # them via its plain `dict(node)` copy; neighborhood's sub_nodes
            # are hand-picked fields, so they need adding explicitly here.
            # Rating mode (§7) blinds the aggregates, same as get-node.
            "agreement": _blind_block(nodes[nid].get("agreement")) if rating_mode
            else _mask_block(nodes[nid].get("agreement"), include_sealed),
            "quality": _blind_quality(nodes[nid].get("quality")) if rating_mode
            else _mask_quality(nodes[nid].get("quality") or {}, include_sealed),
            "depth": visited[nid],
        }
        for nid in order
    ]
    sub_edges = [
        {
            "id": e["id"], "from": e["from"], "to": e["to"], "group": e["group"], "strength": e["strength"],
            "comment_count": 0 if rating_mode else len(e.get("comments", [])),
            "primary_typing": e.get("primary_typing"),
            "primary_typing_text": primary_typing_text(nodes, e),
        }
        for e in edges
        if e["from"] in node_ids and e["to"] in node_ids
    ]

    return {"focus": node_id, "depth": depth, "nodes": sub_nodes, "edges": sub_edges,
            "rating_mode": rating_mode}


def list_comments(graph: dict, target_id: str) -> dict | None:
    """The full comment thread for a node or edge target (FORUMS-SPEC.md
    §3). Returns None if `target_id` isn't a known node or edge. The
    returned "comments" list is flat (thread structure recoverable via
    "parent", per §2) and ordered by seq; see `thread_comments()` for the
    ranked/nested view used by text-mode rendering."""
    nodes = _index_nodes(graph)
    if target_id in nodes:
        return {"target": target_id, "target_kind": "node", "comments": list(nodes[target_id].get("comments", []))}
    edges = {e["id"]: e for e in graph["ground_edges"]}
    if target_id in edges:
        return {"target": target_id, "target_kind": "edge", "comments": list(edges[target_id].get("comments", []))}
    return None


def _comment_seq(c: dict) -> int:
    # Comment ids are global and monotonically assigned ("c001", "c002", ...),
    # so the numeric suffix is a stable, cheap proxy for "seq asc" ordering
    # without having to carry a redundant seq field on every comment record.
    try:
        return int(c["id"][1:])
    except (ValueError, IndexError):
        return 0


def thread_comments(comments: list[dict]) -> list[dict]:
    """Nest a flat comment list into a reply tree, siblings at every level
    ranked by (agrees desc, seq asc) -- FORUMS-SPEC.md §3's rendering rule
    for `list-comments`' default text mode. Each returned node is the
    original comment dict plus a "children" list (same shape, recursively)."""
    by_parent: dict = {}
    for c in comments:
        by_parent.setdefault(c.get("parent"), []).append(c)

    def rank(siblings):
        return sorted(siblings, key=lambda c: (-c["agrees"], _comment_seq(c)))

    def build(parent_id):
        return [dict(c, children=build(c["id"])) for c in rank(by_parent.get(parent_id, []))]

    return build(None)


def search(graph: dict, query: str, include_sealed: bool = False) -> list[dict]:
    # PHASE2-SPEC.md §8 names `search` among the read verbs that must respect
    # `--include-sealed` -- accepted here for CLI/API symmetry, but search
    # hits never carried an aggregate mean to begin with (they're phrasing/
    # title TEXT matches), so there is nothing to mask; the parameter is a
    # documented no-op for this verb.
    del include_sealed
    q = (query or "").strip().lower()
    if not q:
        return []
    hits = []
    for n in graph["nodes"]:
        for p in n["phrasings"]:
            if q in p["text"].lower():
                hits.append({"node": n["id"], "field": "phrasing", "id": p["id"], "text": p["text"]})
        for t in n["titles"]:
            if q in t["text"].lower():
                hits.append({"node": n["id"], "field": "title", "id": t["id"], "text": t["text"]})
    return hits


def list_sets(graph: dict, include_sealed: bool = False) -> list[dict]:
    # PHASE2-SPEC.md §8 names `list-sets` too; antithesis membership carries
    # structural `belonging`, not a rated aggregate, so (as with `search`
    # above) there is currently nothing here to mask -- accepted for
    # interface symmetry / future-proofing.
    del include_sealed
    return graph["antithesis_sets"]


def _load_source_citations(sources_root) -> dict[str, str]:
    """Read every `<sources_root>/<pack>/index.json` and return a flat
    ref_id -> citation map. Missing/unreadable packs are skipped silently
    (F3: a --source is allowed to be free text with no matching pack entry
    at all, so an absent or empty pack is not an error)."""
    citations: dict[str, str] = {}
    if not sources_root:
        return citations
    root = Path(sources_root)
    if not root.is_dir():
        return citations
    for pack_dir in sorted(p for p in root.iterdir() if p.is_dir()):
        index_path = pack_dir / "index.json"
        if not index_path.is_file():
            continue
        try:
            with index_path.open("r", encoding="utf-8") as f:
                entries = json.load(f)
        except (json.JSONDecodeError, OSError):
            continue
        for entry in entries:
            ref_id = entry.get("ref_id")
            if ref_id:
                citations[ref_id] = entry.get("citation", ref_id)
    return citations


def list_studies(graph: dict, sources_root=None) -> list[dict]:
    """Group Evidence nodes by `source_ref` (BUILD-SPEC §2 F2 fix).

    "Evidence" covers both the current `evidence` kind and the legacy
    `external_anchor` name (read alias) -- see `fold.is_evidence_kind`.

    Each distinct source becomes one record: the source id, its citation
    (resolved from a `sources/<pack>/index.json` ref_id when one matches,
    else the raw source string itself), and the sorted list of node ids
    citing it. Lets an author find an existing study id and see every claim
    already attached to it before adding another `external_anchor` under a
    fresh, fragmenting source string."""
    citations = _load_source_citations(sources_root)
    groups: dict[str, list[str]] = {}
    for n in graph["nodes"]:
        if not is_evidence_kind(n["kind"]):
            continue
        src = n.get("source_ref")
        if not src:
            continue
        groups.setdefault(src, []).append(n["id"])
    return [
        {"source": src, "citation": citations.get(src, src), "nodes": sorted(groups[src])}
        for src in sorted(groups)
    ]


def stats(graph: dict, data_dir) -> dict:
    events = store.read_events(data_dir)
    audit = store.read_audit(data_dir)

    node_ids = {n["id"] for n in graph["nodes"]}
    touched = set()
    for e in graph["ground_edges"]:
        touched.add(e["from"])
        touched.add(e["to"])
    orphan_nodes = sorted(node_ids - touched)

    agree_events = sum(1 for e in events if e.get("verb") == "agree")

    def audit_count(status: str, tag: str) -> int:
        return sum(1 for r in audit if r["status"] == status and r["tag"] == tag)

    return {
        "counts": {
            "nodes": len(graph["nodes"]),
            "ground_edges": len(graph["ground_edges"]),
            "conjunction_groups": len(graph["conjunction_groups"]),
            "antithesis_sets": len(graph["antithesis_sets"]),
            "frictions": len(graph["frictions"]),
            "agree_events": agree_events,
            "total_events": len(events),
        },
        "health": {
            "orphan_nodes": orphan_nodes,
            "self_agree_rejected": audit_count("rejected", "self_agree"),
            "duplicate_agree_rejected": audit_count("rejected", "duplicate_agree"),
            "duplicate_text_warnings": audit_count("warning", "duplicate_text"),
            "over_cap_warnings": audit_count("warning", "over_cap"),
        },
        # PHASE2-SPEC.md §3: "stats reports site medians" -- carried straight
        # through from graph.json's meta (computed once, in the fold, from
        # the same heat values `state`/"cold" comparisons used).
        "heat_medians": graph.get("meta", {}).get("heat_medians", {"content": None, "rating": None}),
    }


# --- SPEC-evidence-argument-ought-ghosts.md §4 + §3.3: coherence lint -------
#
# A cheap, DETERMINISTIC structural pass over graph.json (no ratings, no fold
# state) that flags the layering/hygiene problems the spec names: star/hub
# topology (agents attaching every claim to the salient hub instead of its
# proximate support), orphans, malformed antithesis sets, question-shaped
# nodes, disguised "not-X" negations, and redundant direct-vs-layered paths
# (§3.3). Advisory only -- it proposes review targets, it never mutates.

_NEG_PREFIXES = ("no ", "not ", "there is no", "there's no", "neither ", "none of ")


def _primary_text(node: dict) -> str:
    pid = node.get("primary_phrasing")
    for p in node.get("phrasings", []):
        if p["id"] == pid:
            return p["text"]
    ps = node.get("phrasings")
    return ps[0]["text"] if ps else ""


def _reachable_without(adj: dict, src: str, dst: str, banned_edge, max_depth: int = 8) -> bool:
    """Is `dst` reachable from `src` along support edges WITHOUT using the single
    direct edge `banned_edge` (a (from,to) pair), within max_depth hops? Used to
    detect a shortcut edge that a longer layered path already covers (§3.3)."""
    from collections import deque
    seen = {src}
    dq = deque([(src, 0)])
    while dq:
        node, d = dq.popleft()
        if d >= max_depth:
            continue
        for nxt in adj.get(node, ()):
            if (node, nxt) == banned_edge:
                continue
            if nxt == dst:
                return True
            if nxt not in seen:
                seen.add(nxt)
                dq.append((nxt, d + 1))
    return False


def coherence_lint(graph: dict, hub_threshold: int = 8, max_redundant: int = 40) -> dict:
    """Structural-coherence findings (SPEC §4 + §3.3). Every category is a list
    of small dicts so callers can render or count by kind. `hub_threshold` = the
    in-degree (number of DIRECT grounds) at or above which a node is flagged as a
    star/hub (the measured symptom: top answers accruing 11-19 direct grounds)."""
    # A demoted (§3.2 ghosted) node/edge/set is out of the living graph, so the
    # lint ignores it -- demoting a flagged item is a valid way to clear it.
    nodes = {n["id"]: n for n in graph["nodes"] if not n.get("demoted")}
    edges = [e for e in graph["ground_edges"] if not e.get("demoted")]
    live_sets = [s for s in graph["antithesis_sets"] if not s.get("demoted")]

    in_deg: dict[str, int] = {nid: 0 for nid in nodes}
    adj: dict[str, list] = {nid: [] for nid in nodes}   # from -> [to] (support flow)
    for e in edges:
        if e["to"] in in_deg:
            in_deg[e["to"]] += 1
        if e["from"] in adj:
            adj[e["from"]].append(e["to"])

    touched = set()
    for e in edges:
        touched.add(e["from"])
        touched.add(e["to"])
    in_sets = {m["node"] for s in live_sets for m in s["members"]}

    hubs = sorted(
        ({"node": nid, "direct_grounds": in_deg[nid]} for nid in nodes if in_deg[nid] >= hub_threshold),
        key=lambda d: (-d["direct_grounds"], d["node"]),
    )
    orphans = sorted(nid for nid in nodes if nid not in touched and nid not in in_sets)
    malformed_sets = [
        {"set": s["id"], "members": [m["node"] for m in s["members"]], "size": len(s["members"])}
        for s in live_sets if len(s["members"]) < 2
    ]
    question_nodes, negation_nodes = [], []
    for nid, n in nodes.items():
        t = _primary_text(n).strip()
        if t.endswith("?"):
            question_nodes.append({"node": nid, "text": t[:80]})
        norm = t.lower()
        if any(norm.startswith(p) for p in _NEG_PREFIXES):
            negation_nodes.append({"node": nid, "text": t[:80]})

    # §3.3 redundant paths: a direct edge whose endpoints are ALSO joined by a
    # longer (layered) support path -> the shortcut competes with the layering.
    redundant = []
    for e in edges:
        if len(redundant) >= max_redundant:
            break
        if _reachable_without(adj, e["from"], e["to"], (e["from"], e["to"])):
            redundant.append({"edge": e["id"], "from": e["from"], "to": e["to"]})

    return {
        "hub_nodes": hubs,
        "orphan_nodes": orphans,
        "malformed_antithesis_sets": malformed_sets,
        "question_shaped_nodes": question_nodes,
        "negation_framed_nodes": negation_nodes,
        "redundant_paths": redundant,
        "summary": {
            "hub_nodes": len(hubs),
            "orphan_nodes": len(orphans),
            "malformed_antithesis_sets": len(malformed_sets),
            "question_shaped_nodes": len(question_nodes),
            "negation_framed_nodes": len(negation_nodes),
            "redundant_paths": len(redundant),
        },
    }
