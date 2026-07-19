"""Validated assessment machinery, live on the graph (the stack from
`FINDINGS-SYNTHESIS.md` §2/§8, promoted out of the offline experiment scripts).

ADDITIVE and SELECTABLE: this module does not touch the frozen True_R loop in
`assess.py` or the structural `agree` math in `fold.py`. It consumes the same
fold `state` (`state["ratings"][target][dim][agent] = value`) and provides the
three components the adversarial + dispersion work validated:

  1. calibrated_consensus  -- per-rater affine un-distortion on anchors + inverse-
     residual-variance weighting (beats align-to-consensus / winner-take-all;
     robust to a biased or coordinated majority that fails the anchors).
  2. detect_camps + camp_contested -- spectral split of the rater-agreement matrix
     (the BELIEF-CAMP structure), and the corrected "contested" signal: a node is
     contested when the camps disagree on it, NOT when raw stdev is high (raw stdev
     is lens/offset noise on a non-camp panel -- see the dispersion-regimes note).
  3. certainty_guard -- flag a verdict hardened past what the oracle warrants (the
     over-certainty / consensus-entrenchment attack calibration can't stop and MAE
     can't see).

Determinism (same discipline as assess.py): no wall-clock, no RNG, no float sums
in set-iteration order. The spectral power iteration uses a fixed deterministic
seed vector so the same log yields the same result byte-for-byte.
"""
from __future__ import annotations

import math

MIDPOINT = 2.5  # on the 0-5 A scale


# ---------------------------------------------------------------- primitives
def _mean(v):
    v = list(v)
    return sum(v) / len(v) if v else 0.0


def _pstdev(v):
    v = list(v)
    if len(v) < 2:
        return 0.0
    m = _mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / len(v))


def _pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = _mean(xs), _mean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def _fit_affine(xs, ys, lam=2.0):
    """Ridge-toward-identity affine fit; returns (slope, intercept, resid_sd).
    Fewer than 3 points -> identity, sd None (untrustworthy)."""
    n = len(xs)
    if n < 3:
        return 1.0, 0.0, None
    mx, my = _mean(xs), _mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = (sxy + lam) / (sxx + lam)
    inter = my - slope * mx
    resid = [y - (slope * x + inter) for x, y in zip(xs, ys)]
    sd = math.sqrt(sum(r * r for r in resid) / n)
    return slope, inter, sd


def _clip(v, lo=0.0, hi=5.0):
    return max(lo, min(hi, v))


def node_a_matrix(ratings, dim="A"):
    """{node: {agent: value}} for numeric (non-abstain) `dim` ratings on n-nodes.
    Accepts either a fold `state` or its `state["ratings"]` (unwraps a state so
    every entry point is call-convention-safe)."""
    if "ratings" in ratings and isinstance(ratings["ratings"], dict):
        ratings = ratings["ratings"]
    out = {}
    for target, dmap in ratings.items():
        if not target.startswith("n") or dim not in dmap:
            continue
        cell = {a: float(v) for a, v in dmap[dim].items()
                if v != "abstain" and isinstance(v, (int, float))}
        if cell:
            out[target] = cell
    return out


# ---------------------------------------------------------------- calibration
MIN_ANCHOR_SPREAD = 2.0  # identifiability floor for calibrated_consensus (0-5 scale)


def calibrated_consensus(ratings, anchors, gamma=1.0, tol_var=0.05, lam=2.0,
                         min_spread=MIN_ANCHOR_SPREAD):
    """Per-rater affine calibration on `anchors` ({node: truth}) + inverse-
    residual-variance weighting. Returns:
        {"consensus": {node: value} | None,
         "raters": {agent: (slope, intercept, sd, weight)},
         "calibrated": bool, "anchor_spread": float}
    A rater who fits the anchors badly (or fails to rate >=3 of them) is down-
    weighted; a coordinated/biased bloc that also lies on the anchors gets an
    inverted/near-zero weight -- this is the defense that survives a 60% majority.

    IDENTIFIABILITY GUARD: a per-rater affine un-distortion (slope + offset) is
    only identifiable when the anchor *truths* span a real range. If every anchor
    is a settled fact clustered at one end (as in support-only cooperative graphs,
    whose confidently-oracle-able nodes are all high-agreement), the fit has no
    slope leverage: it cannot tell an additive rater bias from scale compression
    from no distortion, and collapses every node toward the anchor-truth mean --
    degrading a raw aggregate that was already good (covid: raw MAE 0.82 ->
    calibrated 1.28; even offset-only stays worse at 1.08 -- the distortion is
    genuinely unidentifiable, not just mis-fit). When the anchor-truth spread is
    below `min_spread` we DECLINE to calibrate (consensus=None) and the caller
    falls back to the raw aggregate. The validated adversarial defense is
    unaffected: its anchors span the scale (eggs-p8 spread 3.28, incl. a truth-1.4
    low anchor) -- well above the floor, so calibration still engages there.
    """
    truths = list(anchors.values())
    spread = (max(truths) - min(truths)) if len(truths) >= 2 else 0.0
    if spread < min_spread:
        return {"consensus": None, "raters": {}, "calibrated": False,
                "anchor_spread": spread}
    mat = node_a_matrix(ratings)
    agents = sorted({a for n in mat for a in mat[n]})
    maps = {}
    for a in agents:
        pts = [(mat[n][a], anchors[n]) for n in anchors if n in mat and a in mat[n]]
        s, b, sd = _fit_affine([p[0] for p in pts], [p[1] for p in pts], lam)
        w = (1.0 / (sd * sd + tol_var)) ** gamma if sd is not None else (1.0 / (1.0 + tol_var)) ** gamma
        maps[a] = (s, b, sd, w)
    consensus = {}
    for n in sorted(mat, key=_node_key):
        num = den = 0.0
        for a, v in mat[n].items():
            s, b, sd, w = maps[a]
            num += w * _clip(s * v + b)
            den += w
        if den > 0:
            consensus[n] = num / den
    return {"consensus": consensus, "raters": maps, "calibrated": True,
            "anchor_spread": spread}


def _node_key(nid):
    try:
        return (0, int(nid[1:]))
    except ValueError:
        return (1, nid)


# ---------------------------------------------------------------- discrimination
def _rank(xs):
    """Average (fractional) ranks, 1-based, deterministic ties handling."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def spearman(xs, ys):
    return _pearson(_rank(xs), _rank(ys))


def discrimination_scores(state, anchors=None, consensus=None, min_overlap=5, exclude=None):
    """Per-rater competence = how well a rater's ORDERING of claims tracks the
    ANCHORED consensus (calibrated_consensus), rank-correlated and mapped to [0,1].
    This is the validated reputation signal (FINDINGS-SYNTHESIS §2): it MUST be
    vs the anchored consensus, never the raw crowd — against the raw crowd it
    rewards agreeing with the (possibly biased) majority and *inverts* on a biased
    crowd. Pass a precomputed `consensus` to avoid recomputing calibration.
    Returns {agent: score in [0,1]} (agents with < min_overlap shared nodes
    are omitted -> caller falls back)."""
    if consensus is None:
        consensus = calibrated_consensus(state, anchors)["consensus"]
    if consensus is None:  # calibration declined (low anchor spread) -> no scores
        return {}
    exclude = exclude or set()
    mat = node_a_matrix(state)
    agents = sorted({a for n in mat for a in mat[n]})
    out = {}
    for a in agents:
        shared = [n for n in mat if a in mat[n] and n in consensus and n not in exclude]
        if len(shared) >= min_overlap:
            rho = spearman([mat[n][a] for n in shared], [consensus[n] for n in shared])
            out[a] = (rho + 1.0) / 2.0
    return out


# ---------------------------------------------------------------- camp detection
def _spectral_split(mat, min_shared=8):
    """Two-cluster spectral split of the rater-agreement (pearson) matrix.
    Deterministic: fixed seed vector, no RNG. Returns (agents, bloc: {agent: 0/1})."""
    agents = sorted({a for n in mat for a in mat[n]})
    idx = {a: i for i, a in enumerate(agents)}
    k = len(agents)
    if k < 2:
        return agents, {a: 0 for a in agents}
    prof = {a: {n: mat[n][a] for n in mat if a in mat[n]} for a in agents}
    A = [[0.0] * k for _ in range(k)]
    for i, a in enumerate(agents):
        for j in range(i + 1, k):
            b = agents[j]
            sh = [n for n in prof[a] if n in prof[b]]
            if len(sh) >= min_shared:
                r = _pearson([prof[a][n] for n in sh], [prof[b][n] for n in sh])
                A[i][j] = A[j][i] = r
    rowm = [_mean(r) for r in A]
    gm = _mean(rowm)
    C = [[A[i][j] - rowm[i] - rowm[j] + gm for j in range(k)] for i in range(k)]
    # deterministic seed vector (index-derived, mean-zero), then power-iterate
    v = [((i * 2654435761) % 1000) / 1000.0 - 0.5 for i in range(k)]
    for _ in range(300):
        nv = [sum(C[i][j] * v[j] for j in range(k)) for i in range(k)]
        nm = math.sqrt(sum(x * x for x in nv)) or 1.0
        v = [x / nm for x in nv]
    return agents, {a: (0 if v[idx[a]] >= 0 else 1) for a in agents}


def detect_camps(ratings, min_shared=8):
    """Belief-camp structure of the rater population. Returns:
        {"blocs": {agent: 0/1}, "sizes": (n0, n1), "split_strength": float,
         "between_group_fraction": float}
    split_strength = mean within-camp agreement - mean between-camp agreement
    (0 ~ one crowd / no real divide; higher = a sharper belief split).
    between_group_fraction = share of per-node dispersion that is systematic
    between-camp (the dispersion-regimes diagnostic: high => dispersion is a valid
    contested signal; low => it's lens/offset noise)."""
    mat = node_a_matrix(ratings)
    agents, blocs = _spectral_split(mat, min_shared)
    prof = {a: {n: mat[n][a] for n in mat if a in mat[n]} for a in agents}
    within, between = [], []
    for i, a in enumerate(agents):
        for b in agents[i + 1:]:
            sh = [n for n in prof[a] if n in prof[b]]
            if len(sh) >= min_shared:
                r = _pearson([prof[a][n] for n in sh], [prof[b][n] for n in sh])
                (within if blocs[a] == blocs[b] else between).append(r)
    strength = (_mean(within) - _mean(between)) if (within and between) else 0.0
    bt, wn = [], []
    for n in mat:
        by = {}
        for a in mat[n]:
            by.setdefault(blocs[a], []).append(mat[n][a])
        by = {g: vs for g, vs in by.items() if vs}
        if len(by) < 2:
            continue
        gm = _mean([mat[n][a] for a in mat[n]])
        bt.append(_mean([(_mean(vs) - gm) ** 2 for vs in by.values()]))
        wn.append(_mean([(_pstdev(vs) ** 2) for vs in by.values()]))
    B, W = _mean(bt), _mean(wn)
    frac = (B / (B + W)) if (B + W) > 0 else 0.0
    n0 = sum(1 for a in agents if blocs[a] == 0)
    return {"blocs": blocs, "sizes": (n0, len(agents) - n0),
            "split_strength": round(strength, 3),
            "between_group_fraction": round(frac, 3)}


def camp_contested(ratings, blocs, threshold=1.0, min_per_camp=2):
    """Nodes the two belief-camps DISAGREE on -> the corrected contested signal
    (supersedes the raw-stdev trigger). Returns a sorted list of
    {node, camp0_mean, camp1_mean, gap}."""
    mat = node_a_matrix(ratings)
    out = []
    for n in sorted(mat, key=_node_key):
        c0 = [mat[n][a] for a in mat[n] if blocs.get(a) == 0]
        c1 = [mat[n][a] for a in mat[n] if blocs.get(a) == 1]
        if len(c0) >= min_per_camp and len(c1) >= min_per_camp:
            gap = abs(_mean(c0) - _mean(c1))
            if gap > threshold:
                out.append({"node": n, "camp0_mean": round(_mean(c0), 2),
                            "camp1_mean": round(_mean(c1), 2), "gap": round(gap, 2)})
    return sorted(out, key=lambda d: -d["gap"])


# ---------------------------------------------------------------- certainty guard
def _decisiveness(x):
    return abs(x - MIDPOINT)


def certainty_guard(consensus, reference_means, reference_sds, verdict_nodes,
                    frontier_nodes, verdict_tol=0.15, frontier_tol_floor=0.2,
                    verdict_thresh=0.1, frontier_thresh=0.2):
    """Flag a verdict hardened past what the oracle warrants. Fires on a wrong-
    leader FLIP or on hardening beyond the warranted margin (verdict signal), or on
    mean unwarranted decisiveness over the contested frontier (corroborating).
    Uses only the aggregate + oracle reference -- no attacker knowledge."""
    cv = {n: consensus[n] for n in verdict_nodes if n in consensus}
    ov = {n: reference_means[n] for n in verdict_nodes if n in reference_means}
    v_score, is_flip = 0.0, False
    if len(cv) >= 2 and len(ov) >= 2:
        lead_c = max(cv, key=cv.get)
        lead_o = max(ov, key=ov.get)
        margin_c = max(cv.values()) - min(cv.values())
        margin_o = max(ov.values()) - min(ov.values())
        if lead_c != lead_o and margin_c > verdict_tol:
            v_score, is_flip = round(margin_c + margin_o, 3), True
        else:
            v_score = round(max(0.0, margin_c - margin_o - verdict_tol), 3)
    per = {}
    for n in frontier_nodes:
        if n in consensus and n in reference_means:
            tol = frontier_tol_floor + reference_sds.get(n, 0.0)
            per[n] = max(0.0, _decisiveness(consensus[n]) - _decisiveness(reference_means[n]) - tol)
    f_mean = round(_mean(per.values()), 3) if per else 0.0
    reason = []
    if v_score > verdict_thresh:
        reason.append("FLIP" if is_flip else "verdict-hardening")
    if f_mean > frontier_thresh:
        reason.append("frontier-hardening")
    return {"fired": bool(reason), "verdict_score": v_score, "is_flip": is_flip,
            "frontier_mean": f_mean, "reason": "+".join(reason) or "-"}


# ---------------------------------------------------------------- convenience
def report(state, anchors=None, reference=None, verdict_nodes=None, frontier_nodes=None):
    """One-call advanced assessment over a fold `state`. Camp-detection always
    runs (no oracle needed); calibration + guard run when an anchors/reference is
    given. `anchors` = {node: truth}; `reference` = {node: {"mean", "sd"}}."""
    ratings = state["ratings"]
    camps = detect_camps(ratings)
    out = {"camps": camps,
           "contested": camp_contested(ratings, camps["blocs"])}
    if anchors:
        cal = calibrated_consensus(ratings, anchors)
        out["calibrated_consensus"] = cal["consensus"]
        if reference and verdict_nodes:
            means = {n: reference[n]["mean"] for n in reference}
            sds = {n: reference[n].get("sd", 0.0) for n in reference}
            out["certainty_guard"] = certainty_guard(
                cal["consensus"], means, sds, verdict_nodes, frontier_nodes or [])
    return out
