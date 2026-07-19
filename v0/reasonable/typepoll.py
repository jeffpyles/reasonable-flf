"""Categorical-consensus poll resolution (SPEC-evidence-argument-ought-ghosts §2.2).

A poll is opened by `flag_type` and voted by `poll_vote` (Yes / No / decline); the
fold records the raw votes (reasonable/fold.py). Resolution is REPUTATION-WEIGHTED,
so it lives here in the assessment layer where True_R is available — never in the
fold. A poll resolves Yes when it clears quorum (enough Yes+No votes) and the
reputation-weighted Yes-share clears the ratio threshold; `decline` is first-class
data but abstains from the ratio (it counts toward neither side).

On a resolved Yes the node's EFFECTIVE kind becomes the polled kind (e.g. `ought`),
which drives the Ought treatment in assess.py. A claim→Ought flip changes the
rating dimension (truth→endorsement), so `reopen_required` flags that the node's
prior truth-era ratings must be isolated via an explicit `reopen` (§2.2 "type-flip
opens a new era") — the existing era machinery then does the isolation.
"""
from __future__ import annotations

# Quorum: min Yes+No votes before a poll can resolve (mirrors lifecycle quorum).
DEFAULT_QUORUM = 5
# Ratio: reputation-weighted Yes-share needed to resolve Yes. 0.66 = a clear
# two-thirds supermajority of reputation, not a bare 50%+1 (a type re-assertion
# should be well-supported, not marginal).
DEFAULT_RATIO = 0.66


def _kind_of_question(question):
    """`"type:ought"` -> `"ought"`; non-type questions -> None (general primitive:
    only type questions carry a resolved *kind*; others resolve to a Yes/No fact)."""
    return question[len("type:"):] if question.startswith("type:") else None


def resolve_polls(state, true_r, *, quorum=DEFAULT_QUORUM, ratio=DEFAULT_RATIO,
                  prior=0.15):
    """Resolve every voted poll in `state["polls"]` against `true_r`.

    Returns {poll_key: {node, question, yes, no, decline, n_votes, yes_w, no_w,
    yes_share, resolved, resolved_kind, reopen_required}}. Dormant (no-vote) polls
    are omitted. Deterministic: pure function of the folded votes + True_R.
    """
    out = {}
    nodes = state.get("nodes", {})
    eras = state.get("eras", {})
    for key in sorted(state.get("polls", {})):
        poll = state["polls"][key]
        votes = poll["votes"]
        if not votes:
            continue
        yes = no = decline = 0
        yes_w = no_w = 0.0
        for agent, v in votes.items():
            val = v["value"]
            w = true_r.get(agent, prior)
            if val == "yes":
                yes += 1
                yes_w += w
            elif val == "no":
                no += 1
                no_w += w
            else:  # "decline" (or any non-yes/no) -- first-class, but abstains
                decline += 1
        n_votes = yes + no
        denom = yes_w + no_w
        yes_share = (yes_w / denom) if denom > 0 else None
        resolved = n_votes >= quorum and yes_share is not None and yes_share >= ratio
        kind = _kind_of_question(poll["question"])
        resolved_kind = kind if (resolved and kind is not None) else None
        node = poll["node"]
        # A flip needs an era bump when the node isn't already that kind in a
        # fresh (un-reopened) era -- surfaced so an explicit `reopen` completes it.
        current_kind = nodes.get(node, {}).get("kind")
        reopen_required = bool(
            resolved and resolved_kind is not None
            and (current_kind != resolved_kind or eras.get(node, 1) == 1)
            and resolved_kind == "ought")
        out[key] = {
            "node": node, "question": poll["question"],
            "yes": yes, "no": no, "decline": decline, "n_votes": n_votes,
            "yes_w": yes_w, "no_w": no_w, "yes_share": yes_share,
            "resolved": resolved, "resolved_kind": resolved_kind,
            "reopen_required": reopen_required,
        }
    return out


def resolved_ought_nodes(poll_result):
    """The set of node ids a poll has resolved to `ought` -- the resolved-Ought
    contribution to assess.py's effective ought set."""
    return {r["node"] for r in poll_result.values()
            if r["resolved_kind"] == "ought"}
