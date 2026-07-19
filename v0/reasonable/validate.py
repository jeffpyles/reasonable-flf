"""Validation rules enforced at the write boundary (BUILD-SPEC.md §2).

Every validate_* function takes the current *internal* fold state (see
fold.py) plus the proposed write's arguments, and returns
`(errors, warnings)` where each is a list of `(tag, message)` pairs.

- Non-empty `errors` => the write MUST be rejected (nothing appended).
- Non-empty `warnings` => the write proceeds, but the message should be
  surfaced to the caller (and, for stats' health signals, recorded).

Tags exist so callers (stats' health signals in particular) can count
occurrences by *kind* without re-parsing human-readable text.
"""
from __future__ import annotations

import re

from .errors import TargetNotFound
from .fold import (
    EVIDENCE_KIND,
    OUGHT_KIND,
    VALID_NODE_KINDS,
    is_evidence_kind,
    is_ought_kind,
    resolve_rate_target,
    resolve_target,
)

DEFAULT_MAX_CLAIM_CHARS = 350
DEFAULT_MAX_COMMENT_CHARS = 2000  # FORUMS-SPEC.md §3: soft cap, warning not error


def _norm_text(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip()).lower()


def find_duplicate_phrasing(state: dict, text: str):
    """Return (node_id, phrasing_id) of an existing phrasing with the same
    normalized text, or None. Used for the duplicate-text warning."""
    target = _norm_text(text)
    if not target:
        return None
    for nid in state["node_order"]:
        for p in state["nodes"][nid]["phrasings"]:
            if _norm_text(p["text"]) == target:
                return nid, p["id"]
    return None


def validate_create_node(
    state: dict,
    agent: str,
    kind: str,
    text: str,
    source: str | None,
    title: str | None,
    max_claim_chars: int = DEFAULT_MAX_CLAIM_CHARS,
):
    errors: list[tuple[str, str]] = []
    warnings: list[tuple[str, str]] = []

    if kind not in VALID_NODE_KINDS:
        errors.append((
            "invalid_kind",
            f"--kind must be one of 'claim', 'evidence', 'ought' (or legacy "
            f"'external_anchor'), got {kind!r}",
        ))
    if not text or not text.strip():
        errors.append(("empty_text", "--text is required and cannot be empty"))
    if is_evidence_kind(kind) and not (source and source.strip()):
        errors.append(("evidence_source", "--source is required when --kind evidence"))

    if text and len(text) > max_claim_chars:
        warnings.append((
            "over_cap",
            f"claim text is {len(text)} chars, over the {max_claim_chars}-char soft cap",
        ))
    if text and text.strip():
        dup = find_duplicate_phrasing(state, text)
        if dup:
            dnode, dpid = dup
            warnings.append((
                "duplicate_text",
                f"text matches existing phrasing {dpid} on node {dnode} -- did you `search` first?",
            ))

    return errors, warnings


def validate_draw_ground(state: dict, agent: str, frm: str, to: str, group: str | None):
    errors: list[tuple[str, str]] = []
    warnings: list[tuple[str, str]] = []

    if frm not in state["nodes"]:
        errors.append(("missing_ref", f"unknown node: {frm}"))
    if to not in state["nodes"]:
        errors.append(("missing_ref", f"unknown node: {to}"))
    if frm == to:
        errors.append(("self_ground", "a node may not be its own Ground (1-cycles are rejected; "
                                       "multi-node cycles are allowed)"))

    # SPEC §1.3 grammar rules the node types enforce. `draw_ground(frm, to)`
    # means "frm is a Ground of to", so support flows frm -> to.
    if frm in state["nodes"] and to in state["nodes"]:
        frm_kind = state["nodes"][frm].get("kind")
        to_kind = state["nodes"][to].get("kind")
        # Hume's rule (structural, hard): an Ought may not ground an is-node.
        # You cannot derive an "is" from an "ought." Ought->Ought is allowed
        # (instrumental value chains).
        if is_ought_kind(frm_kind) and not is_ought_kind(to_kind):
            errors.append((
                "hume_violation",
                f"an Ought ({frm}) may not be a Ground of a non-Ought ({to}, kind "
                f"{to_kind!r}): you cannot derive an 'is' from an 'ought' "
                "(Ought->Ought is allowed)",
            ))
        # Evidence-leaf rule (soft, a warning): an Evidence node is grounded by
        # its source, not by in-graph reasoning. Flag an edge that grounds an
        # Evidence node so the author can reconsider (a claim that supports a
        # fact usually wants the fact as its own Ground, not the reverse).
        if is_evidence_kind(to_kind):
            warnings.append((
                "evidence_grounded",
                f"drawing a Ground into Evidence node {to}: Evidence is anchored by "
                "its source, not grounded by in-graph nodes -- did you mean to draw "
                "the edge the other way?",
            ))

    if group and group != "new":
        g = state["groups"].get(group)
        if g is None:
            errors.append(("missing_ref", f"unknown conjunction group: {group}"))
        elif to in state["nodes"] and g["to"] != to:
            errors.append((
                "group_conflict",
                f"group {group} already targets {g['to']}, cannot also target {to}",
            ))

    return errors, warnings


def validate_add_antithesis(state: dict, agent: str, node: str, set_id: str | None):
    errors: list[tuple[str, str]] = []

    if node not in state["nodes"]:
        errors.append(("missing_ref", f"unknown node: {node}"))

    if set_id and set_id != "new":
        s = state["sets"].get(set_id)
        if s is None:
            errors.append(("missing_ref", f"unknown antithesis set: {set_id}"))
        else:
            if any(m["node"] == node for m in s["members"]):
                errors.append((
                    "duplicate_set_membership",
                    f"node {node} is already a member of set {set_id}",
                ))

    return errors, []


def validate_agree(state: dict, agent: str, target: str):
    errors: list[tuple[str, str]] = []

    try:
        _kind, obj = resolve_target(state, target)
    except TargetNotFound as e:
        return [("missing_ref", str(e))], []

    author = obj.get("author", obj.get("_author"))
    if author == agent:
        errors.append(("self_agree", f"cannot agree with your own object ({target}): self-agree is rejected"))
    if agent in obj.get("agents", []):
        errors.append(("duplicate_agree", f"agent {agent} has already agreed with {target}"))

    return errors, []


def validate_propose_title(state: dict, agent: str, node: str, text: str,
                            max_claim_chars: int = DEFAULT_MAX_CLAIM_CHARS):
    errors: list[tuple[str, str]] = []
    warnings: list[tuple[str, str]] = []

    if node not in state["nodes"]:
        errors.append(("missing_ref", f"unknown node: {node}"))
    if not text or not text.strip():
        errors.append(("empty_text", "--text is required and cannot be empty"))
    if text and len(text) > max_claim_chars:
        warnings.append(("over_cap", f"title text is {len(text)} chars, over the {max_claim_chars}-char soft cap"))

    return errors, warnings


def validate_propose_phrasing(state: dict, agent: str, node: str, text: str,
                               max_claim_chars: int = DEFAULT_MAX_CLAIM_CHARS):
    errors: list[tuple[str, str]] = []
    warnings: list[tuple[str, str]] = []

    if node not in state["nodes"]:
        errors.append(("missing_ref", f"unknown node: {node}"))
    if not text or not text.strip():
        errors.append(("empty_text", "--text is required and cannot be empty"))
    if text and len(text) > max_claim_chars:
        warnings.append(("over_cap", f"phrasing text is {len(text)} chars, over the {max_claim_chars}-char soft cap"))
    if text and text.strip():
        dup = find_duplicate_phrasing(state, text)
        if dup:
            dnode, dpid = dup
            warnings.append((
                "duplicate_text",
                f"text matches existing phrasing {dpid} on node {dnode} -- did you `search` first?",
            ))

    return errors, warnings


def validate_flag_friction(state: dict, agent: str, text: str, refs: list[str]):
    errors: list[tuple[str, str]] = []

    if not text or not text.strip():
        errors.append(("empty_text", "--text is required and cannot be empty"))
    for r in refs or []:
        if r not in state["nodes"]:
            errors.append(("missing_ref", f"unknown node ref: {r}"))

    return errors, []


# --- FORUMS-SPEC.md §1/§3 additions (additive only) ------------------------

def validate_flag_type(state: dict, agent: str, node: str, as_kind: str):
    """`flag-type --node <n> --as <ought|evidence>`
    (SPEC-evidence-argument-ought-ghosts.md §1.4): record a candidate
    re-typing of a node. This is a FLAG only -- it does not change the node's
    kind; the categorical-consensus poll that resolves it is §2 (the
    Assessment thread). `node` must exist and `as_kind` must be a re-typeable
    target kind (evidence or ought -- flagging a node as a plain claim is not
    a meaningful categorical assertion here)."""
    errors: list[tuple[str, str]] = []

    if node not in state["nodes"]:
        errors.append(("missing_ref", f"unknown node: {node}"))
    if as_kind not in (EVIDENCE_KIND, OUGHT_KIND):
        errors.append((
            "invalid_flag_type",
            f"--as must be 'evidence' or 'ought', got {as_kind!r}",
        ))

    return errors, []


def validate_supersede(state: dict, agent: str, target: str, action: str):
    """`supersede --target <node|edge|set> [--reason ...] [--restore]`
    (SPEC-evidence-argument-ought-ghosts.md §3.2): demote a node, edge, or
    antithesis set toward ghost status, or (action="restore") un-demote it.
    `target` must be an existing node, edge, or set id. No self-restriction:
    demoting your own material is fine (it's a curation act, not a rating)."""
    errors: list[tuple[str, str]] = []

    if target not in state["nodes"] and target not in state["edges"] \
            and target not in state.get("sets", {}):
        errors.append(("missing_ref", f"unknown node/edge/set: {target}"))
    if action not in ("demote", "restore"):
        errors.append(("invalid_action", f"action must be 'demote' or 'restore', got {action!r}"))
    if action == "restore" and target not in state.get("demotions", {}):
        errors.append(("not_demoted", f"{target} is not currently demoted -- nothing to restore"))

    return errors, []


POLL_VOTE_VALUES = ("yes", "no", "decline")


def validate_poll_vote(state: dict, agent: str, node: str, question: str, value: str,
                        open_polls: set | None = None):
    """`poll-vote --node <n> --question <q> --value <yes|no|decline>`
    (SPEC-evidence-argument-ought-ghosts.md §2.2). The poll must already be OPEN --
    someone `flag-type`d the node. `flag_type` is a non-folding marker, so the set
    of open "<node>|type:<kind>" keys is derived from the event log by the caller
    (ops.cmd_poll_vote) and passed in; voting on an unopened poll is rejected,
    honoring "dormant until flagged."""
    errors: list[tuple[str, str]] = []

    if node not in state["nodes"]:
        errors.append(("missing_ref", f"unknown node: {node}"))
    if value not in POLL_VOTE_VALUES:
        errors.append((
            "invalid_poll_vote",
            f"--value must be one of {POLL_VOTE_VALUES}, got {value!r}",
        ))
    if open_polls is not None and f"{node}|{question}" not in open_polls:
        errors.append((
            "poll_not_open",
            f"no open poll for {node} / {question} -- flag-type the node first",
        ))

    return errors, []


def validate_comment(
    state: dict,
    agent: str,
    target: str | None,
    text: str,
    parent: str | None,
    max_comment_chars: int = DEFAULT_MAX_COMMENT_CHARS,
):
    errors: list[tuple[str, str]] = []
    warnings: list[tuple[str, str]] = []

    if not text or not text.strip():
        errors.append(("empty_text", "--text is required and cannot be empty"))

    # --target and --reply-to are mutually exclusive, and exactly one must
    # be given: a reply inherits its parent's target instead of naming one.
    if bool(target) == bool(parent):
        errors.append((
            "target_parent_conflict",
            "exactly one of --target or --reply-to is required (they are mutually exclusive)",
        ))
    elif parent:
        if parent not in state["comments"]:
            errors.append(("missing_ref", f"unknown parent comment: {parent}"))
    else:
        if target not in state["nodes"] and target not in state["edges"]:
            errors.append(("missing_ref", f"unknown comment target: {target}"))

    if text and len(text) > max_comment_chars:
        warnings.append((
            "over_cap",
            f"comment text is {len(text)} chars, over the {max_comment_chars}-char soft cap",
        ))

    return errors, warnings


def validate_propose_typing(state: dict, agent: str, edge: str, node: str | None, label: str | None):
    errors: list[tuple[str, str]] = []

    if edge not in state["edges"]:
        errors.append(("missing_ref", f"unknown edge: {edge}"))

    have_node = bool(node)
    have_label = bool(label and label.strip())
    if have_node == have_label:
        errors.append((
            "typing_node_label_conflict",
            "exactly one of --node or --label is required (a typing references a trunk node or "
            "gives a free-text label, never both/neither)",
        ))
    elif have_node and node not in state["nodes"]:
        errors.append(("missing_ref", f"unknown node: {node}"))

    return errors, []


# --- PHASE2-SPEC.md §4 addition (additive only) ------------------------------

def validate_reopen(state: dict, agent: str, target: str, reason: str):
    """`reopen --target <id> --reason "<text>"`: `target` must resolve as a
    rateable target (node/edge/phrasing/comment/group -- exactly the same
    grammar `rate` accepts, reused via `resolve_rate_target`) and `reason`
    must be non-empty (a public record of why the era turned, per
    PHASE2-SPEC.md §4). Unlike `rate`, there is no self-action restriction:
    the spec frames reopening as harness/content-gate-triggered, not an
    author privilege or restriction -- "the harness calls it explicitly"."""
    errors: list[tuple[str, str]] = []

    if not reason or not reason.strip():
        errors.append(("empty_text", "--reason is required and cannot be empty"))

    try:
        resolve_rate_target(state, target)
    except TargetNotFound as e:
        errors.append(("missing_ref", str(e)))

    return errors, []


# --- ASSESSMENT-SPEC.md §2 addition (additive only) -------------------------

def validate_rate(state: dict, agent: str, target: str, dim: str, value, scale_max: float = 5.0):
    """`target`/`dim` per ASSESSMENT-SPEC.md §2 (amended -- see the
    Amendments section): `phrasing:<node>:<pid>` (dim R|C), a bare
    `<nodeid>` or `<edgeid>` (dim A only -- R/C are rejected on edges via the
    `dim not in valid_dims` check below, `resolve_rate_target` gives edges
    `valid_dims == {"A"}`), or `comment:<cid>` (dim R|C). `value` is a float
    in [0, scale_max] or the literal string "abstain". Self-rating (rating
    your own authored phrasing/comment/node/edge) is rejected, same as
    self-agree (BUILD-SPEC.md §2 rule 2)."""
    errors: list[tuple[str, str]] = []

    try:
        _kind, obj, valid_dims = resolve_rate_target(state, target)
    except TargetNotFound as e:
        return [("missing_ref", str(e))], []

    if dim not in valid_dims:
        errors.append((
            "invalid_dim",
            f"dim {dim!r} is not valid for target {target!r} (expected one of {sorted(valid_dims)})",
        ))

    author = obj.get("author", obj.get("_author"))
    if author == agent:
        errors.append(("self_rate", f"cannot rate your own object ({target}): self-rating is rejected"))

    if isinstance(value, str):
        if value != "abstain":
            errors.append(("invalid_value", f"string values must be exactly 'abstain', got {value!r}"))
    elif isinstance(value, (int, float)):
        if not (0.0 <= float(value) <= scale_max):
            errors.append(("value_range", f"value {value} out of range 0.0-{scale_max}"))
    else:
        errors.append(("invalid_value", f"value must be a float 0.0-{scale_max} or 'abstain', got {value!r}"))

    return errors, []
