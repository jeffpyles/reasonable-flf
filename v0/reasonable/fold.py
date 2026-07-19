"""Fold the append-only events.jsonl log into the derived graph.json snapshot.

This is the pure, deterministic heart of the data layer (BUILD-SPEC.md §1, §3):
same list of events -> same output, every time, with no wall-clock reads and
no reliance on anything but the events themselves. `fold()` builds a rich
*internal* state (dict-keyed for O(1) lookups, used by validation and by CLI
id-assignment); `to_graph_json()` projects that internal state down to the
exact FROZEN public schema described in BUILD-SPEC.md §1b.

Unknown / non-mutating verbs (e.g. the "rejected" audit marker some CLIs
might choose to interleave) are ignored by fold() -- only verbs listed in
BUILD-SPEC.md §2 mutate state. This CLI's own store never writes "rejected"
events into events.jsonl (see reasonable/store.py's audit log for that), but
fold() stays defensive so it tolerates hand-built test logs and any future
housekeeping verbs without raising.
"""
from __future__ import annotations

from . import assess, lifecycle
from .errors import TargetNotFound

DEFAULT_QUESTION = "Are eggs good for you?"

# --- SPEC-evidence-argument-ought-ghosts.md §1: node-kind grammar -----------
# The three boundary roles of a node. Evidence anchors reasoning to the world
# at the start (facts in); Argument (`claim`) is internal reasoning; Ought
# anchors it at the end (actions/values out). `external_anchor` is the
# pre-Evidence name for Evidence, kept as a permanent READ ALIAS so logs
# written before the rename still fold byte-identically -- fold never rewrites
# a stored kind, so old graph.json snapshots reproduce exactly.
CLAIM_KIND = "claim"
EVIDENCE_KIND = "evidence"
OUGHT_KIND = "ought"
LEGACY_EVIDENCE_KIND = "external_anchor"
EVIDENCE_KINDS = frozenset({EVIDENCE_KIND, LEGACY_EVIDENCE_KIND})
VALID_NODE_KINDS = frozenset({CLAIM_KIND, EVIDENCE_KIND, OUGHT_KIND, LEGACY_EVIDENCE_KIND})


def is_evidence_kind(kind: str | None) -> bool:
    """True for Evidence nodes under either the current or legacy name."""
    return kind in EVIDENCE_KINDS


def is_ought_kind(kind: str | None) -> bool:
    return kind == OUGHT_KIND


_WRITE_VERBS = {
    "create_node",
    "draw_ground",
    "add_antithesis",
    "agree",
    "propose_title",
    "propose_phrasing",
    "flag_friction",
    # FORUMS-SPEC.md §1 additions -- additive only, nothing above changes.
    "comment",
    "propose_typing",
    # ASSESSMENT-SPEC.md §2 addition -- graded rating, a layer parallel to
    # (never replacing) the structural agree/strength consensus above.
    "rate",
    # PHASE2-SPEC.md §4 addition -- increments a target's era, returns it to
    # sealed. Never mutates ratings themselves (those stay in the log,
    # keyed by the era they were cast in -- see `ratings_all` below).
    "reopen",
    # SPEC-evidence-argument-ought-ghosts.md §3.2: demote a node/edge toward
    # ghost status WITHOUT deleting it (the record of "we checked this, it's
    # wrong/superseded" is a primary asset). Folds to a conditional `demoted`
    # marker on the target's block -- absent for every existing graph, so they
    # stay byte-identical. `--restore` un-demotes (latest event wins), so a
    # ghost can be resurrected (§3.1 resurrection).
    "supersede",
    # SPEC-evidence-argument-ought-ghosts.md §2.2: `poll_vote` casts Yes/No/
    # decline on a categorical poll and folds to a per-(node,question) vote
    # record. `flag_type` is DELIBERATELY absent -- it stays a pure, non-
    # folding, uncounted marker (opening a poll is gated at write time by
    # ops.cmd_poll_vote against the log, so no folded flag record is needed).
    # Keeping flag_type non-folding means the three existing graphs -- eggs
    # included, which carries flag_type markers but no votes -- rebuild
    # byte-identically. A poll exists only once it has a vote; resolution is
    # reputation-weighted (reasonable/typepoll.py).
    "poll_vote",
}


def new_state() -> dict:
    """An empty fold state (the identity element for `fold`)."""
    return {
        "nodes": {},
        "node_order": [],
        "edges": {},
        "edge_order": [],
        "groups": {},
        "group_order": [],
        "sets": {},
        "set_order": [],
        "frictions": [],
        # FORUMS-SPEC.md §2: comments are global (id space shared across all
        # node/edge targets) but each carries its own `target`, so the flat
        # per-node/per-edge lists in to_graph_json() are just filters over
        # this one ordered collection -- insertion order here IS seq order
        # (fold() is always called with seq-sorted events), which is what
        # "order by seq" in the spec means.
        "comments": {},
        "comment_order": [],
        # ASSESSMENT-SPEC.md §2: target -> dim -> agent -> value (float or the
        # literal "abstain"). Keyed by the CURRENT (latest-by-seq) value only
        # -- a later `rate` by the same agent on the same (target, dim)
        # naturally overwrites the earlier dict entry as events replay in seq
        # order, which is exactly the "re-rate supersedes" / "abstain
        # supersedes" rule in §2, with no extra bookkeeping needed.
        "ratings": {},
        # PHASE2-SPEC.md §4 (eras) / §5 (blocs): the full, era-and-bloc-aware
        # history of every rating ever cast: target -> dim -> era -> agent ->
        # {"value", "seq", "bloc"}. Keyed by era (not just target/dim/agent)
        # so a re-rate SUPERSEDES only within the same era (the era-isolation
        # rule: "ratings from a prior era do NOT count in the new era" --
        # this dict is where that isolation actually lives; `ratings` above
        # stays a plain target -> dim -> agent -> value view, derived from
        # this one AFTER the replay loop (see fold()'s tail), filtered to
        # each target's FINAL era, so assess.py's fixed-point loop keeps
        # consuming exactly the shape it always has -- era isolation is
        # invisible to it.
        "ratings_all": {},
        # PHASE2-SPEC.md §4: target -> current era (int, starts at 1 the
        # first time it's referenced; absent == 1, so a target nobody has
        # ever `reopen`ed is implicitly era 1 without needing an entry here).
        "eras": {},
        # SPEC-evidence-argument-ought-ghosts.md §3.2: target id -> demotion
        # record {reason, agent, seq} for nodes/edges superseded toward ghost
        # status. `restore` pops the entry (latest event wins). Empty for every
        # graph without a `supersede` event, so those stay byte-identical.
        "demotions": {},
        # SPEC-evidence-argument-ought-ghosts.md §2.2: categorical-consensus
        # polls, keyed "<node>|<question>" (question e.g. "type:ought"). Created
        # lazily by the first `poll_vote` (`flag_type` stays a non-folding
        # marker), so a flagged-but-unvoted node has NO poll -> emits nothing to
        # graph.json -> existing graphs stay byte-identical. Resolution
        # (reputation-weighted) is the assessment layer's job (typepoll.py).
        "polls": {},
        "last_ts": None,
        "event_count": 0,
    }


def resolve_target(state: dict, target: str):
    """Resolve an `agree --target` string against folded state.

    Returns (kind, obj) where obj is the *internal* mutable record (has an
    "agents" list and either "author" or "_author"). Raises TargetNotFound
    if any part of the reference doesn't exist.
    """
    if target.startswith("set:"):
        parts = target.split(":", 2)
        if len(parts) != 3:
            raise TargetNotFound(f"malformed set target: {target!r}")
        _, sid, node_id = parts
        s = state["sets"].get(sid)
        if s is None:
            raise TargetNotFound(f"unknown antithesis set: {sid}")
        for m in s["members"]:
            if m["node"] == node_id:
                return "set_member", m
        raise TargetNotFound(f"node {node_id} is not a member of set {sid}")

    if target.startswith("title:"):
        parts = target.split(":", 2)
        if len(parts) != 3:
            raise TargetNotFound(f"malformed title target: {target!r}")
        _, node_id, tid = parts
        n = state["nodes"].get(node_id)
        if n is None:
            raise TargetNotFound(f"unknown node: {node_id}")
        for t in n["titles"]:
            if t["id"] == tid:
                return "title", t
        raise TargetNotFound(f"unknown title {tid} on node {node_id}")

    if target.startswith("phrasing:"):
        parts = target.split(":", 2)
        if len(parts) != 3:
            raise TargetNotFound(f"malformed phrasing target: {target!r}")
        _, node_id, pid = parts
        n = state["nodes"].get(node_id)
        if n is None:
            raise TargetNotFound(f"unknown node: {node_id}")
        for p in n["phrasings"]:
            if p["id"] == pid:
                return "phrasing", p
        raise TargetNotFound(f"unknown phrasing {pid} on node {node_id}")

    # FORUMS-SPEC.md §1: agree targets extended to comments and edge typings.
    # Both resolve to an internal record carrying "author"/"agents", so the
    # existing self-agree / duplicate-agree logic in validate.validate_agree
    # applies unchanged -- no new machinery, just two new lookups.
    if target.startswith("comment:"):
        parts = target.split(":", 1)
        if len(parts) != 2 or not parts[1]:
            raise TargetNotFound(f"malformed comment target: {target!r}")
        cid = parts[1]
        c = state["comments"].get(cid)
        if c is None:
            raise TargetNotFound(f"unknown comment: {cid}")
        return "comment", c

    if target.startswith("typing:"):
        parts = target.split(":", 2)
        if len(parts) != 3:
            raise TargetNotFound(f"malformed typing target: {target!r}")
        _, edge_id, tyid = parts
        e = state["edges"].get(edge_id)
        if e is None:
            raise TargetNotFound(f"unknown edge: {edge_id}")
        for t in e["typings"]:
            if t["id"] == tyid:
                return "typing", t
        raise TargetNotFound(f"unknown typing {tyid} on edge {edge_id}")

    # otherwise: a bare ground-edge id
    e = state["edges"].get(target)
    if e is None:
        raise TargetNotFound(f"unknown agree target: {target}")
    return "edge", e


def resolve_rate_target(state: dict, target: str):
    """Resolve a `rate --target` string (ASSESSMENT-SPEC.md §2, amended --
    see ASSESSMENT-SPEC.md's Amendments section).

    A bare id is either a NODE id (dim A) or, since the graded-edge-Agreement
    amendment, an EDGE id (also dim A -- "how strongly does the ground
    actually support the dependent"). Node ids are checked first, matching
    `resolve_target`'s (used by `agree`) opposite convention where a bare id
    defaults to an edge; the two id spaces never collide (nNNN vs eNNN, see
    store.next_node_id/next_edge_id) so the check order has no practical
    effect, it's just which lookup happens first. Returns (kind, obj,
    valid_dims) where `obj` carries an "author"/"_author" field (for the
    self-rate check) and `valid_dims` is the set of dims legal for that
    target kind ({"R","C"} for phrasing/comment, {"A"} for node/edge).
    Raises TargetNotFound if any part of the reference doesn't exist.
    """
    if target.startswith("phrasing:"):
        parts = target.split(":", 2)
        if len(parts) != 3:
            raise TargetNotFound(f"malformed phrasing target: {target!r}")
        _, node_id, pid = parts
        n = state["nodes"].get(node_id)
        if n is None:
            raise TargetNotFound(f"unknown node: {node_id}")
        for p in n["phrasings"]:
            if p["id"] == pid:
                return "phrasing", p, {"R", "C"}
        raise TargetNotFound(f"unknown phrasing {pid} on node {node_id}")

    if target.startswith("comment:"):
        parts = target.split(":", 1)
        if len(parts) != 2 or not parts[1]:
            raise TargetNotFound(f"malformed comment target: {target!r}")
        cid = parts[1]
        c = state["comments"].get(cid)
        if c is None:
            raise TargetNotFound(f"unknown comment: {cid}")
        return "comment", c, {"R", "C"}

    # PHASE2-SPEC.md §7 (f16 closure): `group:<gid>` rates the conjunction
    # group's joint inference ("if ALL members were so..."), dim A only. The
    # group's record carries an "author" (the agent whose `draw-ground
    # --group new` first created it, set in fold()'s draw_ground handling)
    # so the self-rate check in validate.validate_rate applies unchanged.
    if target.startswith("group:"):
        parts = target.split(":", 1)
        if len(parts) != 2 or not parts[1]:
            raise TargetNotFound(f"malformed group target: {target!r}")
        gid = parts[1]
        g = state["groups"].get(gid)
        if g is None:
            raise TargetNotFound(f"unknown conjunction group: {gid}")
        return "group", g, {"A"}

    # otherwise: a bare id -- a node (dim A), or (amendment) an edge (also
    # dim A: graded Agreement-as-inference-strength, parallel to the
    # structural agree/strength consensus, never replacing it).
    n = state["nodes"].get(target)
    if n is not None:
        return "node", n, {"A"}
    e = state["edges"].get(target)
    if e is not None:
        return "edge", e, {"A"}
    raise TargetNotFound(f"unknown rate target: {target}")


def fold(events: list[dict]) -> dict:
    """Replay `events` (already ordered by seq) into internal state."""
    state = new_state()
    # PHASE2-SPEC.md §3 (heat): heat.compute_heat() needs the raw, seq-
    # ordered event list alongside the final folded structures (to resolve
    # each event's target node(s) against the FINAL graph -- see heat.py's
    # docstring for why that's an intentional, documented simplification).
    # Stashing it on `state` keeps `fold()`'s and `to_graph_json()`'s
    # existing call signatures unchanged everywhere else in the codebase
    # (tests included) -- no new required parameter to thread through.
    state["events"] = list(events)
    nodes = state["nodes"]
    edges = state["edges"]
    groups = state["groups"]
    sets_ = state["sets"]
    comments = state["comments"]
    ratings_all = state["ratings_all"]
    eras = state["eras"]

    for ev in events:
        verb = ev.get("verb")
        if verb not in _WRITE_VERBS:
            # Non-mutating / unknown verb (e.g. an audit marker). Ignore.
            continue

        payload = ev.get("payload") or {}
        agent = ev.get("agent")
        seq = ev.get("seq")
        ts = ev.get("ts")

        if verb == "create_node":
            nid = payload["id"]
            node = {
                "id": nid,
                "kind": payload.get("kind", "claim"),
                "phrasings": [{
                    "id": "p0",
                    "text": payload["text"],
                    "agrees": 0,
                    "agents": [],
                    "_author": agent,
                }],
                "titles": [],
                "source_ref": payload.get("source"),
                "author": agent,
                "created_seq": seq,
            }
            if payload.get("title"):
                node["titles"].append({
                    "id": "t0",
                    "text": payload["title"],
                    "agrees": 0,
                    "agents": [],
                    "_author": agent,
                })
            nodes[nid] = node
            state["node_order"].append(nid)

        elif verb == "draw_ground":
            eid = payload["id"]
            edge = {
                "id": eid,
                "from": payload["from"],
                "to": payload["to"],
                "group": payload.get("group"),
                "agrees": 0,
                "agents": [],
                "author": agent,
                "created_seq": seq,
                # FORUMS-SPEC.md §2: every edge gains a typings list (proposed
                # answers to "what inference is this edge making?").
                "typings": [],
            }
            edges[eid] = edge
            state["edge_order"].append(eid)
            gid = payload.get("group")
            if gid:
                g = groups.get(gid)
                if g is None:
                    # PHASE2-SPEC.md §7: "the group's creator counts as
                    # author" -- the agent whose `draw-ground --group new`
                    # first instantiates `gid` is that creator; every
                    # subsequent `--group <gid>` join only appends a member,
                    # it never changes authorship.
                    g = {"id": gid, "to": payload["to"], "members": [], "author": agent}
                    groups[gid] = g
                    state["group_order"].append(gid)
                g["members"].append(payload["from"])

        elif verb == "add_antithesis":
            sid = payload["set"]
            node_id = payload["node"]
            s = sets_.get(sid)
            if s is None:
                s = {"id": sid, "members": []}
                sets_[sid] = s
                state["set_order"].append(sid)
            s["members"].append({
                "node": node_id,
                "agrees": 0,
                "agents": [],
                "author": agent,
            })

        elif verb == "propose_title":
            node = nodes[payload["node"]]
            node["titles"].append({
                "id": payload["id"],
                "text": payload["text"],
                "agrees": 0,
                "agents": [],
                "_author": agent,
            })

        elif verb == "propose_phrasing":
            node = nodes[payload["node"]]
            node["phrasings"].append({
                "id": payload["id"],
                "text": payload["text"],
                "agrees": 0,
                "agents": [],
                "_author": agent,
            })

        elif verb == "agree":
            _kind, obj = resolve_target(state, payload["target"])
            obj["agents"].append(agent)
            obj["agrees"] = len(obj["agents"])

        elif verb == "flag_friction":
            state["frictions"].append({
                "id": payload["id"],
                "agent": agent,
                "ts": ts,
                "refs": list(payload.get("refs", [])),
                "text": payload["text"],
            })

        elif verb == "comment":
            # FORUMS-SPEC.md §1/§2: `target` here is always the already-
            # resolved node/edge id (a reply's --reply-to is resolved to its
            # parent's target at write time, in ops.cmd_comment, so fold()
            # never has to walk the parent chain). "author" duplicates
            # "agent" so validate_agree's generic
            # `obj.get("author", obj.get("_author"))` self-agree check works
            # unchanged on comment records too.
            cid = payload["id"]
            comments[cid] = {
                "id": cid,
                "target": payload["target"],
                "parent": payload.get("parent"),
                "agent": agent,
                "author": agent,
                "ts": ts,
                "text": payload["text"],
                "agrees": 0,
                "agents": [],
            }
            state["comment_order"].append(cid)

        elif verb == "propose_typing":
            edge = edges[payload["edge"]]
            edge["typings"].append({
                "id": payload["id"],
                "node": payload.get("node"),
                "label": payload.get("label"),
                "agrees": 0,
                "agents": [],
                "author": agent,
            })

        elif verb == "rate":
            # ASSESSMENT-SPEC.md §2, extended by PHASE2-SPEC.md §4 (eras) and
            # §5 (blocs): `fold()` applies the write blindly (same convention
            # as every other verb -- validation happens once, at the write
            # boundary, in validate.py). `era` defaults to 1 for events that
            # predate this build (pre-phase-2 test logs and any hand-crafted
            # event with no "era" key), which is exactly era 1's meaning: a
            # target that has never been `reopen`ed. Storage is keyed by era
            # so a later rate by the same agent on the same (target, dim,
            # era) supersedes the earlier one (re-rate/abstain-supersedes,
            # unchanged from v1) while a rating cast in a DIFFERENT era never
            # overwrites or is overwritten by one from another era -- that's
            # the era-isolation rule. `state["ratings"]` (the flat view
            # assess.py's fixed-point loop consumes) is rebuilt from this
            # AFTER the full replay, filtered to each target's FINAL era.
            target = payload["target"]
            dim = payload["dim"]
            value = payload["value"]
            era = payload.get("era", 1)
            bloc = payload.get("bloc")
            (ratings_all.setdefault(target, {}).setdefault(dim, {})
             .setdefault(era, {})[agent]) = {"value": value, "seq": seq, "bloc": bloc}

        elif verb == "reopen":
            # PHASE2-SPEC.md §4: increments the target's era; the item
            # returns to sealed simply because its NEW era starts with zero
            # ratings (block_for() computes n=0 -> "sealed" for the new era
            # the same way it would for a target that had never been rated).
            # Prior-era ratings are untouched in ratings_all -- they become
            # that era's closed "history" entry, never re-touched.
            target = payload["target"]
            eras[target] = eras.get(target, 1) + 1

        elif verb == "supersede":
            # SPEC §3.2: demote (or, with action "restore", un-demote) a
            # node/edge. Latest event per target wins, so a demote can be
            # reversed. The target itself, its ratings, and its history all
            # stay in the graph -- this only sets a `demoted` marker.
            target = payload["target"]
            if payload.get("action") == "restore":
                state["demotions"].pop(target, None)
            else:
                state["demotions"][target] = {
                    "reason": payload.get("reason"), "agent": agent, "seq": seq,
                }

        elif verb == "poll_vote":
            # SPEC-evidence §2.2: cast Yes/No/decline on a categorical poll. The
            # poll record is created lazily by its first vote (so a flagged-but-
            # unvoted node has NO poll -> dormant -> byte-identical). Latest vote
            # per agent supersedes (like re-rate). Applied blindly -- the
            # dormant-until-flagged precondition is enforced once, at the write
            # boundary (ops.cmd_poll_vote), against the flag_type log.
            key = f"{payload['node']}|{payload['question']}"
            poll = state["polls"].setdefault(
                key, {"node": payload["node"], "question": payload["question"],
                      "opened_seq": seq, "votes": {}})
            poll["votes"][agent] = {"value": payload["value"], "seq": seq}

        state["event_count"] += 1
        if ts is not None:
            state["last_ts"] = ts

    # PHASE2-SPEC.md §4: project the era-and-bloc-aware `ratings_all` down to
    # the flat target -> dim -> agent -> value shape assess.py already
    # expects, keeping ONLY each target's FINAL era (i.e. its current era at
    # the end of this replay) -- "the live aggregate for a target uses
    # CURRENT-era ratings only." Doing this once, after the loop, means
    # assess.py needed zero changes: era isolation is invisible to it.
    ratings = state["ratings"]
    for target, dmap in ratings_all.items():
        cur_era = eras.get(target, 1)
        for dim, era_map in dmap.items():
            agent_vals = era_map.get(cur_era)
            if agent_vals:
                ratings.setdefault(target, {})[dim] = {
                    a: rec["value"] for a, rec in agent_vals.items()
                }

    return state


def _pick_primary(items: list[dict]):
    """Highest `agrees`, ties -> earliest (first in insertion order)."""
    if not items:
        return None
    best = items[0]
    for it in items[1:]:
        if it["agrees"] > best["agrees"]:
            best = it
    return best["id"]


_NEG_INF = float("-inf")


def _lifecycle_dims(target: str, dims: tuple, state: dict, aggregate: dict,
                     content_heat: dict, site_median_content, cfg: dict) -> dict:
    """PHASE2-SPEC.md §2: every aggregated `(target, dim)` block becomes the
    full `{mean, n, stdev, state, era, history, blocs, bloc_divergence}`
    envelope -- this wraps `lifecycle.block_for()` for each dim in `dims`
    (`("R","C")` for phrasings/comments, `("A",)` for nodes/edges/groups)."""
    return {dim: lifecycle.block_for(target, dim, state, aggregate, content_heat, site_median_content, cfg)
            for dim in dims}


def _scores_dict(target: str, state: dict, aggregate: dict, content_heat: dict,
                  site_median_content, cfg: dict) -> dict:
    """ASSESSMENT-SPEC.md §5 `"scores": {"R": {...}, "C": {...}}` for one
    phrasing/comment target, extended by PHASE2-SPEC.md §2 to the full
    lifecycle envelope on each of R/C (not just `{mean, n}`)."""
    return _lifecycle_dims(target, ("R", "C"), state, aggregate, content_heat, site_median_content, cfg)


def _pick_primary_phrasing(nid: str, phrasings: list[dict], aggregate: dict, bias: float):
    """ASSESSMENT-SPEC.md §5: "top phrasing selection now uses the R/C
    blend." Ranks by (blend, agrees), highest wins, ties -> earliest --
    `agrees` stays the tie-breaker (and the SOLE criterion when nothing has
    been rated) so a never-rated graph picks its primary phrasing exactly as
    BUILD-SPEC.md's original `_pick_primary` always did: with no ratings,
    every phrasing's blend is -inf, so the comparison degenerates to
    agrees-only, first-on-ties -- byte-for-byte the old behavior.

    blend = R-over-C-weighted average of whichever of the phrasing's R/C
    aggregate means are non-null (`bias` == how many parts R per 1 part C);
    a phrasing with neither dimension rated contributes -inf (loses to any
    rated phrasing, but ties among equally-unrated phrasings on `agrees`).
    """
    if not phrasings:
        return None

    def keyval(p):
        target = f"phrasing:{nid}:{p['id']}"
        r_mean, _rn = aggregate.get((target, "R"), (None, 0))
        c_mean, _cn = aggregate.get((target, "C"), (None, 0))
        if r_mean is None and c_mean is None:
            blend = _NEG_INF
        elif r_mean is not None and c_mean is not None:
            blend = (bias * r_mean + c_mean) / (bias + 1.0)
        else:
            blend = r_mean if r_mean is not None else c_mean
        return (blend, p["agrees"])

    best = phrasings[0]
    best_key = keyval(best)
    for p in phrasings[1:]:
        k = keyval(p)
        if k > best_key:
            best, best_key = p, k
    return best["id"]


def _comment_out(c: dict, state: dict, aggregate: dict, content_heat: dict,
                  site_median_content, cfg: dict) -> dict:
    """Project one internal comment record to its FORUMS-SPEC.md §2 public
    shape (drops the internal-only "target"/"author" bookkeeping fields),
    plus the ASSESSMENT-SPEC.md §5 `"scores"` addition (comments are rated
    on R/C exactly like phrasings), extended to the full PHASE2-SPEC.md §2
    lifecycle envelope."""
    return {
        "id": c["id"],
        "parent": c["parent"],
        "agent": c["agent"],
        "ts": c["ts"],
        "text": c["text"],
        "agrees": c["agrees"],
        "agents": list(c["agents"]),
        "scores": _scores_dict(f"comment:{c['id']}", state, aggregate, content_heat, site_median_content, cfg),
    }


def _comments_for(state: dict, target_id: str, aggregate: dict, content_heat: dict,
                   site_median_content, cfg: dict) -> list[dict]:
    # state["comment_order"] is insertion (== seq) order; filtering it rather
    # than iterating state["comments"].values() keeps the projection ordered
    # deterministically, per FORUMS-SPEC.md §2 ("order by seq").
    return [
        _comment_out(state["comments"][cid], state, aggregate, content_heat, site_median_content, cfg)
        for cid in state["comment_order"]
        if state["comments"][cid]["target"] == target_id
    ]


def _rating_count(state: dict) -> int:
    """ASSESSMENT-SPEC.md §6 `meta.rating_count`: the number of CURRENTLY
    active (agent, target, dim) ratings -- i.e. current board state, the
    same convention `comment_count`/`event_count` use for everything else
    that doesn't supersede. (Ratings, unlike comments, CAN supersede via
    re-rate/abstain -- see `ratings`' docstring in `new_state()` -- so this
    is deliberately a live count, not a lifetime count of `rate` events.)"""
    return sum(len(amap) for dmap in state["ratings"].values() for amap in dmap.values())


def to_graph_json(state: dict, question: str | None = None, assessment_config: dict | None = None,
                   phase2_config: dict | None = None) -> dict:
    """Project internal fold state to the FROZEN graph.json public schema
    (plus FORUMS-SPEC.md §2's additive comments/typings fields,
    ASSESSMENT-SPEC.md §5's additive scores/agreement/quality/accounts
    fields, and PHASE2-SPEC.md's additive lifecycle-state/dispersion/heat/
    era/bloc envelope on every one of those). `assessment_config` /
    `phase2_config` are the raw `config.json` `"assessment"` / `"phase2"`
    blocks (or None); `assess.compute()` / `lifecycle.resolve_config()` fill
    in every missing knob with its documented default."""
    computed = assess.compute(state, assessment_config)
    aggregate = computed["aggregate"]
    bias = float(computed["config"]["phrasing_R_over_C_bias"])

    cfg = lifecycle.resolve_config(phase2_config)
    heat_info = lifecycle.compute_heat_and_medians(state, cfg)
    content_heat = heat_info["_content_raw"]
    site_median_content = heat_info["site_median_content_heat"]

    demotions = state.get("demotions", {})

    # SPEC-evidence-argument-ought-ghosts §3.1: export the AUTO ghost-eligibility
    # signal (a target refuted on its OWN Agreement -- low, settled, and NOT an
    # antithesis rival) as a conditional per-target flag, so the viewer renders
    # auto-ghosts identically to manually-`demoted` ones without re-deriving the
    # rule client-side and risking divergence (UI request, 2026-07-17). Same
    # rule as the `ghosts` read verb; conditional (present only when True), so
    # non-eligible targets and anchor-free graphs stay byte-identical.
    from . import contested  # local import: sidesteps any fold<->contested cycle
    ghost_eligible = {
        t for t, v in contested.assess_contestedness(state, aggregate)["nodes"].items()
        if v["verdict"] == "ghost_eligible"
    }

    nodes_out = []
    for nid in state["node_order"]:
        n = state["nodes"][nid]
        phrasings = [
            {
                "id": p["id"], "text": p["text"], "agrees": p["agrees"], "agents": list(p["agents"]),
                "scores": _scores_dict(f"phrasing:{nid}:{p['id']}", state, aggregate, content_heat,
                                        site_median_content, cfg),
            }
            for p in n["phrasings"]
        ]
        titles = [
            {"id": t["id"], "text": t["text"], "agrees": t["agrees"], "agents": list(t["agents"])}
            for t in n["titles"]
        ]
        primary_phrasing = _pick_primary_phrasing(nid, phrasings, aggregate, bias)
        # A node with no phrasings at all (shouldn't happen -- create_node
        # always seeds p0 -- but kept defensive, matching the pre-phase2
        # code's own defensive default) inherits an empty, never-rated block
        # rather than any real phrasing's.
        _empty = {"mean": None, "n": 0, "stdev": None, "state": "sealed", "era": 1,
                  "history": [], "blocs": {}, "bloc_divergence": None}
        quality = {"R": dict(_empty), "C": dict(_empty)}
        for p in phrasings:
            if p["id"] == primary_phrasing:
                quality = p["scores"]
                break
        agreement = lifecycle.block_for(nid, "A", state, aggregate, content_heat, site_median_content, cfg)
        node_heat = {"content": round(content_heat.get(nid, 0.0), 6),
                     "rating": round(heat_info["heat"]["rating"].get(nid, 0.0), 6)}
        nodes_out.append({
            "id": nid,
            "kind": n["kind"],
            "primary_phrasing": primary_phrasing,
            "primary_title": _pick_primary(titles) if titles else None,
            "phrasings": phrasings,
            "titles": titles,
            "source_ref": n["source_ref"],
            "author": n["author"],
            "created_seq": n["created_seq"],
            "comments": _comments_for(state, nid, aggregate, content_heat, site_median_content, cfg),
            # ASSESSMENT-SPEC.md §5: node's own rated dimension (Agreement)
            # plus R/C INHERITED from its current top phrasing (no R/C of its
            # own -- §1: "a node's inherited R/C can thus change when a
            # better phrasing wins, with nobody rating the node"). Both are
            # now the full PHASE2-SPEC.md §2 lifecycle envelope, not just
            # {mean, n} -- quality's block is a straight copy of the winning
            # phrasing's own block (era/state/history/blocs included), since
            # "inherited" means inheriting the WHOLE aggregate, not just its
            # mean.
            "agreement": agreement,
            "quality": quality,
            # PHASE2-SPEC.md §3 (amended by p2.1): event-time heat, two
            # independent ledgers, rounded to 6 decimals for byte-stability.
            "heat": node_heat,
        })
        if nid in demotions:
            nodes_out[-1]["demoted"] = dict(demotions[nid])
        if nid in ghost_eligible:
            nodes_out[-1]["ghost_eligible"] = True

    edges_out = []
    for eid in state["edge_order"]:
        e = state["edges"][eid]
        typings = [
            {
                "id": t["id"], "node": t["node"], "label": t["label"],
                "agrees": t["agrees"], "agents": list(t["agents"]), "author": t["author"],
            }
            for t in e["typings"]
        ]
        edge_agreement = lifecycle.block_for(eid, "A", state, aggregate, content_heat, site_median_content, cfg)
        edges_out.append({
            "id": eid,
            "from": e["from"],
            "to": e["to"],
            "group": e["group"],
            "agrees": e["agrees"],
            "strength": e["agrees"] + 1,
            "agents": list(e["agents"]),
            "author": e["author"],
            "created_seq": e["created_seq"],
            # ASSESSMENT-SPEC.md §1/§5, amended (see Amendments section):
            # edges now ALSO carry a graded `"agreement"` (dim A), computed
            # by the exact same True_R-weighted fixed-point loop as every
            # other rated target -- an edge Agreement rating is just another
            # (target, dim) pair to assess.compute(), nothing edge-specific
            # was added to the aggregation machinery itself. Now the full
            # PHASE2-SPEC.md §2 lifecycle envelope. This sits ALONGSIDE, and
            # never touches, the original structural `agrees`/`strength`
            # consensus fields above -- both are kept, independent signals.
            "agreement": edge_agreement,
            "comments": _comments_for(state, eid, aggregate, content_heat, site_median_content, cfg),
            "typings": typings,
            "primary_typing": _pick_primary(typings),
        })
        if eid in demotions:
            edges_out[-1]["demoted"] = dict(demotions[eid])
        if eid in ghost_eligible:
            edges_out[-1]["ghost_eligible"] = True

    groups_out = []
    for gid in state["group_order"]:
        g = state["groups"][gid]
        group_target = f"group:{gid}"
        groups_out.append({
            "id": gid,
            "to": g["to"],
            "members": list(g["members"]),
            "author": g.get("author"),
            # PHASE2-SPEC.md §7 (f16 closure): the group's own graded A
            # rating -- "if ALL members were so, how strongly would the
            # conjunction support `to`" -- aggregates exactly like an edge's,
            # full lifecycle envelope included.
            "agreement": lifecycle.block_for(group_target, "A", state, aggregate, content_heat,
                                              site_median_content, cfg),
        })

    sets_out = []
    for sid in state["set_order"]:
        s = state["sets"][sid]
        members = [
            {"node": m["node"], "agrees": m["agrees"], "belonging": m["agrees"] + 1, "author": m["author"]}
            for m in s["members"]
        ]
        sets_out.append({"id": sid, "members": members})
        if sid in demotions:
            sets_out[-1]["demoted"] = dict(demotions[sid])

    frictions_out = [dict(f) for f in state["frictions"]]

    full_config = dict(computed["config"])
    full_config["phase2"] = cfg

    meta = {
        "question": question or DEFAULT_QUESTION,
        # Deliberately NOT wall-clock (BUILD-SPEC.md §3): copied from the log
        # so that rebuild is byte-for-byte deterministic given the same log.
        "generated_ts": state["last_ts"],
        "event_count": state["event_count"],
        # FORUMS-SPEC.md §2.
        "comment_count": len(state["comment_order"]),
        # ASSESSMENT-SPEC.md §5/§6.
        "rating_count": _rating_count(state),
        # PHASE2-SPEC.md §1: "config used must be recorded in graph.json meta
        # so rebuilds are reproducible from the log + flags" -- `assessment`
        # (v1, unchanged) plus the new `phase2` block, together in one place.
        "config": full_config,
        # PHASE2-SPEC.md §3: "stats reports site medians" -- stashed in meta
        # too (not just recomputed ad hoc by the `stats` read verb) so every
        # consumer of graph.json sees the exact medians `heat`/`state` above
        # were computed against.
        "heat_medians": {
            "content": heat_info["site_median_content_heat"],
            "rating": heat_info["site_median_rating_heat"],
        },
    }

    result = {
        "meta": meta,
        "nodes": nodes_out,
        "ground_edges": edges_out,
        "conjunction_groups": groups_out,
        "antithesis_sets": sets_out,
        "frictions": frictions_out,
        # ASSESSMENT-SPEC.md §5: one reputation account per agent who has
        # ever authored or rated anything, sorted by agent id (a stable,
        # explicit order independent of event/dict iteration order).
        "accounts": computed["accounts"],
    }

    # SPEC-evidence §2.2: categorical-poll surface. A poll with no votes is
    # DORMANT and emits nothing; the "polls" key itself is omitted when there
    # are no voted polls, so every graph without poll activity (all three
    # flagship graphs) rebuilds byte-identically.
    poll_res = computed.get("polls", {})
    polls_out = []
    for key in sorted(state.get("polls", {})):
        poll = state["polls"][key]
        if not poll["votes"]:
            continue
        r = poll_res.get(key, {})
        polls_out.append({
            "node": poll["node"], "question": poll["question"],
            "yes": r.get("yes", 0), "no": r.get("no", 0), "decline": r.get("decline", 0),
            "n_votes": r.get("n_votes", 0), "yes_share": r.get("yes_share"),
            "resolved": r.get("resolved", False), "resolved_kind": r.get("resolved_kind"),
            "reopen_required": r.get("reopen_required", False),
        })
    if polls_out:
        result["polls"] = polls_out

    return result
