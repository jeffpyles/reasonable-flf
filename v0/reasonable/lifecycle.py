"""Phase-2 mechanics: lifecycle states, dispersion, eras, blocs (PHASE2-SPEC.md
§1, §2, §4, §5). ADDITIVE to the ASSESSMENT-SPEC.md layer in assess.py -- this
module never recomputes the True_R-weighted mean itself (that stays exactly
assess.compute()'s job); it wraps each `(target, dim)` aggregate that assess
already produced with the rest of the phase-2 envelope: rater-count-derived
`state`, raw-rating `stdev`, per-era `history`, and per-`--bloc` breakdown.

Nothing here reads the wall clock. Determinism follows the same discipline as
assess.py: plain dicts/lists only, iterated in the log's own seq order (never
a bare `set()` for anything that feeds a float sum), so `same events.jsonl +
same config -> byte-identical graph.json` (PHASE2-SPEC.md §1) holds for this
layer too.
"""
from __future__ import annotations

from . import heat as heat_mod

DEFAULT_PHASE2_CONFIG = {
    "quorum": 5,
    "confirm": 15,
    "contested_threshold": 1.0,
    "heat_half_life": 300.0,
    "heat_diffuse": 0.15,
    "cold_factor": 0.5,
    "nudge_distance": 1.5,
    "bloc_min_ratings": 3,
    # Static-artifact mode. In a live wiki, `settled` is gated on the target
    # being "cold" (content-heat decayed => nobody is actively editing this
    # region). In a FROZEN presentation graph nothing is live, so content-heat
    # only tracks BUILD ORDER and that gate makes `settled` vs `provisional` an
    # artifact of when a node was authored. With `static: true` the cold gate is
    # skipped: a converged, non-contested, fully-rated target reads `settled`
    # outright. The quorum/confirm gates (sealed/provisional for thin evidence)
    # and the contested verdict are untouched.
    "static": False,
}


def resolve_config(user_phase2: dict | None) -> dict:
    """Merge a user-supplied `phase2` config block over the documented
    defaults above -- same one-level-merge convention as
    assess.resolve_config (there is nothing nested here to merge deeper
    than the top level, so a plain `dict.update` copy suffices)."""
    cfg = dict(DEFAULT_PHASE2_CONFIG)
    if user_phase2:
        cfg.update(user_phase2)
    return cfg


# --- small math helpers -----------------------------------------------------

def population_stdev(values: list[float]) -> float | None:
    """Population stdev (PHASE2-SPEC.md §2: "stdev of the raw ratings, not
    True_R-weighted"), null when n < 2."""
    n = len(values)
    if n < 2:
        return None
    mean = sum(values) / n
    var = sum((v - mean) ** 2 for v in values) / n
    return var ** 0.5


def structurally_contested(state: dict) -> set:
    """Targets that are rival positive claims in a live antithesis set (>=2
    members) -- the RELIABLE, deterministic, always-available "this claim is a
    live argument" signal. This is the corrected contested trigger: per the
    dispersion-regimes finding, raw rating stdev tracks contestedness only when
    dispersion is belief-camp-driven and is lens/offset noise otherwise, so stdev
    is demoted to a conservative secondary net (see block_for). The population-
    level camp-belief signal (spectral) lives in reasonable/assessment.py, out of
    the per-target fold hot path.

    Deterministic (set membership only, never a float-sum order); cached on the
    per-fold `state` so the block loop stays O(1) per target."""
    cached = state.get("_structurally_contested")
    if cached is not None:
        return cached
    out = set()
    for s in state.get("sets", {}).values():
        members = s.get("members", [])
        if len(members) >= 2:
            for m in members:
                out.add(m["node"] if isinstance(m, dict) else m)
    state["_structurally_contested"] = out
    return out


def median(values: list[float]) -> float | None:
    if not values:
        return None
    vs = sorted(values)
    n = len(vs)
    mid = n // 2
    if n % 2 == 1:
        return vs[mid]
    return (vs[mid - 1] + vs[mid]) / 2.0


def bloc_f_statistic(groups: dict[str, list[float]]) -> float:
    """One-way-ANOVA-style F ratio (PHASE2-SPEC.md §5: "ratio of between-bloc
    to within-bloc variance, F-style"):

        F = (SS_between / (k-1)) / (SS_within / (N-k))

    `groups` maps bloc id -> list of that bloc's raw (numeric, non-abstain)
    values in the target's CURRENT era; callers already filter to only the
    qualifying blocs (>= bloc_min_ratings each, >= 2 such blocs) before
    calling this, so k >= 2 and every group has >= 3 values here (N-k >= k
    >= 2, so the within-group degrees of freedom is always positive -- no
    degenerate-df guard needed).

    A small epsilon is added to the within-group mean square so the ratio
    stays a finite, JSON-serializable float even in the edge case where
    every rater inside every bloc agrees EXACTLY (SS_within == 0) but the
    blocs disagree with each other -- the maximally divergent case, which
    should read as a very large (not literally infinite/NaN) number.
    """
    all_vals = [v for vs in groups.values() for v in vs]
    n_total = len(all_vals)
    k = len(groups)
    grand_mean = sum(all_vals) / n_total
    ss_between = 0.0
    ss_within = 0.0
    for vs in groups.values():
        gm = sum(vs) / len(vs)
        ss_between += len(vs) * (gm - grand_mean) ** 2
        ss_within += sum((v - gm) ** 2 for v in vs)
    ms_between = ss_between / (k - 1)
    ms_within = ss_within / (n_total - k)
    EPS = 1e-9
    return ms_between / (ms_within + EPS)


# --- representative "node" for a rated target's cold check ------------------

def representative_content_heat(target_id: str, state: dict, content_heat: dict) -> float:
    """The content-heat value used to decide whether a rated TARGET's node is
    "cold" (PHASE2-SPEC.md §1/§3). Every rateable target maps to one or two
    underlying nodes:
      - a node target -> itself
      - an edge target -> the mean of its two endpoints' content heat
        (documented choice: an edge has no node of its own, and averaging
        its endpoints is the natural "how cold is the neighborhood this
        edge sits in" reading)
      - `phrasing:<node>:<pid>` / a comment on a node -> that node
      - a comment on an edge -> that edge's endpoint-mean (recurses)
      - `group:<gid>` -> the group's `to` node (same node the group's
        Dependent is; matches how an edge target already reduces to its own
        pair of nodes)
    """
    if target_id.startswith("phrasing:"):
        _, nid, _pid = target_id.split(":", 2)
        return content_heat.get(nid, 0.0)
    if target_id.startswith("comment:"):
        cid = target_id.split(":", 1)[1]
        c = state["comments"].get(cid)
        if c is None:
            return 0.0
        return representative_content_heat(c["target"], state, content_heat)
    if target_id.startswith("group:"):
        gid = target_id.split(":", 1)[1]
        g = state["groups"].get(gid)
        if g is None:
            return 0.0
        return content_heat.get(g["to"], 0.0)
    if target_id in state["nodes"]:
        return content_heat.get(target_id, 0.0)
    e = state["edges"].get(target_id)
    if e is not None:
        a = content_heat.get(e["from"], 0.0)
        b = content_heat.get(e["to"], 0.0)
        return (a + b) / 2.0
    return 0.0


# --- the per-(target, dim) block ---------------------------------------------

def block_for(target_id: str, dim: str, state: dict, aggregate: dict,
              content_heat: dict, site_median_content: float | None, cfg: dict) -> dict:
    """The full PHASE2-SPEC.md §1/§2/§4/§5 envelope for one rated
    `(target, dim)` pair: `{mean, n, stdev, state, era, history, blocs,
    bloc_divergence}`. Works uniformly whether or not the target has ever
    been rated (a never-rated target still gets a real block: era 1,
    n=0, state="sealed", empty history/blocs) -- callers don't need to
    special-case "nothing rated yet"."""
    era = state["eras"].get(target_id, 1)
    mean, n = aggregate.get((target_id, dim), (None, 0))

    era_map = state.get("ratings_all", {}).get(target_id, {}).get(dim, {}).get(era, {})
    raw_values = [rec["value"] for rec in era_map.values() if rec["value"] != "abstain"]
    stdev = population_stdev(raw_values)

    quorum = cfg["quorum"]
    confirm = cfg["confirm"]
    contested_threshold = cfg["contested_threshold"]
    cold_factor = cfg["cold_factor"]

    if n < quorum:
        st = "sealed"
    elif n < confirm:
        st = "provisional"
    else:
        # Contested trigger (corrected -- see structurally_contested() /
        # dispersion-regimes/): STRUCTURAL contestedness (this target is a rival
        # positive claim in a live antithesis) is the reliable primary signal;
        # raw rating stdev is a DEMOTED, conservative secondary net (it is only a
        # valid contested signal when dispersion is belief-camp-driven, and fails
        # toward "flag for review" -- a safe error -- when it fires spuriously).
        struct = target_id in structurally_contested(state)
        contested = struct or (stdev is not None and stdev > contested_threshold)
        if contested:
            # Contested wins over settled (PHASE2-SPEC.md §1) even if the
            # node also happens to be cold.
            st = "contested"
        elif cfg.get("static"):
            # Static presentation graph: content-heat is a build-order artifact,
            # not a live "is this being edited" signal, so don't gate `settled`
            # on coldness -- a converged, non-contested, fully-rated target is
            # settled outright.
            st = "settled"
        else:
            rep_heat = representative_content_heat(target_id, state, content_heat)
            is_cold = site_median_content is not None and rep_heat < cold_factor * site_median_content
            st = "settled" if is_cold else "provisional"

    # --- blocs (PHASE2-SPEC.md §5) ---
    bloc_groups: dict[str, list[float]] = {}
    for rec in era_map.values():
        b = rec.get("bloc")
        if b is None or rec["value"] == "abstain":
            continue
        bloc_groups.setdefault(b, []).append(rec["value"])
    blocs_out = {b: {"mean": sum(vs) / len(vs), "n": len(vs)} for b, vs in bloc_groups.items()}
    min_ratings = cfg["bloc_min_ratings"]
    qualifying = {b: vs for b, vs in bloc_groups.items() if len(vs) >= min_ratings}
    bloc_divergence = bloc_f_statistic(qualifying) if len(qualifying) >= 2 else None

    # --- history (PHASE2-SPEC.md §4): every CLOSED era's final aggregate ---
    # Deliberately a plain (unweighted) mean of that era's raw ratings, not
    # the True_R-weighted aggregate assess.compute() produces for the LIVE
    # era: reputations are a current, site-wide, cross-era quantity (an
    # agent has one True_R, not one per era), so "re-running the weighted
    # fixed-point loop as of a past, closed era" would need its own
    # era-scoped reputation model the spec doesn't ask for. History is a
    # visible record of what that era settled at, not a live, reputation-
    # weighted score -- a plain mean is the honest, simple thing to show.
    all_eras_map = state.get("ratings_all", {}).get(target_id, {}).get(dim, {})
    history = []
    for e in sorted(k for k in all_eras_map if k < era):
        vals = [rec["value"] for rec in all_eras_map[e].values() if rec["value"] != "abstain"]
        if vals:
            history.append({"era": e, "mean": sum(vals) / len(vals), "n": len(vals),
                             "stdev": population_stdev(vals)})
        else:
            history.append({"era": e, "mean": None, "n": 0, "stdev": None})

    block = {
        "mean": mean, "n": n, "stdev": stdev, "state": st, "era": era,
        "history": history, "blocs": blocs_out, "bloc_divergence": bloc_divergence,
    }
    # ASSESSMENT-SPEC §5 (UI ask): the raw rating DISTRIBUTION, as 6 integer bins
    # over the 0-5 scale -- histogram[i] = count of current-era ratings that round
    # to i (half-up, clamped). Unweighted (a distribution, not a reputation-weighted
    # score) and present ONLY when the target has ratings, so unrated blocks and
    # rating-free graphs are unchanged; the viewer renders it wherever it appears
    # and falls back to the stdev band where it doesn't.
    if raw_values:
        histogram = [0, 0, 0, 0, 0, 0]
        for v in raw_values:
            histogram[min(5, max(0, int(v + 0.5)))] += 1
        block["histogram"] = histogram
    return block


# --- nudge (PHASE2-SPEC.md §7) ----------------------------------------------

def check_nudge(state: dict, target: str, dim: str, value, cfg: dict) -> str | None:
    """PHASE2-SPEC.md §7 divergence nudge: called with the state BEFORE the
    new rating is applied. Returns a human-readable note, or None. Only
    fires for a numeric rating (an abstain has no "distance") against an
    UNSEALED target (n >= quorum already, per the spec's "visible current
    mean" -- a sealed target has no visible mean to diverge from) using a
    simple unweighted mean of the target's current-era numeric ratings so
    far (documented choice: the nudge is a fast, informational check at
    write time, not the True_R-weighted published aggregate, which would
    require running the full fixed-point loop on every `rate` call)."""
    if value == "abstain":
        return None
    era = state["eras"].get(target, 1)
    era_map = state.get("ratings_all", {}).get(target, {}).get(dim, {}).get(era, {})
    values = [rec["value"] for rec in era_map.values() if rec["value"] != "abstain"]
    n = len(values)
    if n < cfg["quorum"]:
        return None
    mean = sum(values) / n
    distance = abs(float(value) - mean)
    if distance >= cfg["nudge_distance"]:
        return (f"this rating ({value}) is {distance:.2f} from the current mean "
                f"({mean:.2f}, n={n}) -- consider adding a comment explaining the "
                "divergence, or adding what's missing to the graph.")
    return None


# --- heat / site medians -----------------------------------------------------

def compute_heat_and_medians(state: dict, cfg: dict) -> dict:
    """Returns {"heat": {"content": {node: x}, "rating": {node: y}},
    "site_median_content_heat": float|None, "site_median_rating_heat":
    float|None} -- heat values rounded to 6 decimals here (the one place
    output-facing rounding happens, PHASE2-SPEC.md §3: "round to 6 decimals
    for byte-stability"); medians are computed from the UNROUNDED values
    (rounding first would make the "any nonzero" filter and the median
    itself depend on the rounding step's own floating point, which is a
    needless extra source of instability for a threshold comparison)."""
    raw = heat_mod.compute_heat(state, half_life=float(cfg["heat_half_life"]), diffuse=float(cfg["heat_diffuse"]))
    content_vals = [v for v in raw["content"].values() if v > 0]
    rating_vals = [v for v in raw["rating"].values() if v > 0]
    site_median_content = median(content_vals)
    site_median_rating = median(rating_vals)
    content_rounded = {nid: round(v, 6) for nid, v in raw["content"].items()}
    rating_rounded = {nid: round(v, 6) for nid, v in raw["rating"].items()}
    return {
        "heat": {"content": content_rounded, "rating": rating_rounded},
        "site_median_content_heat": site_median_content,
        "site_median_rating_heat": site_median_rating,
        # Unrounded content heat is what state-machine "cold" comparisons use
        # (see block_for's caller in fold.py) -- kept alongside the rounded,
        # display-facing copies above.
        "_content_raw": raw["content"],
    }
