#!/usr/bin/env python3
"""graph.py -- the Reasonable v0 CLI (BUILD-SPEC.md §2, the frozen interface).

    python3 graph.py <verb> [args] --data <dir> [--agent <id>] [--json]

`--data <dir>` is REQUIRED on every verb, read or write -- it names the
graph you are working in. There is no default; concurrent multi-agent runs
that forgot it used to silently fall through to a shared ./data graph.

Stdlib-only, Python 3.11+. No pip, no servers, no network. Every write verb
appends one event to `<data>/events.jsonl` and rewrites `<data>/graph.json`
as a pure, deterministic function of the log (see reasonable/fold.py). Every
read verb re-derives its answer from the same log, so it's always accurate
even if graph.json happens to be stale.

Run `python3 graph.py --help` or `python3 graph.py <verb> --help` for full
per-verb usage.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from reasonable import chain as chain_mod
from reasonable import assess, assessment, contested, decompose, fold, ops, queries, store, validate
from reasonable.ops import Result


def _rate_value(s: str):
    """argparse `type=` for `rate --value`: either the literal "abstain" or a
    float (range-checked later, against the configurable scale_max, by
    validate.validate_rate -- not here, since argparse has no data-dir
    context to read config.json from)."""
    if s.strip().lower() == "abstain":
        return "abstain"
    try:
        return float(s)
    except ValueError:
        raise argparse.ArgumentTypeError(f"--value must be a float or 'abstain', got {s!r}") from None


def _print(obj_text, obj_json, as_json: bool) -> None:
    if as_json:
        print(json.dumps(obj_json, sort_keys=True, indent=2, ensure_ascii=False))
    else:
        print(obj_text)


def _emit_result(res: Result, as_json: bool, label: str) -> int:
    if res.ok:
        if as_json:
            out = {"ok": True, "id": res.id, "warnings": res.warnings}
            # PHASE2-SPEC.md §7 divergence nudge: never a rejection, just an
            # extra advisory field/line riding along with the normal
            # success response -- `res.data["nudge"]` is only ever set by
            # `cmd_rate` when the new rating landed far from the target's
            # current visible mean.
            if res.data and res.data.get("nudge"):
                out["nudge"] = res.data["nudge"]
            print(json.dumps(out, sort_keys=True, indent=2))
        else:
            print(res.id if res.id is not None else "ok")
            for w in res.warnings:
                print(f"warning: {w}", file=sys.stderr)
            if res.data and res.data.get("nudge"):
                print(f"nudge: {res.data['nudge']}", file=sys.stderr)
        return 0

    if as_json:
        print(json.dumps({"ok": False, "errors": res.errors}, sort_keys=True, indent=2))
    else:
        for e in res.errors:
            print(f"error: {e}", file=sys.stderr)
    return 1


# --- write verbs ---------------------------------------------------------

def do_create_node(args) -> int:
    res = ops.cmd_create_node(
        args.data, args.agent, args.text, kind=args.kind, source=args.source,
        title=args.title, max_claim_chars=args.max_claim_chars,
    )
    return _emit_result(res, args.json, "node")


def do_draw_ground(args) -> int:
    res = ops.cmd_draw_ground(args.data, args.agent, args.from_, args.to, group=args.group)
    return _emit_result(res, args.json, "edge")


def do_add_antithesis(args) -> int:
    res = ops.cmd_add_antithesis(args.data, args.agent, args.node, set_id=args.set)
    return _emit_result(res, args.json, "set")


def do_agree(args) -> int:
    res = ops.cmd_agree(args.data, args.agent, args.target)
    return _emit_result(res, args.json, "agree")


def do_propose_title(args) -> int:
    res = ops.cmd_propose_title(args.data, args.agent, args.node, args.text,
                                 max_claim_chars=args.max_claim_chars)
    return _emit_result(res, args.json, "title")


def do_propose_phrasing(args) -> int:
    res = ops.cmd_propose_phrasing(args.data, args.agent, args.node, args.text,
                                    max_claim_chars=args.max_claim_chars)
    return _emit_result(res, args.json, "phrasing")


def do_flag_friction(args) -> int:
    refs = [r.strip() for r in args.refs.split(",")] if args.refs else []
    res = ops.cmd_flag_friction(args.data, args.agent, args.text, refs=refs)
    return _emit_result(res, args.json, "friction")


def do_flag_type(args) -> int:
    res = ops.cmd_flag_type(args.data, args.agent, args.node, args.as_kind)
    return _emit_result(res, args.json, "flag")


def do_supersede(args) -> int:
    res = ops.cmd_supersede(args.data, args.agent, args.target, reason=args.reason,
                            restore=args.restore)
    return _emit_result(res, args.json, "target")


def do_comment(args) -> int:
    res = ops.cmd_comment(args.data, args.agent, target=args.target, text=args.text, reply_to=args.reply_to)
    return _emit_result(res, args.json, "comment")


def do_propose_typing(args) -> int:
    res = ops.cmd_propose_typing(args.data, args.agent, args.edge, node=args.node, label=args.label)
    return _emit_result(res, args.json, "typing")


def do_rate(args) -> int:
    res = ops.cmd_rate(args.data, args.agent, args.target, args.dim, args.value,
                        bloc=args.bloc, nudge_distance=args.nudge_distance)
    return _emit_result(res, args.json, "rate")


def do_reopen(args) -> int:
    res = ops.cmd_reopen(args.data, args.agent, args.target, args.reason)
    return _emit_result(res, args.json, "reopen")


def do_poll_vote(args) -> int:
    res = ops.cmd_poll_vote(args.data, args.agent, args.node, args.question, args.value)
    return _emit_result(res, args.json, "poll_vote")


def do_polls(args) -> int:
    """Categorical type-poll state + reputation-weighted resolution (typepoll.py;
    SPEC-evidence-argument-ought-ghosts §2.2). Read-only. Dormant (unvoted) flags
    emit nothing."""
    state = fold.fold(store.read_events(Path(args.data)))
    cfg = store.read_config(Path(args.data))
    out = assess.compute(state, cfg.get("assessment"))
    polls = {k: v for k, v in out["polls"].items() if v["n_votes"] or v["decline"]}
    if args.json:
        print(json.dumps({"ok": True, "polls": polls}, sort_keys=True, indent=2))
        return 0
    if not polls:
        print("no active polls (dormant flags emit nothing until voted)")
        return 0
    for k in sorted(polls):
        v = polls[k]
        share = "n/a" if v["yes_share"] is None else f"{v['yes_share']:.0%}"
        status = f"RESOLVED -> {v['resolved_kind']}" if v["resolved"] else "open"
        reopen = " (reopen required to complete the flip)" if v["reopen_required"] else ""
        print(f"  {v['node']} [{v['question']}]: yes {v['yes']} / no {v['no']} / "
              f"decline {v['decline']} | rep-weighted yes-share {share} | {status}{reopen}")
    return 0


def do_decompose(args) -> int:
    """SPEC-evidence-argument-ought-ghosts §2.3: type polls that met quorum but
    stayed SPLIT -> is/ought-conflation decomposition candidates. Read-only; the
    split itself is an authoring act (guided by the printed hint)."""
    state = fold.fold(store.read_events(Path(args.data)))
    cfg = store.read_config(Path(args.data))
    out = assess.compute(state, cfg.get("assessment"))
    cands = decompose.decompose_candidates(out["polls"])
    if args.json:
        print(json.dumps({"ok": True, "decompose_candidates": cands}, sort_keys=True, indent=2))
        return 0
    if not cands:
        print("no decomposition candidates (no type poll is quorum-met-but-split)")
        return 0
    print(f"decomposition candidates ({len(cands)}) -- persistent type contestation, likely is/ought conflation:")
    for c in cands:
        print(f"  {c['node']} [{c['question']}]: yes-share {c['yes_share']:.0%} over {c['n_votes']} votes")
        print(f"     -> {c['hint']}")
    return 0


# --- read verbs ------------------------------------------------------------

def _fmt_agg(block) -> str:
    """Text-mode rendering of one lifecycle block (PHASE2-SPEC.md §1/§8):
    "pending quorum (n=X)" when sealed and masked, else the usual
    mean±stdev(n=N)[state] form."""
    if not block:
        return "mean=None n=0"
    if block.get("pending"):
        return f"pending quorum (n={block.get('n', 0)})"
    mean = block.get("mean")
    n = block.get("n")
    state = block.get("state")
    if mean is None:
        return f"no ratings yet (n={n}) [{state}]"
    stdev = block.get("stdev")
    stdev_s = f"{stdev:.3f}" if isinstance(stdev, (int, float)) else "-"
    return f"{mean:.3f}±{stdev_s} (n={n}) [{state}]"


def do_get_node(args) -> int:
    graph = queries.load_graph(args.data)
    rating_mode = getattr(args, "rating_mode", False) or queries.rating_mode_only(args.data)
    rec = queries.get_node(graph, args.node, include_sealed=args.include_sealed,
                           rating_mode=rating_mode)
    if rec is None:
        _print(f"error: unknown node {args.node}", {"ok": False, "errors": [f"unknown node {args.node}"]}, args.json)
        return 1
    if args.json:
        print(json.dumps({"ok": True, **rec}, sort_keys=True, indent=2))
        return 0
    n = rec["node"]
    print(f"{n['id']} [{n['kind']}] by {n['author']}")
    print(f"  primary phrasing ({n['primary_phrasing']}): {_phrasing_text(n, n['primary_phrasing'])}")
    if n["primary_title"]:
        print(f"  primary title ({n['primary_title']}): {_title_text(n, n['primary_title'])}")
    if n["source_ref"]:
        print(f"  source: {n['source_ref']}")
    print(f"  comments: {n.get('comment_count', len(n.get('comments', [])))}")
    qual = n.get("quality") or {}
    print(f"  agreement: {_fmt_agg(n.get('agreement'))}")
    print(f"  quality (inherited from top phrasing): "
          f"R {_fmt_agg(qual.get('R'))}  C {_fmt_agg(qual.get('C'))}")
    print(f"  grounds ({len(rec['grounds'])}):")
    for e in rec["grounds"]:
        typing_note = f" typing={e['primary_typing_text']!r}" if e.get("primary_typing_text") else ""
        print(f"    {e['id']}: {e['from']} -> {n['id']}  strength={e['strength']} group={e['group']}"
              f" comments={e['comment_count']}{typing_note}")
    print(f"  dependents ({len(rec['dependents'])}):")
    for e in rec["dependents"]:
        typing_note = f" typing={e['primary_typing_text']!r}" if e.get("primary_typing_text") else ""
        print(f"    {e['id']}: {n['id']} -> {e['to']}  strength={e['strength']} group={e['group']}"
              f" comments={e['comment_count']}{typing_note}")
    print(f"  antithesis sets ({len(rec['antithesis_sets'])}):")
    for s in rec["antithesis_sets"]:
        members = ", ".join(f"{m['node']}(belonging={m['belonging']})" for m in s["members"])
        print(f"    {s['id']}: {members}")
    return 0


def _phrasing_text(node, pid):
    for p in node["phrasings"]:
        if p["id"] == pid:
            return p["text"]
    return ""


def _title_text(node, tid):
    for t in node["titles"]:
        if t["id"] == tid:
            return t["text"]
    return ""


def do_neighborhood(args) -> int:
    graph = queries.load_graph(args.data)
    rating_mode = getattr(args, "rating_mode", False) or queries.rating_mode_only(args.data)
    rec = queries.neighborhood(graph, args.node, depth=args.depth, include_sealed=args.include_sealed,
                               rating_mode=rating_mode)
    if rec is None:
        _print(f"error: unknown node {args.node}", {"ok": False, "errors": [f"unknown node {args.node}"]}, args.json)
        return 1
    if args.json:
        print(json.dumps({"ok": True, **rec}, sort_keys=True, indent=2))
        return 0
    print(f"neighborhood of {rec['focus']} (depth={rec['depth']})")
    for n in rec["nodes"]:
        label = n["primary_title_text"] or n["primary_phrasing_text"] or "(untitled)"
        print(f"  d{n['depth']}  {n['id']} [{n['kind']}]  {label}  comments={n['comment_count']}"
              f"  agreement={_fmt_agg(n.get('agreement'))}")
    for e in rec["edges"]:
        typing_note = f" typing={e['primary_typing_text']!r}" if e.get("primary_typing_text") else ""
        print(f"    {e['id']}: {e['from']} -> {e['to']}  strength={e['strength']} group={e['group']}"
              f" comments={e['comment_count']}{typing_note}")
    return 0


def do_search(args) -> int:
    graph = queries.load_graph(args.data)
    hits = queries.search(graph, args.query, include_sealed=args.include_sealed)
    if args.json:
        print(json.dumps({"ok": True, "hits": hits}, sort_keys=True, indent=2))
        return 0
    if not hits:
        print("(no matches)")
    for h in hits:
        print(f"{h['node']}  {h['field']}:{h['id']}  {h['text']}")
    return 0


def do_list_sets(args) -> int:
    graph = queries.load_graph(args.data)
    sets = queries.list_sets(graph, include_sealed=args.include_sealed)
    if args.json:
        print(json.dumps({"ok": True, "sets": sets}, sort_keys=True, indent=2))
        return 0
    if not sets:
        print("(no antithesis sets)")
    for s in sets:
        members = ", ".join(f"{m['node']}(belonging={m['belonging']})" for m in s["members"])
        print(f"{s['id']}: {members}")
    return 0


def do_list_studies(args) -> int:
    graph = queries.load_graph(args.data)
    sources_root = args.sources if args.sources else (Path(__file__).resolve().parent / "sources")
    studies = queries.list_studies(graph, sources_root)
    if args.json:
        print(json.dumps({"ok": True, "studies": studies}, sort_keys=True, indent=2))
        return 0
    if not studies:
        print("(no evidence sources cited)")
    for s in studies:
        print(f"{s['source']}: {s['citation']}")
        print(f"  cited by: {', '.join(s['nodes'])}")
    return 0


def do_list_comments(args) -> int:
    graph = queries.load_graph(args.data)
    rec = queries.list_comments(graph, args.target)
    if rec is None:
        _print(f"error: unknown target {args.target}",
               {"ok": False, "errors": [f"unknown target {args.target}"]}, args.json)
        return 1
    # ASSESSMENT-SPEC.md §7 (v1.5): enforced Rating mode blinds the comment
    # thread too -- comments routinely state explicit rating values, so reading
    # them during a blind rating pass defeats the point. The thread is withheld,
    # not the fact that it exists (count is still shown).
    if queries.rating_mode_only(args.data):
        n = len(rec["comments"])
        rec = {"target": rec["target"], "target_kind": rec["target_kind"],
               "comments": [], "comment_count": n, "rating_mode": True}
        if args.json:
            print(json.dumps({"ok": True, **rec}, sort_keys=True, indent=2))
            return 0
        print(f"comments on {rec['target']} ({rec['target_kind']}): {n} withheld "
              f"(blind Rating mode)")
        return 0
    if args.json:
        print(json.dumps({"ok": True, **rec}, sort_keys=True, indent=2))
        return 0
    print(f"comments on {rec['target']} ({rec['target_kind']}):")
    if not rec["comments"]:
        print("  (no comments yet)")

    def render(nodes, depth):
        for c in nodes:
            indent = "  " * (depth + 1)
            print(f"{indent}{c['id']} [{c['agent']}, agrees={c['agrees']}] {c['text']}")
            render(c["children"], depth + 1)

    render(queries.thread_comments(rec["comments"]), 0)
    return 0


def _print_account(acc) -> None:
    print(f"{acc['agent']}: true_r={acc['true_r']:.4f} raw_r={acc['raw_r']:.4f} "
          f"confidence={acc['confidence']:.4f} n_assessments={acc['n_assessments']} "
          f"authored={acc['authored']} rated={acc['rated']}")


def do_reputation(args) -> int:
    graph = queries.load_graph(args.data)
    if args.agent:
        acc = queries.reputation(graph, args.agent)
        if acc is None:
            _print(f"error: unknown agent {args.agent}",
                   {"ok": False, "errors": [f"unknown agent {args.agent}"]}, args.json)
            return 1
        if args.json:
            print(json.dumps({"ok": True, "account": acc}, sort_keys=True, indent=2))
        else:
            _print_account(acc)
        return 0
    accounts = queries.reputation(graph)
    if args.json:
        print(json.dumps({"ok": True, "accounts": accounts}, sort_keys=True, indent=2))
        return 0
    if not accounts:
        print("(no accounts yet)")
    for acc in accounts:
        _print_account(acc)
    return 0


def do_assess(args) -> int:
    """Run the validated assessment stack (reasonable/assessment.py) on the live
    graph: belief-camp detection + the corrected contested signal (always), and
    calibrated consensus + the certainty guardrail when an --anchors oracle is
    given. This is the machinery from FINDINGS-SYNTHESIS.md §2/§8, on the graph."""
    state = fold.fold(store.read_events(Path(args.data)))
    anchors = reference = verdict = frontier = None
    if args.anchors:
        raw = json.loads(Path(args.anchors).read_text())
        if isinstance(raw.get("nodes"), dict):  # covid anchors.json shape
            nodes = raw["nodes"]
            cal = raw.get("calibration_anchors") or list(nodes)
            anchors = {n: nodes[n]["oracle_mean"] for n in cal if n in nodes}
            reference = {n: {"mean": nodes[n]["oracle_mean"], "sd": nodes[n].get("oracle_sd", 0.0)}
                         for n in nodes}
            verdict = list(raw.get("reference_verdict") or [])
        else:  # flat {node: truth} map
            anchors = {n: float(v) for n, v in raw.items()}
    if args.verdict:
        verdict = [n.strip() for n in args.verdict.split(",") if n.strip()]
    if args.frontier:
        frontier = [n.strip() for n in args.frontier.split(",") if n.strip()]
    if reference and verdict and frontier is None:
        skip = set(anchors or []) | set(verdict)
        frontier = [n for n in reference if n not in skip]

    rep = assessment.report(state, anchors, reference, verdict, frontier)
    if args.json:
        print(json.dumps({"ok": True, **rep}, sort_keys=True, indent=2))
        return 0
    c = rep["camps"]
    print(f"belief-camps: sizes {c['sizes']}  split_strength {c['split_strength']}  "
          f"between-camp dispersion {c['between_group_fraction']:.0%}")
    print(f"  (between-camp share high => dispersion is a valid contested signal; low => lens/offset noise)")
    cont = rep["contested"]
    print(f"camp-contested nodes ({len(cont)}):")
    for d in cont[:20]:
        print(f"  {d['node']}: camp0 {d['camp0_mean']} vs camp1 {d['camp1_mean']}  (gap {d['gap']})")
    if "calibrated_consensus" in rep:
        cc = rep["calibrated_consensus"]
        print(f"calibrated consensus computed for {len(cc)} nodes (anchor-calibrated, "
              f"inverse-residual-variance weighted)")
    if "certainty_guard" in rep:
        g = rep["certainty_guard"]
        print(f"certainty guardrail: {'FIRED' if g['fired'] else 'quiet'}  ({g['reason']}; "
              f"verdict-score {g['verdict_score']}, frontier {g['frontier_mean']})")
    return 0


def do_contested(args) -> int:
    """Shared contestedness service (reasonable/contested.py): per-node/edge verdict
    contested / settled / ghost_eligible, for the type-poll + ghost trigger. Composes
    the structural (antithesis) + belief-camp signals + own Agreement -- no raw stdev."""
    state = fold.fold(store.read_events(Path(args.data)))
    cfg = store.read_config(Path(args.data))
    anchors = None
    if args.anchors:
        raw = json.loads(Path(args.anchors).read_text())
        if isinstance(raw.get("nodes"), dict):
            nodes = raw["nodes"]
            cal = raw.get("calibration_anchors") or list(nodes)
            anchors = {n: nodes[n]["oracle_mean"] for n in cal if n in nodes}
        else:
            anchors = {n: float(v) for n, v in raw.items()}
    out = assess.compute(state, cfg.get("assessment"), anchors=anchors)
    result = contested.assess_contestedness(state, out["aggregate"],
                                            ghost_floor=args.ghost_floor)
    if args.json:
        print(json.dumps({"ok": True, **result}, sort_keys=True, indent=2))
        return 0
    print(f"belief-split strength {result['split_strength']} | between-camp dispersion "
          f"{result['between_group_fraction']:.0%} | verdicts {contested.summary(result)}")
    for t, v in result["nodes"].items():
        if v["verdict"] != "settled":
            tag = f"camp_gap {v['camp_gap']}" if v["camp_gap"] is not None else \
                  ("antithesis" if v["structural_contested"] else f"own {v['own_agreement']}")
            print(f"  {t:6} {v['verdict']:14} ({tag})")
    return 0


def do_ghosts(args) -> int:
    """SPEC-evidence-argument-ought-ghosts.md §3.1: list the ghost candidates --
    targets refuted on their OWN Agreement (low, settled, and NOT an antithesis
    rival), the refuted-but-retained set. Read-only; composes contested.py's
    verdict so the ghost trigger and the type-poll share one implementation."""
    state = fold.fold(store.read_events(Path(args.data)))
    cfg = store.read_config(Path(args.data))
    out = assess.compute(state, cfg.get("assessment"))
    result = contested.assess_contestedness(state, out["aggregate"], ghost_floor=args.ghost_floor)
    ghosts = {t: v for t, v in result["nodes"].items() if v["verdict"] == "ghost_eligible"}
    # §3.2: manually superseded/demoted targets are ghosts too -- an explicit
    # curation act, distinct from the auto "refuted on own Agreement" candidates.
    demoted = state.get("demotions", {})
    if args.json:
        print(json.dumps({"ok": True, "ghost_floor": args.ghost_floor,
                          "ghost_eligible": ghosts, "demoted": demoted},
                         sort_keys=True, indent=2))
        return 0
    print(f"auto ghost candidates (own Agreement < {args.ghost_floor}, settled, not an antithesis "
          f"rival): {len(ghosts)}")
    for t, v in sorted(ghosts.items()):
        print(f"  {t:6} own {v['own_agreement']}")
    print(f"demoted (superseded, §3.2): {len(demoted)}")
    for t, d in sorted(demoted.items()):
        print(f"  {t:6} by {d.get('agent')}" + (f" -- {d['reason']}" if d.get("reason") else ""))
    return 0


def do_lint(args) -> int:
    """SPEC §4 + §3.3 coherence lint: deterministic structural-hygiene pass
    (hub topology, orphans, malformed sets, question/negation framing, redundant
    paths). Advisory -- proposes review targets, never mutates."""
    graph = queries.load_graph(args.data)
    rep = queries.coherence_lint(graph, hub_threshold=args.hub_threshold)
    if args.json:
        print(json.dumps({"ok": True, **rep}, sort_keys=True, indent=2))
        return 0
    print("coherence lint:")
    for k, v in rep["summary"].items():
        print(f"  {k}: {v}")
    if rep["hub_nodes"]:
        print("hubs (in-degree >= %d -- attach grounds more proximately?):" % args.hub_threshold)
        for h in rep["hub_nodes"]:
            print(f"  {h['node']}: {h['direct_grounds']} direct grounds")
    for cat, label in (("malformed_antithesis_sets", "malformed antithesis sets"),
                       ("orphan_nodes", "orphans"),
                       ("question_shaped_nodes", "question-shaped"),
                       ("negation_framed_nodes", "negation-framed"),
                       ("redundant_paths", "redundant paths")):
        items = rep[cat]
        if items:
            print(f"{label}: {items}")
    return 0


def do_show_config(args) -> int:
    cfg = queries.effective_config(args.data)
    if args.json:
        print(json.dumps({"ok": True, **cfg}, sort_keys=True, indent=2))
        return 0

    def _print_block(d, indent=2):
        for k in sorted(d):
            v = d[k]
            if isinstance(v, dict):
                print(" " * indent + f"{k}:")
                _print_block(v, indent + 2)
            else:
                print(" " * indent + f"{k}: {v}")

    print(f"question: {cfg['question']}")
    print("assessment:")
    _print_block(cfg["assessment"])
    print("phase2:")
    _print_block(cfg["phase2"])
    return 0


def do_stats(args) -> int:
    graph = queries.load_graph(args.data)
    st = queries.stats(graph, args.data)
    if args.json:
        print(json.dumps({"ok": True, **st}, sort_keys=True, indent=2))
        return 0
    print("counts:")
    for k, v in st["counts"].items():
        print(f"  {k}: {v}")
    print("health:")
    for k, v in st["health"].items():
        print(f"  {k}: {v}")
    print("heat_medians:")
    for k, v in st["heat_medians"].items():
        print(f"  {k}: {v}")
    return 0


def do_rebuild(args) -> int:
    overrides = {
        "quorum": args.quorum,
        "confirm": args.confirm,
        "contested_threshold": args.contested_threshold,
        "heat_half_life": args.heat_half_life,
        "heat_diffuse": args.heat_diffuse,
        "cold_factor": args.cold_factor,
        "nudge_distance": args.nudge_distance,
    }
    overrides = {k: v for k, v in overrides.items() if v is not None} or None
    graph = ops.rebuild(args.data, phase2_overrides=overrides)
    if args.json:
        print(json.dumps({"ok": True, "event_count": graph["meta"]["event_count"]}, sort_keys=True, indent=2))
    else:
        print(f"rebuilt graph.json from {graph['meta']['event_count']} events")
    return 0


def do_chain(args) -> int:
    graph = queries.load_graph(args.data)
    result = chain_mod.compute(graph, args.from_, args.to_, max_paths=args.max_paths)
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0 if result["ok"] else 1
    if not result["ok"]:
        for e in result["errors"]:
            print(f"error: {e}", file=sys.stderr)
        return 1
    print(f"chain {result['from']} -> {result['to']}  ({len(result['paths'])} path(s)):")
    for i, p in enumerate(result["paths"], 1):
        partial_note = "  (partial -- includes unrated element(s))" if p["partial"] else ""
        print(f"  path {i}: {' -> '.join(p['nodes'])}{partial_note}")
        print(f"    edges: {', '.join(p['edges'])}")
        print(f"    product={p['product']:.4f}  geometric_mean={p['geometric_mean']:.4f}  "
              f"weakest={p['weakest_link']['id']}({p['weakest_link']['factor']:.3f})")
    return 0


def _print_leg(label: str, leg: dict) -> None:
    s = leg["strongest"]
    if s is None:
        print(f"  {label} ({leg['target']}): no support path from the common ancestor")
        return
    trivial = "  (the ancestor itself -- its own Agreement is the whole strength)" if leg["trivial"] else ""
    partial = "  (partial)" if s["partial"] else ""
    print(f"  {label} ({leg['target']}): {' -> '.join(s['nodes'])}{trivial}{partial}")
    print(f"    product={s['product']:.4f}  geometric_mean={s['geometric_mean']:.4f}  "
          f"weakest={s['weakest_link']['id']}({s['weakest_link']['factor']:.3f})")
    if len(leg["paths"]) > 1:
        print(f"    ({len(leg['paths'])} paths total; strongest shown)")


def do_compare(args) -> int:
    graph = queries.load_graph(args.data)
    result = chain_mod.compare(graph, args.a, args.b, max_paths=args.max_paths)
    if args.json:
        print(json.dumps(result, sort_keys=True, indent=2))
        return 0 if result["ok"] else 1
    if not result["ok"]:
        for e in result["errors"]:
            print(f"error: {e}", file=sys.stderr)
        return 1
    if not result["comparisons"]:
        print(f"compare {result['a']} vs {result['b']}: no common ancestor over the Ground graph "
              "(the two claims share no supporting root).")
        return 0
    print(f"compare {result['a']} vs {result['b']}  "
          f"({len(result['comparisons'])} common ancestor(s)):")
    for c in result["comparisons"]:
        print(f"\nlast common ancestor: {c['lca']}")
        _print_leg("a", c["a_leg"])
        _print_leg("b", c["b_leg"])
        if c["verdict"] == "a":
            print(f"  => a ({result['a']}) is better grounded  (margin {c['margin']:.4f})")
        elif c["verdict"] == "b":
            print(f"  => b ({result['b']}) is better grounded  (margin {c['margin']:.4f})")
        elif c["verdict"] == "tie":
            print("  => equally grounded (tie)")
        else:
            print("  => indeterminate (a branch has no support path)")
    return 0


# --- argparse wiring ---------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="graph.py",
        description="Reasonable v0 CLI: append-only argument-graph events.jsonl + derived graph.json.",
    )
    sub = p.add_subparsers(dest="verb", required=True)

    def common(sp, needs_agent: bool):
        # No default: every verb (read AND write) must name its graph
        # explicitly. Multi-agent runs that forgot --data used to silently
        # fall through to ./data and corrupt/pollute the wrong graph (see
        # BUILD-SPEC.md ## Amendments). We don't use argparse's own
        # `required=True` here because it produces a generic argparse
        # message; instead we default to None and raise a clear, specific
        # error for it in main() below.
        sp.add_argument("--data", type=Path, default=None,
                         help="data directory to operate on (REQUIRED -- name the graph you are working in, "
                              "e.g. --data v0/data)")
        sp.add_argument("--json", action="store_true", help="emit JSON instead of human-readable text")
        if needs_agent:
            sp.add_argument("--agent", required=True, help="acting agent id, e.g. agent-01")
        sp.set_defaults(_subparser=sp)

    # writes
    sp = sub.add_parser("create-node", help="create a new node")
    common(sp, True)
    sp.add_argument("--text", required=True, help="claim text (becomes phrasing p0)")
    sp.add_argument("--kind", choices=["claim", "evidence", "ought", "external_anchor"],
                     default="claim",
                     help="claim (Argument), evidence (fact from a source), ought "
                          "(action/value); 'external_anchor' is a legacy alias for evidence")
    sp.add_argument("--source", default=None, help="required iff --kind evidence")
    sp.add_argument("--title", default=None, help="optional initial title")
    sp.add_argument("--max-claim-chars", type=int, default=validate.DEFAULT_MAX_CLAIM_CHARS,
                     dest="max_claim_chars")
    sp.set_defaults(func=do_create_node)

    sp = sub.add_parser("draw-ground", help="draw a Ground/Dependent edge (from is a Ground of to). "
                                             "Hume's rule: an Ought may not ground a non-Ought.")
    common(sp, True)
    sp.add_argument("--from", required=True, dest="from_")
    sp.add_argument("--to", required=True)
    sp.add_argument("--group", default=None, help="'new' to start a conjunction group, or an existing gid")
    sp.set_defaults(func=do_draw_ground)

    sp = sub.add_parser("add-antithesis", help="add a node to an antithesis set")
    common(sp, True)
    sp.add_argument("--node", required=True)
    sp.add_argument("--set", default="new", dest="set", help="'new' or an existing sid (default new)")
    sp.set_defaults(func=do_add_antithesis)

    sp = sub.add_parser("agree", help="agree with an edge / membership / title / phrasing")
    common(sp, True)
    sp.add_argument("--target", required=True,
                     help="edge id, or set:<sid>:<node> / title:<node>:<tid> / phrasing:<node>:<pid> / "
                          "comment:<cid> / typing:<edge>:<tyid>")
    sp.set_defaults(func=do_agree)

    sp = sub.add_parser("propose-title", help="propose a competing title for a node")
    common(sp, True)
    sp.add_argument("--node", required=True)
    sp.add_argument("--text", required=True)
    sp.add_argument("--max-claim-chars", type=int, default=validate.DEFAULT_MAX_CLAIM_CHARS,
                     dest="max_claim_chars")
    sp.set_defaults(func=do_propose_title)

    sp = sub.add_parser("propose-phrasing", help="propose a competing phrasing for a node")
    common(sp, True)
    sp.add_argument("--node", required=True)
    sp.add_argument("--text", required=True)
    sp.add_argument("--max-claim-chars", type=int, default=validate.DEFAULT_MAX_CLAIM_CHARS,
                     dest="max_claim_chars")
    sp.set_defaults(func=do_propose_phrasing)

    sp = sub.add_parser("flag-friction", help="log something the grammar couldn't cleanly express")
    common(sp, True)
    sp.add_argument("--text", required=True)
    sp.add_argument("--refs", default=None, help="comma-separated node ids, e.g. n001,n004")
    sp.set_defaults(func=do_flag_friction)

    sp = sub.add_parser("flag-type", help="flag a node as a candidate Ought/Evidence "
                                          "(records the flag; the consensus poll that resolves "
                                          "it is the Assessment layer -- SPEC §1.4/§2)")
    common(sp, True)
    sp.add_argument("--node", required=True)
    sp.add_argument("--as", required=True, dest="as_kind", choices=["ought", "evidence"],
                     help="the type being proposed for the node")
    sp.set_defaults(func=do_flag_type)

    sp = sub.add_parser("supersede", help="demote a node/edge toward ghost status without deleting it "
                                          "(--restore to un-demote) -- SPEC §3.2")
    common(sp, True)
    sp.add_argument("--target", required=True, help="node id or edge id to demote/restore")
    sp.add_argument("--reason", default=None, help="public record of why it was superseded")
    sp.add_argument("--restore", action="store_true", help="un-demote a currently-demoted target")
    sp.set_defaults(func=do_supersede)

    sp = sub.add_parser("poll-vote", help="vote Yes/No/decline on an open categorical type poll "
                                          "(opened by flag-type; resolves reputation-weighted -- "
                                          "SPEC-evidence-argument-ought-ghosts §2.2)")
    common(sp, True)
    sp.add_argument("--node", required=True)
    sp.add_argument("--question", required=True,
                     help="the poll question, e.g. 'type:ought' or 'type:evidence'")
    sp.add_argument("--value", required=True, choices=["yes", "no", "decline"])
    sp.set_defaults(func=do_poll_vote)

    sp = sub.add_parser("polls", help="categorical type-poll state + reputation-weighted "
                                      "resolution (typepoll.py; SPEC-evidence §2.2)")
    common(sp, False)
    sp.set_defaults(func=do_polls)

    sp = sub.add_parser("decompose", help="type polls that met quorum but stayed split -> is/ought "
                                          "conflation decomposition candidates (SPEC-evidence §2.3)")
    common(sp, False)
    sp.set_defaults(func=do_decompose)

    sp = sub.add_parser("comment", help="comment on a node or edge, or reply to an existing comment "
                                          "(FORUMS-SPEC.md)")
    common(sp, True)
    sp.add_argument("--target", default=None, help="node id or edge id to comment on "
                                                     "(mutually exclusive with --reply-to)")
    sp.add_argument("--text", required=True)
    sp.add_argument("--reply-to", default=None, dest="reply_to",
                     help="an existing comment id to reply to; inherits its target "
                          "(mutually exclusive with --target)")
    sp.set_defaults(func=do_comment)

    sp = sub.add_parser("propose-typing", help="propose a candidate answer to \"what inference is this "
                                                 "edge making?\" (FORUMS-SPEC.md)")
    common(sp, True)
    sp.add_argument("--edge", required=True)
    sp.add_argument("--node", default=None, help="reference an existing trunk node (preferred when one exists)")
    sp.add_argument("--label", default=None, help="free-text typing, when no trunk node exists yet "
                                                    "(mutually exclusive with --node)")
    sp.set_defaults(func=do_propose_typing)

    sp = sub.add_parser("rate", help="rate a phrasing/comment (R|C), a node/edge/group (A) on a 0-5 "
                                       "scale, or abstain (ASSESSMENT-SPEC.md, PHASE2-SPEC.md §7)")
    common(sp, True)
    sp.add_argument("--target", required=True,
                     help="phrasing:<node>:<pid> / comment:<cid> (dim R or C), or a bare node id, "
                          "edge id, or group:<gid> (dim A only)")
    sp.add_argument("--dim", required=True, choices=["R", "C", "A"],
                     help="R=Reasonableness, C=Clarity (phrasings/comments); "
                          "A=Agreement (nodes, edges & groups)")
    sp.add_argument("--value", required=True, type=_rate_value, help="0.0-5.0, or 'abstain'")
    sp.add_argument("--bloc", default=None,
                     help="PHASE2-SPEC.md §5: an opaque bloc id (e.g. b1), for bloc-divergence bookkeeping")
    sp.add_argument("--nudge-distance", type=float, default=None, dest="nudge_distance",
                     help="PHASE2-SPEC.md §7: override the configured divergence-nudge distance "
                          "for this call only (default: the persisted phase2.nudge_distance config, 1.5)")
    sp.set_defaults(func=do_rate)

    sp = sub.add_parser("reopen", help="reopen a rated target: increments its era, returns it to "
                                         "sealed (PHASE2-SPEC.md §4)")
    common(sp, True)
    sp.add_argument("--target", required=True,
                     help="same target grammar as `rate`: node/edge id, group:<gid>, "
                          "phrasing:<node>:<pid>, comment:<cid>")
    sp.add_argument("--reason", required=True, help="why the era is turning (recorded in the log)")
    sp.set_defaults(func=do_reopen)

    # reads
    sp = sub.add_parser("get-node", help="full node record + edges + antithesis + titles/phrasings")
    common(sp, False)
    sp.add_argument("node")
    sp.add_argument("--include-sealed", action="store_true", dest="include_sealed",
                     help="PHASE2-SPEC.md §1/§8: show real means for sealed targets too "
                          "(default: masked as 'pending quorum')")
    sp.add_argument("--rating-mode", action="store_true", dest="rating_mode",
                     help="ASSESSMENT-SPEC.md §7 blind Rating mode: hide every consensus cue "
                          "(agreement/quality/scores aggregates, comments, rating-heat) so you "
                          "judge independently before seeing how others rated. Text + structure kept.")
    sp.set_defaults(func=do_get_node)

    sp = sub.add_parser("neighborhood", help="node + neighbors out to depth N (titles + G/D structure)")
    common(sp, False)
    sp.add_argument("--node", required=True)
    sp.add_argument("--depth", type=int, default=1)
    sp.add_argument("--include-sealed", action="store_true", dest="include_sealed",
                     help="PHASE2-SPEC.md §1/§8: show real means for sealed targets too")
    sp.add_argument("--rating-mode", action="store_true", dest="rating_mode",
                     help="ASSESSMENT-SPEC.md §7 blind Rating mode: hide agreement/quality "
                          "aggregates + comments (structure/text kept)")
    sp.set_defaults(func=do_neighborhood)

    sp = sub.add_parser("search", help="substring/keyword match over phrasings + titles")
    common(sp, False)
    sp.add_argument("query")
    sp.add_argument("--include-sealed", action="store_true", dest="include_sealed",
                     help="PHASE2-SPEC.md §1/§8: accepted for interface symmetry (search shows no "
                          "aggregate means to mask)")
    sp.set_defaults(func=do_search)

    sp = sub.add_parser("list-sets", help="all antithesis sets with members")
    common(sp, False)
    sp.add_argument("--include-sealed", action="store_true", dest="include_sealed",
                     help="PHASE2-SPEC.md §1/§8: accepted for interface symmetry (antithesis "
                          "membership has no rated aggregate to mask)")
    sp.set_defaults(func=do_list_sets)

    sp = sub.add_parser("list-studies",
                         help="group external_anchor nodes by source_ref, with pack citation lookup "
                              "(find an existing study id / see all claims already attached to it)")
    common(sp, False)
    sp.add_argument("--sources", type=Path, default=None,
                     help="sources pack root (default: <v0>/sources, i.e. sibling of graph.py)")
    sp.set_defaults(func=do_list_studies)

    sp = sub.add_parser("list-comments", help="list a node's or edge's comment thread (FORUMS-SPEC.md)")
    common(sp, False)
    sp.add_argument("--target", required=True, help="node id or edge id")
    sp.set_defaults(func=do_list_comments)

    sp = sub.add_parser("assess", help="validated assessment stack on the live graph: belief-camp "
                        "detection + corrected contested signal (always), calibrated consensus + "
                        "certainty guardrail with --anchors (assessment.py; FINDINGS-SYNTHESIS §2/§8)")
    common(sp, False)
    sp.add_argument("--anchors", help="oracle JSON: covid anchors.json shape, or a flat {node: truth} map")
    sp.add_argument("--verdict", help="comma-separated top-answer node ids (for the certainty guardrail)")
    sp.add_argument("--frontier", help="comma-separated contested crux node ids (default: reference minus anchors/verdict)")
    sp.set_defaults(func=do_assess)

    sp = sub.add_parser("contested", help="shared contestedness verdict per node/edge "
                        "(contested / settled / ghost_eligible) for the type-poll + ghost trigger "
                        "(contested.py; SPEC-evidence-argument-ought-ghosts §2/§3)")
    common(sp, False)
    sp.add_argument("--anchors", help="oracle JSON (covid anchors.json shape or flat {node:truth}) "
                    "-> use the calibrated aggregate")
    sp.add_argument("--ghost-floor", type=float, default=1.5, dest="ghost_floor",
                    help="own-Agreement below which a settled, non-antithesis target is ghost_eligible")
    sp.set_defaults(func=do_contested)

    sp = sub.add_parser("ghosts", help="list ghost candidates: targets refuted on their own Agreement "
                                       "(refuted-but-retained; SPEC §3.1)")
    common(sp, False)
    sp.add_argument("--ghost-floor", type=float, default=1.5, dest="ghost_floor",
                    help="own-Agreement below which a settled, non-antithesis target is a ghost candidate")
    sp.set_defaults(func=do_ghosts)

    sp = sub.add_parser("lint", help="deterministic structural-coherence lint: hubs, orphans, malformed "
                                     "sets, question/negation framing, redundant paths (SPEC §4/§3.3)")
    common(sp, False)
    sp.add_argument("--hub-threshold", type=int, default=8, dest="hub_threshold",
                    help="direct-ground in-degree at/above which a node is flagged as a star/hub")
    sp.set_defaults(func=do_lint)

    sp = sub.add_parser("reputation", help="agent reputation accounts (ASSESSMENT-SPEC.md)")
    common(sp, False)
    sp.add_argument("--agent", default=None, help="show one agent's account instead of the whole table")
    sp.set_defaults(func=do_reputation)

    sp = sub.add_parser("show-config", help="the effective config.json, defaults filled in "
                                              "(ASSESSMENT-SPEC.md)")
    common(sp, False)
    sp.set_defaults(func=do_show_config)

    sp = sub.add_parser("stats", help="counts + health signals")
    common(sp, False)
    sp.set_defaults(func=do_stats)

    sp = sub.add_parser("rebuild", help="regenerate graph.json from events.jsonl (idempotent). "
                                          "PHASE2-SPEC.md §1: any --quorum/--confirm/etc. flag given here "
                                          "persists into <data>/config.json's phase2 block for every "
                                          "subsequent write/rebuild too, not just this one.")
    common(sp, False)
    sp.add_argument("--quorum", type=int, default=None, help="min ratings before a target is no longer "
                                                                "sealed (default 5)")
    sp.add_argument("--confirm", type=int, default=None, help="min ratings for provisional -> "
                                                                 "settled/contested eligibility (default 15)")
    sp.add_argument("--contested-threshold", type=float, default=None, dest="contested_threshold",
                     help="stdev above which a confirmed target is contested, not settled (default 1.0)")
    sp.add_argument("--heat-half-life", type=float, default=None, dest="heat_half_life",
                     help="heat decay half-life in SITE-WIDE EVENTS, not wall-clock (default 300, "
                          "PHASE2-SPEC.md Amendment p2.1)")
    sp.add_argument("--heat-diffuse", type=float, default=None, dest="heat_diffuse",
                     help="fraction of each injection diffused to direct neighbors (default 0.15)")
    sp.add_argument("--cold-factor", type=float, default=None, dest="cold_factor",
                     help="a node is cold when content heat < this * the site median (default 0.5)")
    sp.add_argument("--nudge-distance", type=float, default=None, dest="nudge_distance",
                     help="persisted default divergence-nudge distance (default 1.5; `rate` can also "
                          "override this per-call with its own --nudge-distance)")
    sp.set_defaults(func=do_rebuild)

    sp = sub.add_parser("chain", help="chain-strength analysis over simple Ground-paths from an "
                                        "ancestor to a descendant (PHASE2-SPEC.md §7). Reads CURRENT-era, "
                                        "sealed-or-not ACTUAL means -- --include-sealed semantics apply "
                                        "implicitly, since this is an analysis verb, not a display one.")
    common(sp, False)
    sp.add_argument("--from", required=True, dest="from_", metavar="FROM", help="ancestor node id")
    sp.add_argument("--to", required=True, dest="to_", metavar="TO", help="descendant node id")
    sp.add_argument("--max-paths", type=int, default=16, dest="max_paths",
                     help="cap on reported simple paths (default 16, PHASE2-SPEC.md §7)")
    sp.set_defaults(func=do_chain)

    sp = sub.add_parser("compare", help="compare two competing nodes back to their last common "
                                          "ancestor over the Ground graph: score the support chain from "
                                          "the shared root down to each and say which branch is better "
                                          "grounded. A display/UI helper over chain-strength; reads "
                                          "CURRENT-era ACTUAL means like `chain`.")
    common(sp, False)
    sp.add_argument("--a", required=True, help="first node id")
    sp.add_argument("--b", required=True, help="second node id")
    sp.add_argument("--max-paths", type=int, default=16, dest="max_paths",
                     help="cap on reported simple paths per leg (default 16)")
    sp.set_defaults(func=do_compare)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.data is None:
        # args.func is only unset if `--help` was handled inline (which
        # exits before reaching here), so every verb has a _subparser.
        sp = getattr(args, "_subparser", parser)
        sp.error("--data is required: name the graph you are working in")
    try:
        return args.func(args)
    except ops.store.LockTimeoutError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
