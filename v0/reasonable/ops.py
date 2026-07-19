"""High-level write-verb handlers: validate -> append -> rebuild.

Each `cmd_*` function is the full implementation of one write verb from
BUILD-SPEC.md §2: load the log, fold it, validate the proposed write against
that state, and either reject (recording an audit entry) or append the new
event, persist it, and rewrite graph.json. graph.py (the CLI) is a thin
argparse wrapper around these.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from . import assess, lifecycle, store, validate
from .fold import DEFAULT_QUESTION, fold, to_graph_json


@dataclass
class Result:
    ok: bool
    id: str | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    data: dict | None = None


def _load_state(data_dir: Path):
    events = store.read_events(data_dir)
    return events, fold(events)


def _rebuild_impl(data_dir: Path) -> dict:
    """The actual rebuild work: fold events.jsonl and atomically rewrite
    graph.json. Callers must already hold `store.locked(data_dir)` -- this
    is called both from inside each write verb's locked critical section
    (via `_finish`) and from the public `rebuild()` below."""
    _events, state = _load_state(data_dir)
    config = store.read_config(data_dir)
    graph = to_graph_json(
        state,
        question=config.get("question", DEFAULT_QUESTION),
        assessment_config=config.get("assessment"),
        phase2_config=config.get("phase2"),
    )
    # Name each Evidence node's source (study) in the committed snapshot so the
    # viewer can render it on the node body (FLF requirement). Local import
    # avoids an ops<->queries import cycle at module load.
    from . import queries
    queries.attach_sources(graph, data_dir)
    queries.attach_layers(graph)
    store.write_graph_json(data_dir, graph)
    return graph


def rebuild(data_dir: Path, phase2_overrides: dict | None = None) -> dict:
    """Regenerate graph.json from events.jsonl. Deterministic, idempotent.

    Acquires the write lock itself (BUILD-SPEC.md §3 note): `rebuild` also
    mutates graph.json, so a standalone `graph.py rebuild` call must not be
    allowed to race a concurrent writer's read-fold-append-rebuild cycle.

    `phase2_overrides` (PHASE2-SPEC.md §1: "--quorum, --confirm,
    --contested-threshold" etc. "on rebuild") is a dict of knob-name ->
    value for any of `lifecycle.DEFAULT_PHASE2_CONFIG`'s keys that were
    explicitly passed on the command line; `None`/absent keys are left
    untouched. When given, it's merged into `<data>/config.json`'s
    `"phase2"` block BEFORE the rebuild, so the new config persists for
    every subsequent write/rebuild too (not just this one call) -- the same
    "config lives in config.json" convention ASSESSMENT-SPEC.md §6 already
    established for the `"assessment"` block.
    """
    with store.locked(data_dir):
        if phase2_overrides:
            config = store.read_config(data_dir)
            phase2 = dict(config.get("phase2") or {})
            phase2.update({k: v for k, v in phase2_overrides.items() if v is not None})
            config["phase2"] = phase2
            store.write_config(data_dir, config)
        return _rebuild_impl(data_dir)


def _reject(data_dir: Path, agent: str, verb: str, errors: list[tuple[str, str]]) -> Result:
    store.append_audit(data_dir, agent, verb, "rejected", errors)
    return Result(ok=False, errors=[msg for _tag, msg in errors])


def _finish(data_dir: Path, agent: str, verb: str, payload: dict, warnings: list[tuple[str, str]],
            state: dict, id_: str | None) -> Result:
    if warnings:
        payload = dict(payload)
        payload["warnings"] = [msg for _tag, msg in warnings]
        store.append_audit(data_dir, agent, verb, "warning", warnings)
    event = store.make_event(state, agent, verb, payload)
    store.append_event(data_dir, event)
    _rebuild_impl(data_dir)
    return Result(ok=True, id=id_, warnings=[msg for _tag, msg in warnings])


# Each cmd_* function below is one write verb's ENTIRE critical section --
# read/fold current state -> validate -> append event (with its seq
# assignment) -> rebuild graph.json -- wrapped in the cross-process write
# lock (store.locked) so concurrent writers serialize instead of racing on
# seq assignment or tearing events.jsonl/graph.json.

def cmd_create_node(data_dir: Path, agent: str, text: str, kind: str = "claim",
                     source: str | None = None, title: str | None = None,
                     max_claim_chars: int = validate.DEFAULT_MAX_CLAIM_CHARS) -> Result:
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        errors, warnings = validate.validate_create_node(state, agent, kind, text, source, title, max_claim_chars)
        if errors:
            return _reject(data_dir, agent, "create_node", errors)
        nid = store.next_node_id(state)
        payload = {"id": nid, "kind": kind, "text": text, "source": source, "title": title}
        return _finish(data_dir, agent, "create_node", payload, warnings, state, nid)


def cmd_draw_ground(data_dir: Path, agent: str, frm: str, to: str, group: str | None = None) -> Result:
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        errors, warnings = validate.validate_draw_ground(state, agent, frm, to, group)
        if errors:
            return _reject(data_dir, agent, "draw_ground", errors)
        eid = store.next_edge_id(state)
        gid = store.next_group_id(state) if group == "new" else group
        payload = {"id": eid, "from": frm, "to": to, "group": gid}
        return _finish(data_dir, agent, "draw_ground", payload, warnings, state, eid)


def cmd_add_antithesis(data_dir: Path, agent: str, node: str, set_id: str | None = None) -> Result:
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        errors, warnings = validate.validate_add_antithesis(state, agent, node, set_id)
        if errors:
            return _reject(data_dir, agent, "add_antithesis", errors)
        sid = store.next_set_id(state) if set_id == "new" else set_id
        payload = {"set": sid, "node": node}
        return _finish(data_dir, agent, "add_antithesis", payload, warnings, state, sid)


def cmd_agree(data_dir: Path, agent: str, target: str) -> Result:
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        errors, warnings = validate.validate_agree(state, agent, target)
        if errors:
            return _reject(data_dir, agent, "agree", errors)
        payload = {"target": target}
        return _finish(data_dir, agent, "agree", payload, warnings, state, target)


def cmd_propose_title(data_dir: Path, agent: str, node: str, text: str,
                       max_claim_chars: int = validate.DEFAULT_MAX_CLAIM_CHARS) -> Result:
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        errors, warnings = validate.validate_propose_title(state, agent, node, text, max_claim_chars)
        if errors:
            return _reject(data_dir, agent, "propose_title", errors)
        tid = store.next_title_id(state["nodes"][node])
        payload = {"id": tid, "node": node, "text": text}
        return _finish(data_dir, agent, "propose_title", payload, warnings, state, tid)


def cmd_propose_phrasing(data_dir: Path, agent: str, node: str, text: str,
                          max_claim_chars: int = validate.DEFAULT_MAX_CLAIM_CHARS) -> Result:
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        errors, warnings = validate.validate_propose_phrasing(state, agent, node, text, max_claim_chars)
        if errors:
            return _reject(data_dir, agent, "propose_phrasing", errors)
        pid = store.next_phrasing_id(state["nodes"][node])
        payload = {"id": pid, "node": node, "text": text}
        return _finish(data_dir, agent, "propose_phrasing", payload, warnings, state, pid)


def cmd_flag_friction(data_dir: Path, agent: str, text: str, refs: list[str] | None = None) -> Result:
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        refs = refs or []
        errors, warnings = validate.validate_flag_friction(state, agent, text, refs)
        if errors:
            return _reject(data_dir, agent, "flag_friction", errors)
        fid = store.next_friction_id(state)
        payload = {"id": fid, "text": text, "refs": refs}
        return _finish(data_dir, agent, "flag_friction", payload, warnings, state, fid)


def cmd_supersede(data_dir: Path, agent: str, target: str, reason: str | None = None,
                  restore: bool = False) -> Result:
    """SPEC-evidence-argument-ought-ghosts.md §3.2: demote a node/edge toward
    ghost status (or restore it) -- never a delete. Folds to a conditional
    `demoted` marker; graphs with no supersede event stay byte-identical."""
    action = "restore" if restore else "demote"
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        errors, warnings = validate.validate_supersede(state, agent, target, action)
        if errors:
            return _reject(data_dir, agent, "supersede", errors)
        payload = {"target": target, "action": action}
        if reason and reason.strip():
            payload["reason"] = reason
        return _finish(data_dir, agent, "supersede", payload, warnings, state, target)


def cmd_flag_type(data_dir: Path, agent: str, node: str, as_kind: str) -> Result:
    """SPEC-evidence-argument-ought-ghosts.md §1.4: flag a node as a candidate
    Ought/Evidence. Recorded as a durable event but NOT folded into graph.json
    in §1 -- the categorical-consensus poll that resolves the flag (and its
    graph surface) is §2, the Assessment thread's lane. Because fold() treats
    `flag_type` as a non-mutating marker, appending one leaves every existing
    graph.json byte-identical on rebuild."""
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        errors, warnings = validate.validate_flag_type(state, agent, node, as_kind)
        if errors:
            return _reject(data_dir, agent, "flag_type", errors)
        # Sequential id over prior flags; fold does not track these, so count
        # them straight off the log.
        n_prior = sum(1 for e in _events if e.get("verb") == "flag_type")
        fid = f"ft{n_prior + 1}"
        payload = {"id": fid, "node": node, "as": as_kind}
        return _finish(data_dir, agent, "flag_type", payload, warnings, state, fid)


def cmd_poll_vote(data_dir: Path, agent: str, node: str, question: str, value: str) -> Result:
    """SPEC-evidence-argument-ought-ghosts.md §2.2: cast a Yes/No/decline vote on
    an open categorical poll. The poll must have been opened by a prior `flag_type`
    (validation enforces it). Resolution is reputation-weighted and derived at
    assess time (reasonable/typepoll.py) -- this verb only records the vote."""
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        # `flag_type` is a non-folding marker, so derive the set of OPEN polls
        # ("<node>|type:<kind>") straight from the log for the dormant-until-
        # flagged gate.
        open_polls = {f"{e['payload']['node']}|type:{e['payload']['as']}"
                      for e in _events if e.get("verb") == "flag_type"}
        errors, warnings = validate.validate_poll_vote(state, agent, node, question, value, open_polls)
        if errors:
            return _reject(data_dir, agent, "poll_vote", errors)
        n_prior = sum(1 for e in _events if e.get("verb") == "poll_vote")
        payload = {"node": node, "question": question, "value": value}
        return _finish(data_dir, agent, "poll_vote", payload, warnings, state, f"pv{n_prior + 1}")


# --- FORUMS-SPEC.md §1/§3 write verbs (additive; same locked pipeline) -----

def cmd_comment(data_dir: Path, agent: str, target: str | None = None, text: str = "",
                reply_to: str | None = None,
                max_comment_chars: int = validate.DEFAULT_MAX_COMMENT_CHARS) -> Result:
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        errors, warnings = validate.validate_comment(state, agent, target, text, reply_to, max_comment_chars)
        if errors:
            return _reject(data_dir, agent, "comment", errors)
        # A reply inherits its parent's target (FORUMS-SPEC.md §3) -- resolved
        # here, once, at write time, so fold() never has to walk the parent
        # chain and every stored comment event already carries its final,
        # explicit target.
        resolved_target = state["comments"][reply_to]["target"] if reply_to else target
        cid = store.next_comment_id(state)
        payload = {"id": cid, "target": resolved_target, "parent": reply_to, "text": text}
        return _finish(data_dir, agent, "comment", payload, warnings, state, cid)


def cmd_propose_typing(data_dir: Path, agent: str, edge: str, node: str | None = None,
                        label: str | None = None) -> Result:
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        errors, warnings = validate.validate_propose_typing(state, agent, edge, node, label)
        if errors:
            return _reject(data_dir, agent, "propose_typing", errors)
        tyid = store.next_typing_id(state["edges"][edge])
        payload = {"id": tyid, "edge": edge, "node": node, "label": label}
        return _finish(data_dir, agent, "propose_typing", payload, warnings, state, tyid)


# --- ASSESSMENT-SPEC.md §2/§6 write verb (additive; same locked pipeline) --

def cmd_rate(data_dir: Path, agent: str, target: str, dim: str, value,
             bloc: str | None = None, nudge_distance: float | None = None) -> Result:
    """`value` is already normalized by the caller to either the float 0.0-5.0
    or the literal string "abstain" (graph.py's argparse `type=` does this
    for the CLI; tests may pass either form directly to this function).

    PHASE2-SPEC.md §5/§7 additions, both optional and backward compatible:
    `bloc` (an opaque string, recorded on the event so the fold's bloc-
    divergence math can group by it) and `nudge_distance` (a per-call
    override of the configured nudge distance -- defaults to the persisted
    `phase2.nudge_distance` config knob when omitted, matching how every
    other phase-2 knob is sourced). The era recorded on the event is
    ALWAYS the target's current era per the folded state at cast time
    (PHASE2-SPEC.md §4: "assigned by the CLI, from the target's era in the
    folded state") -- never a caller-supplied value.
    """
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        config = store.read_config(data_dir)
        scale_max = assess.resolve_config(config.get("assessment"))["scale_max"]
        errors, warnings = validate.validate_rate(state, agent, target, dim, value, scale_max=scale_max)
        if errors:
            return _reject(data_dir, agent, "rate", errors)

        phase2_cfg = lifecycle.resolve_config(config.get("phase2"))
        if nudge_distance is not None:
            phase2_cfg = dict(phase2_cfg)
            phase2_cfg["nudge_distance"] = nudge_distance
        # Computed from `state` BEFORE this rating is appended -- the
        # "current" mean the new rating is being compared against.
        nudge = lifecycle.check_nudge(state, target, dim, value, phase2_cfg)

        era = state["eras"].get(target, 1)
        payload = {"target": target, "dim": dim, "value": value, "era": era}
        if bloc:
            payload["bloc"] = bloc
        res = _finish(data_dir, agent, "rate", payload, warnings, state, f"{target}:{dim}")
        if res.ok and nudge:
            res.data = {"nudge": nudge}
        return res


# --- PHASE2-SPEC.md §4 write verb (additive; same locked pipeline) ---------

def cmd_reopen(data_dir: Path, agent: str, target: str, reason: str) -> Result:
    """`reopen --target <id> --reason "<text>"`: increments the target's era
    and (by virtue of the new era starting at n=0) returns it to sealed. The
    reason is recorded on the event -- a public record of why the era
    turned (PHASE2-SPEC.md §4)."""
    with store.locked(data_dir):
        _events, state = _load_state(data_dir)
        errors, warnings = validate.validate_reopen(state, agent, target, reason)
        if errors:
            return _reject(data_dir, agent, "reopen", errors)
        new_era = state["eras"].get(target, 1) + 1
        payload = {"target": target, "reason": reason}
        return _finish(data_dir, agent, "reopen", payload, warnings, state, str(new_era))
