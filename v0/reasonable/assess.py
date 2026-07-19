"""Assessment layer: reputation + weighted aggregation (ASSESSMENT-SPEC.md
§3-§4). ADDITIVE to the frozen v0 core -- this module is consulted by
`fold.to_graph_json()` to compute a parallel, derived layer (graded ratings,
per-agent reputation, weighted score aggregates) that sits alongside, and
never touches, the structural `agree`/`strength` consensus math in fold.py.

Nothing here reads the wall clock and nothing here uses a bare `set()` for
anything that feeds a floating-point sum: Python's `set` iteration order for
str/bytes keys depends on PYTHONHASHSEED, which is randomized *per process*
by default, so summing floats in a set's iteration order would make the
result vary run-to-run even for the identical input log -- silently breaking
BUILD-SPEC.md §3's "same log -> same graph.json, byte-for-byte" invariant the
moment two separate `graph.py` invocations happened to draw different seeds.
Plain dicts (insertion-ordered by language guarantee, independent of hash
seed) and lists are used everywhere instead, so the exact same arithmetic in
the exact same order runs every time, given the same events.jsonl.

The whole point of this layer (ASSESSMENT-SPEC.md §0, Entry 3) is that every
scale/rule/weight is a knob to be swept later -- `resolve_config()` is the
single place defaults live and get documented; `compute()` is the one fixed-
point loop that ties reputation and aggregation together.
"""
from __future__ import annotations

DEFAULT_ASSESSMENT_CONFIG = {
    "scale_max": 5.0,
    "phrasing_R_over_C_bias": 1.5,
    "reputation": {"prior": 0.15, "K": 8.0, "raw_blend": "mean"},
    "aggregation": {"weight_by": "true_r", "iterations": 12, "epsilon": 0.001},
}


def resolve_config(user_assessment: dict | None) -> dict:
    """Merge a user-supplied `assessment` config block (config.json's
    `"assessment"` key) over the documented defaults above. Missing config,
    or a missing individual knob within it, silently falls back to its
    default (ASSESSMENT-SPEC.md §6: "Missing config -> documented
    defaults."). One level of nested-dict merging for `reputation` and
    `aggregation`, so a caller can override e.g. just `K` without having to
    restate `prior`/`raw_blend` too."""
    cfg = {k: (dict(v) if isinstance(v, dict) else v) for k, v in DEFAULT_ASSESSMENT_CONFIG.items()}
    if not user_assessment:
        return cfg
    for k, v in user_assessment.items():
        if isinstance(v, dict) and isinstance(cfg.get(k), dict):
            cfg[k].update(v)
        else:
            cfg[k] = v
    return cfg


def _phrasing_target(nid: str, pid: str) -> str:
    return f"phrasing:{nid}:{pid}"


def _comment_target(cid: str) -> str:
    return f"comment:{cid}"


def _agents_seen(state: dict) -> list[str]:
    """Every agent id that ever acted (authored something or rated
    something), in first-seen order -- a dict-as-ordered-set (see module
    docstring for why never a bare `set()` here)."""
    seen: dict[str, None] = {}
    for nid in state["node_order"]:
        n = state["nodes"][nid]
        seen.setdefault(n["author"], None)
        for p in n["phrasings"]:
            seen.setdefault(p["_author"], None)
        for t in n["titles"]:
            seen.setdefault(t["_author"], None)
    for eid in state["edge_order"]:
        seen.setdefault(state["edges"][eid]["author"], None)
    for cid in state["comment_order"]:
        seen.setdefault(state["comments"][cid]["author"], None)
    for _target, dmap in state["ratings"].items():
        for _dim, amap in dmap.items():
            for agent in amap:
                seen.setdefault(agent, None)
    return list(seen.keys())


def _authored_items(state: dict) -> dict:
    """agent -> list of (target, dims) for everything they authored: their
    nodes AND edges (dim A -- amendment: edges gained graded Agreement too,
    see ASSESSMENT-SPEC.md's Amendments section), their phrasings + comments
    (dims R, C). Used both for the authoring-input (§3 `auth`, restricted to
    phrasings/comments' R below) and for the broader "ratings received on
    their items" half of `n` (confidence's evidence count, §3) -- which
    counts evidence about the agent from ANY of their authored content, nodes
    AND edges included. An edge's author thus earns reputation "received"
    credit from graded Agreement ratings on their edge the exact same way a
    node's author already did -- no edge-specific reputation code, just one
    more entry in this list, reusing the machinery unchanged."""
    out: dict[str, list] = {}
    for nid in state["node_order"]:
        n = state["nodes"][nid]
        out.setdefault(n["author"], []).append((nid, ("A",)))
        for p in n["phrasings"]:
            out.setdefault(p["_author"], []).append((_phrasing_target(nid, p["id"]), ("R", "C")))
    for eid in state["edge_order"]:
        e = state["edges"][eid]
        out.setdefault(e["author"], []).append((eid, ("A",)))
    for cid in state["comment_order"]:
        c = state["comments"][cid]
        out.setdefault(c["author"], []).append((_comment_target(cid), ("R", "C")))
    return out


def compute(state: dict, assessment_config: dict | None = None,
            anchors: dict | None = None) -> dict:
    """The ASSESSMENT-SPEC.md §3/§4 fixed-point loop.

    Returns:
      {
        "config": <resolved assessment config actually used>,
        "aggregate": {(target, dim): (mean_or_None, n)},
        "true_r": {agent: float},
        "accounts": [{"agent", "true_r", "raw_r", "confidence",
                       "n_assessments", "authored", "rated"}, ...]  (sorted
                      by agent id, for a stable snapshot regardless of any
                      incidental dict/event ordering)
      }
    """
    cfg = resolve_config(assessment_config)
    # SPEC-evidence-argument-ought-ghosts §2.1 (Ought -> endorsement): Ought nodes are
    # rated on ENDORSEMENT (a value), not truth. Two consequences, both below: (a) their
    # A aggregate is DEMOCRATIC (unweighted), and (b) their ratings do NOT feed truth-
    # reputation. Weighting a value by truth-competence -- or letting a value-endorsement
    # earn truth-reputation -- is a category error + minority-suppression risk. Completes
    # the Evidence<->Ought symmetry: Evidence maximally rep/anchor-weighted, Ought minimally.
    from reasonable import fold as _fold
    ought_nodes = {nid for nid, nd in state.get("nodes", {}).items()
                   if _fold.is_ought_kind(nd.get("kind"))}
    # Rating-input reputation signal (ASSESSMENT-SPEC §3, amended): when anchors are
    # configured (`assessment.anchors` = {node: truth}, or passed in), the rating
    # input is DISCRIMINATION vs the ANCHORED consensus -- the validated competence
    # signal -- instead of `align` (agreement with the True_R-weighted aggregate,
    # which is the tyranny-of-median rule: valid only against an anchored reference,
    # it inverts on a biased crowd; see FINDINGS-SYNTHESIS §1). No anchors -> `align`
    # unchanged (backward-compatible; every anchor-free dataset is byte-identical).
    if anchors is None:
        anchors = (assessment_config or {}).get("anchors")
    disc = None
    cal_consensus = None
    used_calibration = False
    if anchors:
        from reasonable import assessment as _assessment
        # Calibration is computed ONCE (loop-independent -- it depends only on
        # ratings + anchors, not True_R): it feeds BOTH the discrimination
        # reputation signal AND the node-Agreement aggregate below.
        # The identifiability guard may DECLINE (consensus=None) when the anchor
        # truths lack the spread to identify a per-rater affine fit -- e.g. an
        # all-settled-facts anchor set clustered high (covid). In that case we
        # fall back to the raw/align path, byte-identical to the anchor-free run.
        cal_consensus = _assessment.calibrated_consensus(state, anchors)["consensus"]
        used_calibration = cal_consensus is not None
        if used_calibration:
            disc = _assessment.discrimination_scores(state, consensus=cal_consensus, exclude=ought_nodes)
    prior = float(cfg["reputation"]["prior"])
    K = float(cfg["reputation"]["K"])
    raw_blend = cfg["reputation"].get("raw_blend", "mean")
    weight_by = cfg["aggregation"].get("weight_by", "true_r")
    iterations = int(cfg["aggregation"]["iterations"])
    epsilon = float(cfg["aggregation"]["epsilon"])
    scale_max = float(cfg.get("scale_max", 5.0)) or 5.0

    ratings = state["ratings"]
    agents = _agents_seen(state)
    authored_items = _authored_items(state)
    # auth input only ever looks at R on phrasings/comments (ASSESSMENT-SPEC
    # §3: "the ... mean R of the agent's authored phrasings + comments").
    authored_rc_targets: dict[str, list] = {}
    for agent, items in authored_items.items():
        for target, dims in items:
            if "R" in dims:
                authored_rc_targets.setdefault(agent, []).append(target)

    # Every (target, dim) that has at least one rating (numeric or abstain),
    # and the numeric (non-abstain) raters for it -- built once; abstains are
    # real superseding values already resolved away by fold() (only the
    # latest-by-seq value per (agent, target, dim) survives into `ratings`),
    # so "numeric" here is simply "not the literal 'abstain' sentinel".
    all_pairs: list[tuple[str, str]] = []
    numeric: dict[tuple, list] = {}
    for target, dmap in ratings.items():
        for dim, amap in dmap.items():
            all_pairs.append((target, dim))
            numeric[(target, dim)] = [(a, v) for a, v in amap.items() if v != "abstain"]

    # Per-agent: how many ratings did they GIVE (their "own scored ratings",
    # §3), and what did they rate (for the alignment input, §3 `align`).
    given_count: dict[str, int] = {}
    given_pairs: dict[str, list] = {}
    for target, dim in all_pairs:
        if dim == "A" and target in ought_nodes:
            continue  # §2.1: endorsing a value neither builds nor spends truth-reputation
        for a, v in numeric[(target, dim)]:
            given_count[a] = given_count.get(a, 0) + 1
            given_pairs.setdefault(a, []).append((target, dim, v))

    # Per-agent: how many ratings did they RECEIVE on anything they authored
    # (nodes' A, phrasings'/comments' R & C) -- the other half of `n`.
    received_count: dict[str, int] = {}
    for agent, items in authored_items.items():
        total = 0
        for target, dims in items:
            for dim in dims:
                if dim == "A" and target in ought_nodes:
                    continue  # §2.1: endorsements received on an authored Ought aren't truth-assessments
                total += len(numeric.get((target, dim), []))
        received_count[agent] = total

    def _aggregate_pass(true_r: dict) -> dict:
        agg = {}
        for target, dim in all_pairs:
            raters = numeric[(target, dim)]
            n = len(raters)
            if n == 0:
                agg[(target, dim)] = (None, 0)
                continue
            if dim == "A" and target in ought_nodes:
                # Ought -> ENDORSEMENT: DEMOCRATIC (unweighted, one-agent-one-vote)
                # aggregate -- never truth/reputation-weighted (§2.1). Overrides both the
                # calibrated and True_R-weighted paths below. (Anti-sybil / good-faith
                # identity weighting is the future refinement once an identity layer
                # exists; unweighted is the honest democratic default now.)
                mean = sum(v for _a, v in raters) / n
            elif cal_consensus is not None and dim == "A" and target.startswith("n") \
                    and target in cal_consensus:
                # anchored: the node-Agreement aggregate is the CALIBRATED consensus
                # (per-rater affine un-distortion on anchors + inverse-residual-
                # variance weight) -- the validated aggregator that survives a
                # biased/coordinated majority (FINDINGS-SYNTHESIS §2). Other dims
                # (R/C, edges, groups -- no anchors) keep `weight_by` below.
                mean = cal_consensus[target]
            elif weight_by == "true_r":
                wsum = 0.0
                vsum = 0.0
                for a, v in raters:
                    w = true_r.get(a, prior)
                    wsum += w
                    vsum += w * v
                mean = (vsum / wsum) if wsum > 0 else (sum(v for _a, v in raters) / n)
            else:  # "uniform" -- plain unweighted mean (the other pluggable option)
                mean = sum(v for _a, v in raters) / n
            agg[(target, dim)] = (mean, n)
        return agg

    def _raw_r(auth, align) -> float:
        if raw_blend == "auth_only":
            return auth if auth is not None else prior
        if raw_blend == "align_only":
            return align if align is not None else prior
        # default "mean": mean of whichever inputs are non-null; both null -> prior
        vals = [v for v in (auth, align) if v is not None]
        return (sum(vals) / len(vals)) if vals else prior

    true_r = {a: prior for a in agents}
    aggregate: dict = {}
    accounts_by_agent: dict = {}

    for _iteration in range(max(iterations, 1)):
        aggregate = _aggregate_pass(true_r)
        new_true_r = {}
        for a in agents:
            r_scores = []
            for target in authored_rc_targets.get(a, []):
                mean, _n = aggregate.get((target, "R"), (None, 0))
                if mean is not None:
                    r_scores.append(mean / scale_max)
            auth = (sum(r_scores) / len(r_scores)) if r_scores else None

            diffs = []
            for target, dim, v in given_pairs.get(a, []):
                mean, n = aggregate[(target, dim)]
                if mean is None or n < 2:
                    continue
                diffs.append(abs(v - mean) / scale_max)
            align = (1.0 - sum(diffs) / len(diffs)) if diffs else None

            # anchored -> discrimination vs the anchored consensus; else -> align
            rating_input = disc.get(a) if disc is not None else align
            raw_r = _raw_r(auth, rating_input)
            n_assessments = received_count.get(a, 0) + given_count.get(a, 0)
            denom = n_assessments + K
            conf = (n_assessments / denom) if denom > 0 else (1.0 if n_assessments > 0 else 0.0)
            tr = prior + conf * (raw_r - prior)

            new_true_r[a] = tr
            accounts_by_agent[a] = {
                "agent": a,
                "true_r": tr,
                "raw_r": raw_r,
                "confidence": conf,
                "n_assessments": n_assessments,
                "authored": len(authored_items.get(a, [])),
                "rated": given_count.get(a, 0),
            }

        delta = 0.0
        for a in agents:
            d = abs(new_true_r[a] - true_r[a])
            if d > delta:
                delta = d
        true_r = new_true_r
        if delta < epsilon:
            break

    # SPEC-evidence §2.2: resolve categorical type-polls at the converged True_R
    # (resolution is reputation-weighted). A poll resolved to `ought` joins the
    # effective Ought set, so the final aggregate pass gives that node the
    # democratic endorsement treatment. Poll activity exists only in graphs that
    # carry `poll_vote` events -- none of the flagship graphs do -- so this is a
    # no-op there and every poll-free dataset stays byte-identical.
    #
    # SCOPE (documented): resolution runs once, after the reputation loop, so a
    # resolved-Ought node gets the democratic AGGREGATION here, but the reputation
    # loop above already ran with the authored-Ought set -- i.e. its pre-flip
    # truth-ratings still counted toward True_R. That second-order effect is
    # deferred (a full fixed point over resolution is next-version); in practice
    # an explicit `reopen` on the flip isolates those ratings into a closed era.
    from reasonable import typepoll as _typepoll
    poll_result = _typepoll.resolve_polls(state, true_r)
    ought_nodes.update(_typepoll.resolved_ought_nodes(poll_result))

    # One final aggregate pass at the converged (or iteration-capped) True_R
    # values, so the snapshot's scores reflect the same weights the last
    # reputation update was computed from.
    aggregate = _aggregate_pass(true_r)

    accounts = [accounts_by_agent[a] for a in sorted(agents)]
    return {
        "config": cfg,
        "aggregate": aggregate,
        "true_r": true_r,
        "accounts": accounts,
        "used_calibration": used_calibration,
        "polls": poll_result,
    }
