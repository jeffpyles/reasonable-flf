"""`graph.py chain` -- chain-strength analysis over simple Ground-paths
(PHASE2-SPEC.md §7, ASSESSMENT-SPEC.md v1.2's conditional edge semantics).

With node Agreement ~ "how likely true" and edge Agreement ~ "how strongly
this, if so, supports that" (the conditional reading, ASSESSMENT-SPEC.md
v1.2), the product of `(node_A/5) x (edge_A/5)` over a support-path from an
ancestor to a descendant is literally the chain rule: P(ancestor) x
P(step|ancestor) x P(n1) x P(step|n1) x ... x P(descendant), under the usual
independence idealizations. This module computes that product (plus the
weakest link and a per-step geometric mean) over every simple path, capped
and sorted deterministically.

This is an ANALYSIS verb: it reads graph.json's real, CURRENT-era means
regardless of a target's sealed/provisional/settled/contested `state` --
"--include-sealed semantics apply implicitly" (PHASE2-SPEC.md §7) -- so it
never goes through queries.py's sealed-masking helpers.
"""
from __future__ import annotations

NEUTRAL_MEAN = 2.5  # "unrated elements contribute the neutral 2.5/5"
SCALE_MAX = 5.0


def _factor(mean) -> tuple[float, bool]:
    """(factor in [0,1], was_unrated) for one node/edge/group A mean."""
    if mean is None:
        return NEUTRAL_MEAN / SCALE_MAX, True
    return float(mean) / SCALE_MAX, False


def _forward_adjacency(edges: list[dict]) -> dict[str, list[dict]]:
    adj: dict[str, list[dict]] = {}
    for e in edges:
        adj.setdefault(e["from"], []).append(e)
    for lst in adj.values():
        # Deterministic exploration order -- sorted by (target node id, edge
        # id) -- not required for correctness (results are re-sorted at the
        # end regardless) but keeps DFS well-behaved/early-exitable.
        lst.sort(key=lambda e: (e["to"], e["id"]))
    return adj


def enumerate_simple_paths(ancestor: str, descendant: str, edges: list[dict],
                           max_paths: int = 16, safety_cap: int = 20000) -> list[tuple[list[str], list[str]]]:
    """Every simple (no repeated node) path ancestor -> descendant following
    Ground edges in their natural `from -> to` (support-flows-forward)
    direction, deterministically sorted by the tuple of node ids on the
    path, capped at `max_paths`. `safety_cap` bounds total DFS exploration
    steps as a defensive guard against pathological graphs -- it does not
    affect which paths are reported among the top `max_paths` for any
    graph small enough that the cap isn't hit (PHASE2-SPEC.md doesn't spec
    a performance bound, so this is implementation freedom)."""
    if ancestor == descendant:
        return []
    adj = _forward_adjacency(edges)
    results: list[tuple[list[str], list[str]]] = []
    visited = {ancestor}
    path_nodes = [ancestor]
    path_edges: list[str] = []
    explored = 0

    def dfs(cur: str):
        nonlocal explored
        if cur == descendant:
            results.append((list(path_nodes), list(path_edges)))
            return
        for e in adj.get(cur, []):
            if explored > safety_cap:
                return
            nxt = e["to"]
            if nxt in visited:
                continue
            explored += 1
            visited.add(nxt)
            path_nodes.append(nxt)
            path_edges.append(e["id"])
            dfs(nxt)
            path_nodes.pop()
            path_edges.pop()
            visited.discard(nxt)

    dfs(ancestor)
    results.sort(key=lambda pe: pe[0])
    return results[:max_paths]


def _path_factors(path_nodes: list[str], path_edges: list[str],
                   nodes_index: dict, edges_index: dict, groups_index: dict) -> list[dict]:
    """One factor per node (endpoints + interior -- PHASE2-SPEC.md §7:
    "include both endpoint nodes' A and every edge and intermediate node on
    the path") and one per edge, IN PATH ORDER (node, edge, node, edge, ...,
    node) -- a grouped edge contributes via its GROUP's A instead of its own
    (§7's conjunction-group closure)."""
    factors = []
    for nid in path_nodes:
        mean = nodes_index[nid]["agreement"]["mean"]
        f, unrated = _factor(mean)
        factors.append({"id": nid, "kind": "node", "factor": f, "unrated": unrated})

    for eid in path_edges:
        edge = edges_index[eid]
        gid = edge.get("group")
        if gid:
            g = groups_index[gid]
            mean = g["agreement"]["mean"]
            f, unrated = _factor(mean)
            factors.append({
                "id": gid, "kind": "group", "factor": f, "unrated": unrated,
                "note": f"edge {eid} is grouped; contributes via group {gid}'s Agreement, not its own",
            })
        else:
            mean = edge["agreement"]["mean"]
            f, unrated = _factor(mean)
            factors.append({"id": eid, "kind": "edge", "factor": f, "unrated": unrated})
    return factors


def _one_path_result(path_nodes: list[str], path_edges: list[str],
                      nodes_index: dict, edges_index: dict, groups_index: dict) -> dict:
    factors = _path_factors(path_nodes, path_edges, nodes_index, edges_index, groups_index)
    product = 1.0
    for fc in factors:
        product *= fc["factor"]
    weakest = min(factors, key=lambda fc: fc["factor"])
    geometric_mean = product ** (1.0 / len(factors)) if factors else 0.0
    partial = any(fc["unrated"] for fc in factors)
    return {
        "nodes": path_nodes,
        "edges": path_edges,
        "product": product,
        "weakest_link": {"id": weakest["id"], "kind": weakest["kind"], "factor": weakest["factor"]},
        "geometric_mean": geometric_mean,
        "partial": partial,
        "factors": factors,
    }


def _reverse_adjacency(edges: list[dict]) -> dict[str, list[str]]:
    """`to -> [from, ...]` -- who directly grounds each node."""
    radj: dict[str, list[str]] = {}
    for e in edges:
        radj.setdefault(e["to"], []).append(e["from"])
    return radj


def _reach(start: str, adjacency: dict[str, list[str]]) -> set[str]:
    """Every node reachable from `start` following `adjacency` (excludes
    `start` itself unless a cycle leads back to it -- the graph is a DAG in
    practice, so it won't)."""
    seen: set[str] = set()
    stack = list(adjacency.get(start, []))
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(adjacency.get(cur, []))
    return seen


def lowest_common_ancestors(a: str, b: str, edges: list[dict]) -> list[str]:
    """The `last common ancestor(s)` of two nodes over the Ground DAG: nodes
    from which support flows forward to BOTH `a` and `b`, closest to them --
    i.e. common ancestors that do not themselves ground another common
    ancestor. A node counts as its own ancestor here, so if `a` grounds `b`
    (or vice versa) the LCA is `a` itself (one leg is then trivial). Returns
    a deterministically sorted list; usually one node, but a diamond can
    yield several."""
    radj = _reverse_adjacency(edges)
    anc_a = _reach(a, radj) | {a}
    anc_b = _reach(b, radj) | {b}
    common = anc_a & anc_b
    if not common:
        return []
    # A forward-adjacency restricted to `common` lets us ask, for each
    # candidate, whether it grounds any OTHER common node; if it does, a
    # lower common ancestor exists and this one isn't the last.
    fadj: dict[str, list[str]] = {}
    for e in edges:
        if e["from"] in common:
            fadj.setdefault(e["from"], []).append(e["to"])
    lcas = [z for z in common if not (_reach(z, fadj) & (common - {z}))]
    return sorted(lcas)


def _leg(graph: dict, lca: str, target: str, nodes_index: dict,
         edges_index: dict, groups_index: dict, max_paths: int) -> dict:
    """Strongest support chain from `lca` down to `target`, plus every path.
    When `lca == target` the leg is trivial: the target's own Agreement is
    its whole strength (no edges to traverse)."""
    if lca == target:
        f, unrated = _factor(nodes_index[target]["agreement"]["mean"])
        trivial = {
            "nodes": [target], "edges": [], "product": f,
            "weakest_link": {"id": target, "kind": "node", "factor": f},
            "geometric_mean": f, "partial": unrated,
            "factors": [{"id": target, "kind": "node", "factor": f, "unrated": unrated}],
        }
        return {"target": target, "trivial": True, "paths": [trivial], "strongest": trivial}
    raw = enumerate_simple_paths(lca, target, graph["ground_edges"], max_paths=max_paths)
    paths = [_one_path_result(pn, pe, nodes_index, edges_index, groups_index) for pn, pe in raw]
    strongest = max(paths, key=lambda p: p["product"]) if paths else None
    return {"target": target, "trivial": False, "paths": paths, "strongest": strongest}


def compare(graph: dict, node_a: str, node_b: str, max_paths: int = 16) -> dict:
    """Compare two nodes back to their last common ancestor: find the LCA(s)
    over the Ground DAG, then score the support chain from each LCA down to
    `node_a` and to `node_b` and say which branch is better grounded. This is
    a display/UI helper -- it consumes assessment outputs (the CURRENT-era
    means chain.py already reads) to make "which of these competing points is
    stronger, and where they diverge" legible. Returns `{"ok": True,
    "comparisons": [...]}` (one per LCA, each with `a_leg`/`b_leg`/`verdict`/
    `margin`) or `{"ok": False, "errors": [...]}`."""
    nodes_index = {n["id"]: n for n in graph["nodes"]}
    edges_index = {e["id"]: e for e in graph["ground_edges"]}
    groups_index = {g["id"]: g for g in graph["conjunction_groups"]}

    errors = []
    if node_a not in nodes_index:
        errors.append(f"unknown node: {node_a}")
    if node_b not in nodes_index:
        errors.append(f"unknown node: {node_b}")
    if node_a == node_b and not errors:
        errors.append("--a and --b must be different nodes")
    if errors:
        return {"ok": False, "errors": errors}

    lcas = lowest_common_ancestors(node_a, node_b, graph["ground_edges"])
    comparisons = []
    for lca in lcas:
        a_leg = _leg(graph, lca, node_a, nodes_index, edges_index, groups_index, max_paths)
        b_leg = _leg(graph, lca, node_b, nodes_index, edges_index, groups_index, max_paths)
        pa = a_leg["strongest"]["product"] if a_leg["strongest"] else None
        pb = b_leg["strongest"]["product"] if b_leg["strongest"] else None
        if pa is None or pb is None:
            verdict, margin = "indeterminate", None
        elif abs(pa - pb) < 1e-9:
            verdict, margin = "tie", 0.0
        else:
            verdict = "a" if pa > pb else "b"
            margin = abs(pa - pb)
        comparisons.append({
            "lca": lca, "a_leg": a_leg, "b_leg": b_leg,
            "verdict": verdict, "margin": margin,
        })
    return {"ok": True, "a": node_a, "b": node_b,
            "common_ancestors": lcas, "comparisons": comparisons}


def compute(graph: dict, ancestor: str, descendant: str, max_paths: int = 16) -> dict:
    """Returns `{"ok": True, "paths": [...]}` or `{"ok": False, "errors":
    [...]}`. Reads graph's CURRENT means directly (bypassing sealed-masking
    -- see module docstring)."""
    nodes_index = {n["id"]: n for n in graph["nodes"]}
    edges_index = {e["id"]: e for e in graph["ground_edges"]}
    groups_index = {g["id"]: g for g in graph["conjunction_groups"]}

    errors = []
    if ancestor not in nodes_index:
        errors.append(f"unknown node: {ancestor}")
    if descendant not in nodes_index:
        errors.append(f"unknown node: {descendant}")
    if ancestor == descendant and not errors:
        errors.append("--from and --to must be different nodes")
    if errors:
        return {"ok": False, "errors": errors}

    raw_paths = enumerate_simple_paths(ancestor, descendant, graph["ground_edges"], max_paths=max_paths)
    paths = [
        _one_path_result(pn, pe, nodes_index, edges_index, groups_index)
        for pn, pe in raw_paths
    ]
    return {"ok": True, "from": ancestor, "to": descendant, "paths": paths}
