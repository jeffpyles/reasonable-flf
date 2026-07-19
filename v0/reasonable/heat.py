"""Event-time heat diffusion (PHASE2-SPEC.md §3, amended by p2.1 -- heat is
measured in SITE-WIDE EVENTS, not wall-clock time, so a fast swarm run can
still reach "cold" and the fold stays deterministic: no `datetime.now()`
anywhere in this module, only `seq` distances already present in the log).

Two independent ledgers, same mechanics: **content** heat (authored-content
events) and **rating** heat (`rate` events). For every heat-bearing event:

1. It injects a total of 1.0 "unit" of heat, split evenly across its target
   node(s) -- most verbs touch exactly one node (full 1.0); edge-shaped
   events (`draw_ground`, an `agree`/`rate`/`comment`/`propose_typing` that
   resolves to an edge) touch both endpoints and so split 0.5/0.5 (an
   explicit, spec-sanctioned choice for edge ratings, generalized here to
   every edge-shaped injection for consistency -- see PHASE2-SPEC.md §3).
   `flag_friction` with N `--refs` splits 1/N across the referenced nodes;
   with no refs, nothing is injected (there is no node to heat).
2. 15% of each node's share (`heat_diffuse`, configurable) is deposited,
   split evenly, on that node's DIRECTLY connected neighbors -- "connected"
   per the FINAL graph state at fold time (a documented simplification per
   PHASE2-SPEC.md §3's explicit allowance: incremental, event-time-accurate
   adjacency would require re-deriving the graph at every event, which is
   unnecessary complexity for a metric whose whole purpose is a coarse,
   site-relative churn signal). A node with no neighbors simply keeps 100%
   at itself for that event's diffusable share (nowhere to send it).
3. The whole injected amount (direct share + diffused share) decays
   exponentially with half-life `heat_half_life` SITE-WIDE EVENTS: an event
   at seq `s`, viewed from the log's tip `S`, contributes
   `0.5 ** ((S - s) / heat_half_life)` of its original weight. "Now" for any
   rebuild is the log's own tip seq, never wall-clock -- so the same log
   always yields the same heat, byte-for-byte (BUILD-SPEC.md §3).

Target resolution reuses the same target-string grammar as `agree`/`rate`
(`set:`, `title:`, `phrasing:`, `comment:`, `typing:`, `group:`, bare node/
edge id) so a heat-bearing event's node(s) are derived the same way the rest
of the fold already understands those strings -- no new grammar invented.
"""
from __future__ import annotations

# Verbs that inject CONTENT heat (authored material, structural consensus,
# and forum activity) -- PHASE2-SPEC.md §3's explicit list.
CONTENT_VERBS = {
    "create_node", "draw_ground", "add_antithesis", "propose_title",
    "propose_phrasing", "comment", "propose_typing", "flag_friction", "agree",
}
# Verbs that inject RATING heat -- graded assessment activity.
RATING_VERBS = {"rate"}

DEFAULT_HALF_LIFE = 300.0
DEFAULT_DIFFUSE = 0.15


def _edge_split(state: dict, eid: str) -> list[tuple[str, float]]:
    e = state["edges"].get(eid)
    if e is None:
        return []
    return [(e["from"], 0.5), (e["to"], 0.5)]


def _resolve_generic_target(state: dict, target: str) -> list[tuple[str, float]]:
    """Resolve an `agree`/`rate` `--target` string to (node_id, fraction)
    pairs -- shared by both verbs' heat injection since they use the same
    target grammar (fold.resolve_target / fold.resolve_rate_target)."""
    nodes = state["nodes"]
    if target.startswith("set:"):
        _, _sid, node_id = target.split(":", 2)
        return [(node_id, 1.0)] if node_id in nodes else []
    if target.startswith("title:"):
        _, node_id, _tid = target.split(":", 2)
        return [(node_id, 1.0)] if node_id in nodes else []
    if target.startswith("phrasing:"):
        _, node_id, _pid = target.split(":", 2)
        return [(node_id, 1.0)] if node_id in nodes else []
    if target.startswith("comment:"):
        cid = target.split(":", 1)[1]
        c = state["comments"].get(cid)
        if c is None:
            return []
        t = c["target"]
        return [(t, 1.0)] if t in nodes else _edge_split(state, t)
    if target.startswith("typing:"):
        _, eid, _tyid = target.split(":", 2)
        return _edge_split(state, eid)
    if target.startswith("group:"):
        gid = target.split(":", 1)[1]
        g = state["groups"].get(gid)
        return [(g["to"], 1.0)] if g else []
    # bare id: a node or an edge.
    if target in nodes:
        return [(target, 1.0)]
    return _edge_split(state, target)


def _targets_for_event(state: dict, verb: str, payload: dict) -> tuple[str | None, list[tuple[str, float]]]:
    """Return (ledger, [(node_id, fraction), ...]) for one event. `ledger` is
    None (and the list empty) for any verb that doesn't inject heat."""
    if verb == "create_node":
        return "content", [(payload["id"], 1.0)]
    if verb == "draw_ground":
        return "content", [(payload["from"], 0.5), (payload["to"], 0.5)]
    if verb == "add_antithesis":
        return "content", [(payload["node"], 1.0)]
    if verb == "propose_title":
        return "content", [(payload["node"], 1.0)]
    if verb == "propose_phrasing":
        return "content", [(payload["node"], 1.0)]
    if verb == "comment":
        t = payload["target"]
        if t in state["nodes"]:
            return "content", [(t, 1.0)]
        return "content", _edge_split(state, t)
    if verb == "propose_typing":
        return "content", _edge_split(state, payload["edge"])
    if verb == "flag_friction":
        refs = payload.get("refs") or []
        if not refs:
            return "content", []
        frac = 1.0 / len(refs)
        return "content", [(r, frac) for r in refs if r in state["nodes"]]
    if verb == "agree":
        return "content", _resolve_generic_target(state, payload["target"])
    if verb == "rate":
        return "rating", _resolve_generic_target(state, payload["target"])
    return None, []


def _adjacency(state: dict) -> dict[str, list[str]]:
    """node_id -> [directly connected node_id, ...] (deduplicated, insertion
    order -- deliberately a dict-as-ordered-set, never a bare `set()`, so
    iteration order can't vary with PYTHONHASHSEED, per the determinism
    discipline already established in assess.py)."""
    adj: dict[str, dict[str, None]] = {}
    for eid in state["edge_order"]:
        e = state["edges"][eid]
        a, b = e["from"], e["to"]
        adj.setdefault(a, {}).setdefault(b, None)
        adj.setdefault(b, {}).setdefault(a, None)
    return {k: list(v.keys()) for k, v in adj.items()}


def compute_heat(state: dict, half_life: float = DEFAULT_HALF_LIFE,
                  diffuse: float = DEFAULT_DIFFUSE) -> dict[str, dict[str, float]]:
    """Compute {"content": {node_id: heat}, "rating": {node_id: heat}} from
    `state["events"]` (fold() stashes the raw, seq-ordered event list there
    -- see fold.py) and the FINAL folded adjacency/target structures.

    Values are NOT rounded here (rounding to 6 decimals for byte-stability
    is a `graph.json`-projection concern, done once at output time in
    lifecycle.py) so repeated diffusion/decay math stays full-precision
    until the very last step.
    """
    events = state.get("events") or []
    content: dict[str, float] = {}
    rating: dict[str, float] = {}
    if not events:
        return {"content": content, "rating": rating}

    tip = max(e["seq"] for e in events if e.get("seq") is not None)
    adj = _adjacency(state)

    for e in events:
        verb = e.get("verb")
        if verb not in CONTENT_VERBS and verb not in RATING_VERBS:
            continue
        seq = e.get("seq")
        if seq is None:
            continue
        payload = e.get("payload") or {}
        ledger, targets = _targets_for_event(state, verb, payload)
        if not targets:
            continue
        bucket = content if ledger == "content" else rating
        decay = 0.5 ** ((tip - seq) / half_life)
        for node_id, frac in targets:
            neighbors = adj.get(node_id, [])
            if neighbors:
                direct = frac * (1.0 - diffuse) * decay
                share = frac * diffuse * decay / len(neighbors)
                for nb in neighbors:
                    bucket[nb] = bucket.get(nb, 0.0) + share
            else:
                # Nowhere to diffuse to -- the would-be-diffused share stays
                # with the originating node instead of being lost.
                direct = frac * decay
            bucket[node_id] = bucket.get(node_id, 0.0) + direct

    return {"content": content, "rating": rating}
