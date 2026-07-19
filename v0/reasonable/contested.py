"""Shared contestedness service — the single 'is this settled / contested /
refuted' verdict for BOTH the type-poll (SPEC-evidence-argument-ought-ghosts §2.2/
§2.3) and the ghost trigger (§3.1), so the two threads build on one implementation
rather than duplicating (their §5 "share the threshold plumbing" ask).

It composes the reliable signals we validated (dispersion-regimes/ retired raw
rating stdev):
  - STRUCTURAL contestedness (lifecycle.structurally_contested): a node is a live
    argument iff it is a rival positive claim in an antithesis set. Deterministic,
    always available.
  - BELIEF-CAMP contestedness (assessment.detect_camps / camp_contested): the nodes
    the reputation-weighted camps genuinely disagree on, plus the between-camp
    variance diagnostic (high => the disagreement is real, not lens/offset noise).
  - the node/edge's OWN Agreement aggregate (for the "settled-against" / ghost floor).

Per-node verdict:
  - "contested"      -> a live argument (structural rivalry or camps disagree). ALIVE.
  - "settled"        -> converged, not refuted. ALIVE.
  - "ghost_eligible" -> refuted on its OWN Agreement (low, settled, and NOT an
                        antithesis rival). The §3.1 ghost candidate.
Antithesis members are NEVER ghost_eligible here: a rival that lost its stack is
"less supported, not wrong" (§3.1) and stays live (minority-truth / Semmelweis
protection). §3.1 can tune a more aggressive rule from the raw signals we expose;
this default errs toward preserving minority positions.
"""
from __future__ import annotations

from reasonable import assessment, lifecycle


def _node_key(nid):
    try:
        return (0, int(nid[1:]))
    except (ValueError, IndexError):
        return (1, nid)


def assess_contestedness(state, aggregate, *, camp_gap_threshold=1.0,
                         ghost_floor=1.5, midpoint=2.5):
    """Returns {"split_strength", "between_group_fraction", "nodes": {id: verdict}}.
    `aggregate` is assess.compute(...)["aggregate"] = {(target, dim): (mean, n)}."""
    struct = lifecycle.structurally_contested(state)          # antithesis members
    camps = assessment.detect_camps(state)
    camp_hits = {d["node"]: d["gap"]
                 for d in assessment.camp_contested(state, camps["blocs"], camp_gap_threshold)}

    own = {t: m for (t, dim), (m, n) in aggregate.items()
           if dim == "A" and m is not None and (t.startswith("n") or t.startswith("e"))}

    # antithesis co-membership -> best rival Agreement (for §3.4 relative dimming)
    set_members = {sid: [m["node"] for m in s.get("members", [])]
                   for sid, s in state.get("sets", {}).items()}
    sets_of = {}
    for sid, mem in set_members.items():
        for n in mem:
            sets_of.setdefault(n, []).append(sid)

    verdicts = {}
    for t in sorted(own, key=_node_key):
        is_member = t in struct
        camp_gap = camp_hits.get(t)
        is_contested = is_member or (camp_gap is not None)

        best_rival = None
        for sid in sets_of.get(t, []):
            for m in set_members[sid]:
                if m != t and m in own:
                    best_rival = own[m] if best_rival is None else max(best_rival, own[m])
        lost_rival = best_rival is not None and own[t] < best_rival

        if is_contested:
            verdict = "contested"
        elif own[t] < ghost_floor:
            verdict = "ghost_eligible"
        else:
            verdict = "settled"

        verdicts[t] = {
            "verdict": verdict,
            "own_agreement": round(own[t], 3),
            "structural_contested": is_member,
            "camp_gap": round(camp_gap, 3) if camp_gap is not None else None,
            "best_rival_agreement": round(best_rival, 3) if best_rival is not None else None,
            "lost_rival": lost_rival,
        }

    return {
        "split_strength": camps["split_strength"],
        "between_group_fraction": camps["between_group_fraction"],
        "nodes": verdicts,
    }


def summary(result):
    """Compact counts by verdict, for a CLI/readout."""
    from collections import Counter
    return dict(Counter(v["verdict"] for v in result["nodes"].values()))
