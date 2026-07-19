"""Shared loaders + stats for the cold-start lab (see FINDINGS.md).

Everything reads the committed event logs; stdlib only; deterministic.
Run scripts from the repo root (paths are root-relative, like the other
harnesses).
"""
import json
import math
import statistics as st
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from reasonable import store, fold  # noqa: E402


# ---------- stats ----------
def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx and dy else 0.0


def rank(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i])
    r = [0.0] * len(vals)
    i = 0
    while i < len(vals):
        j = i
        while j + 1 < len(vals) and vals[order[j + 1]] == vals[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2.0
        i = j + 1
    return r


def spearman(xs, ys):
    return pearson(rank(xs), rank(ys))


def pctile(v, pop):
    return sum(1 for x in pop if x < v) / len(pop)


def mean(v):
    return st.mean(v) if v else float("nan")


# ---------- loaders ----------
def load_roster(run):
    r = json.loads((ROOT / run / "harness/roster.json").read_text())
    return {a["id"]: a for a in r["agents"]}


def node_a_matrix(run, restrict_ids=None):
    """items[node_id] = {agent: value} for dim A on nodes, numeric only."""
    stt = fold.fold(store.read_events(str(ROOT / run)))
    items = {}
    for t, dm in stt["ratings"].items():
        if t.startswith("n") and "A" in dm:
            cell = {a: v for a, v in dm["A"].items()
                    if v != "abstain" and (restrict_ids is None or a in restrict_ids)}
            if cell:
                items[t] = cell
    return items


def full_matrix(run, restrict_ids=None):
    """items[(target, dim)] = {agent: value}, all target kinds."""
    stt = fold.fold(store.read_events(str(ROOT / run)))
    items = {}
    for t, dm in stt["ratings"].items():
        for d, am in dm.items():
            cell = {a: v for a, v in am.items()
                    if v != "abstain" and (restrict_ids is None or a in restrict_ids)}
            if cell:
                items[(t, d)] = cell
    return items


def p5_oracle(min_experts=3):
    """truth[node_id], ostd[node_id] from the eggs-p5 8-expert panel."""
    stt = fold.fold(store.read_events(str(ROOT / "eggs-p5")))
    roster = load_roster("eggs-p5")
    truth, ostd = {}, {}
    for t, dm in stt["ratings"].items():
        if "A" in dm:
            ev = [v for a, v in dm["A"].items()
                  if roster.get(a, {}).get("tier") == "expert" and v != "abstain"]
            if len(ev) >= min_experts:
                truth[t] = st.mean(ev)
                ostd[t] = st.pstdev(ev)
    return truth, ostd


def oracle_competence(items, truth, min_items=5):
    """competence[agent] = corr(their ratings, oracle truth) over co-covered items."""
    by = defaultdict(list)
    for t, cell in items.items():
        if t in truth:
            for a, v in cell.items():
                by[a].append((v, truth[t]))
    return {a: pearson([p[0] for p in pts], [p[1] for p in pts])
            for a, pts in by.items() if len(pts) >= min_items}


# ---------- candidate rating-quality scores ----------
def align_score(items, min_raters=2):
    """1 - mean |v - item mean| / 5. The failed live rule, as baseline."""
    diffs = defaultdict(list)
    for t, cell in items.items():
        if len(cell) < min_raters:
            continue
        m = st.mean(cell.values())
        for a, v in cell.items():
            diffs[a].append(abs(v - m) / 5.0)
    return {a: 1 - sum(d) / len(d) for a, d in diffs.items()}


def disc_score(items, min_raters=4, min_pairs=5):
    """Pearson corr with the leave-one-out item mean."""
    by = defaultdict(list)
    for t, cell in items.items():
        if len(cell) < min_raters:
            continue
        tot, n = sum(cell.values()), len(cell)
        for a, v in cell.items():
            by[a].append((v, (tot - v) / (n - 1)))
    return {a: pearson([p[0] for p in pr], [p[1] for p in pr])
            for a, pr in by.items() if len(pr) >= min_pairs}


def anchor_score(items, anchors, anchor_truth, min_hits=1):
    """1 - mean |v - anchor truth| / 5 over the anchor items the agent rated."""
    out = {}
    agents = {a for c in items.values() for a in c}
    for a in agents:
        pts = [abs(items[t][a] - anchor_truth[t]) / 5.0
               for t in anchors if t in items and a in items[t]]
        if len(pts) >= min_hits:
            out[a] = 1 - sum(pts) / len(pts)
    return out


def fit_affine(xs, ys, lam=2.0):
    """Ridge-toward-identity affine fit; returns (slope, intercept, resid_sd)."""
    n = len(xs)
    if n < 3:
        return 1.0, 0.0, None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = (sxy + lam) / (sxx + lam)
    inter = my - slope * mx
    resid = [y - (slope * x + inter) for x, y in zip(xs, ys)]
    sd = math.sqrt(sum(r * r for r in resid) / n)
    return slope, inter, sd


def clip5(v):
    return max(0.0, min(5.0, v))
