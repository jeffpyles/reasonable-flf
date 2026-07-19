#!/usr/bin/env python3
"""Dispersion regimes — when is rating dispersion a valid contested signal?

Reproduces the belief-camp-driven half of the three-regime finding from committed
data in THIS branch (the lens-driven covid numbers are from the fermi
`v0/archive/dispersion-handoff/` package on the beautiful-fermi branch, quoted in README).

For each panel: the between-group (camp) variance share of per-node dispersion, and
the correlation of per-node stdev with consensus error vs an oracle — before and
after removing each rater's additive offset. The claim: raw stdev tracks error only
when dispersion is BELIEF-CAMP-driven (high between-group share); on a good-faith
lens panel it is offset/noise. Run: python3 dispersion-regimes/regimes.py
"""
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "coldstart-lab"))
from common import load_roster, node_a_matrix, p5_oracle  # noqa: E402


def pearson(a, b):
    n = len(a)
    if n < 2:
        return float("nan")
    ma, mb = sum(a) / n, sum(b) / n
    sa = sum((x - ma) ** 2 for x in a) ** .5
    sb = sum((y - mb) ** 2 for y in b) ** .5
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / (sa * sb) if sa and sb else 0.0


def disp(nv):
    xs = list(nv.values())
    return st.pstdev(xs) if len(xs) > 1 else 0.0


def analyze(name, items, truth, group_of):
    nodes = [n for n in items if n in truth and len(items[n]) > 2]
    agents = sorted({a for n in nodes for a in items[n]})
    amean = {a: st.mean([items[n][a] for n in nodes if a in items[n]]) for a in agents}
    raw = {n: disp(items[n]) for n in nodes}
    res = {n: disp({a: items[n][a] - amean[a] for a in items[n]}) for n in nodes}
    cons = {n: st.mean(list(items[n].values())) for n in nodes}
    err = {n: abs(cons[n] - truth[n]) for n in nodes}
    bt, wn = [], []
    for n in nodes:
        by = {}
        for a in items[n]:
            by.setdefault(group_of(a), []).append(items[n][a])
        by = {g: v for g, v in by.items() if v}
        if len(by) < 2:
            continue
        gm = st.mean([items[n][a] for a in items[n]])
        bt.append(st.mean([(st.mean(v) - gm) ** 2 for v in by.values()]))
        wn.append(st.mean([st.pvariance(v) if len(v) > 1 else 0 for v in by.values()]))
    B, W = st.mean(bt), st.mean(wn)
    N = list(nodes)
    print(f"=== {name}  ({len(nodes)} nodes, {len(agents)} raters) ===")
    print(f"  between-group / total dispersion        : {B/(B+W):.0%}")
    print(f"  corr(RAW stdev, consensus error)        : {pearson([raw[n] for n in N], [err[n] for n in N]):+.2f}")
    print(f"  corr(rater-offset-removed stdev, error) : {pearson([res[n] for n in N], [err[n] for n in N]):+.2f}\n")


def main():
    truth, _ = p5_oracle()
    r8 = load_roster("eggs-p8")
    analyze("eggs-p8 (BIASED belief-camps)", node_a_matrix("eggs-p8", set(r8)),
            truth, lambda a: r8[a]["disposition"])

    anc = json.loads((ROOT / "covid/anchors.json").read_text())["nodes"]
    ctruth = {n: d["oracle_mean"] for n, d in anc.items()}
    roster = {a["id"]: a for a in json.loads((ROOT / "covid/harness/roster.json").read_text())["agents"]}
    latest = {}
    for line in (ROOT / "covid/events.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e["verb"] == "rate" and e["payload"].get("dim") == "A":
            latest[(e["agent"], e["payload"]["target"])] = e["payload"]["value"]
    citems = {}
    for (a, t), v in latest.items():
        if roster.get(a, {}).get("role") == "honest":
            citems.setdefault(t, {})[a] = v
    analyze("our covid (GOOD-FAITH belief-camps: zoo/lab)", citems, ctruth, lambda a: roster[a]["camp"])

    print("fermi covid (GOOD-FAITH lens panel: bayes/domain/ev/skeptic) — from v0/archive/dispersion-handoff/:")
    print("  between-lens / total dispersion  : 16%")
    print("  raw dispersion AUC(contested>settled): 0.42 (anti-signal); reliability ~0.37")
    print("\nReading: dispersion tracks contestedness when it is BELIEF-CAMP-driven (high between-group")
    print("share, corr>0), and is noise when LENS/STYLE-driven (low share). The between-group fraction is")
    print("the diagnostic. The corrected contested signal is the camp structure, now live in")
    print("reasonable/assessment.py (detect_camps.between_group_fraction + camp_contested).")


if __name__ == "__main__":
    main()
