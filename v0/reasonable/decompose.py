"""Decomposition routing (SPEC-evidence-argument-ought-ghosts §2.3).

A categorical **type poll** (§2.2) that clears quorum but stays *split* -- the
reputation-weighted Yes-share sits in the ambiguous band, resolving neither Yes
(it's that type) nor No (it isn't) -- is the signal of a **persistent type
contestation**, which usually means an **is/ought conflation**: the node is
partly descriptive and partly prescriptive, so raters genuinely can't agree on
its single type. The routing response (per §1.3) is not to force a type but to
**decompose** the node -- split the is-claim from the ought, and ground the
ought on the is plus an explicit value premise (Hume-safe).

This is a thin read-layer classifier over `typepoll.resolve_polls`' output; it
consumes the poll proportion (a first moment, reliable at modest n -- §2.2), and
needs no dispersion signal. Detection + surfacing live here; the actual split is
an authoring act, guided by `candidate_hint`.
"""
from __future__ import annotations

from . import typepoll


def candidate_hint(question: str) -> str:
    """The §1.3 decomposition guidance for a split poll, by question type."""
    if question == "type:ought":
        return ("split into the descriptive is-claim + a separate ought, and ground the ought on the "
                "is-claim plus an explicit value premise (an ought may only be grounded by oughts/values)")
    return ("the node is contested between two categories -- split it so each category is its own node")


def decompose_candidates(poll_result: dict,
                         quorum: int = typepoll.DEFAULT_QUORUM,
                         ratio: float = typepoll.DEFAULT_RATIO) -> list[dict]:
    """Type polls that met quorum but stayed split -> is/ought-conflation
    decomposition candidates. `poll_result` is `assess.compute(...)["polls"]`.

    A poll is a candidate when it has >= `quorum` Yes+No votes and its
    reputation-weighted `yes_share` sits strictly inside `(1 - ratio, ratio)` --
    i.e. it resolved neither Yes (>= ratio) nor No (<= 1 - ratio). Resolved and
    under-quorum polls are not candidates.
    """
    lo, hi = 1.0 - ratio, ratio
    out = []
    for key in sorted(poll_result):
        r = poll_result[key]
        ys = r.get("yes_share")
        if ys is None or r["n_votes"] < quorum:
            continue
        if lo < ys < hi:
            out.append({
                "poll": key,
                "node": r["node"],
                "question": r["question"],
                "yes_share": round(ys, 3),
                "n_votes": r["n_votes"],
                "hint": candidate_hint(r["question"]),
            })
    return out
