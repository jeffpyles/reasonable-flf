#!/usr/bin/env python3
"""Score the black-holes panel against the cross-model oracle (reference only).

Reads blackholes-graph/graph.json (the folded 20-rater panel aggregate) and
blackholes-graph/anchors.json (the oracle), and reports MAE + correlation over
all oracled nodes, plus the verdict and catastrophe-crux comparison. This is a
REFERENCE check — the oracle is NOT wired into the graph config (calibration
activation is parked; see archive/calibration-handoff/).

Run from v0/:  python3 blackholes-graph/oracle/score_panel.py
"""
import json
import statistics as st
from pathlib import Path

BH = Path(__file__).resolve().parent.parent
anc = json.loads((BH / "anchors.json").read_text())
oracle = {n: anc["nodes"][n]["oracle_mean"] for n in anc["nodes"]}
panel = {n["id"]: (n.get("agreement") or {}).get("mean")
         for n in json.loads((BH / "graph.json").read_text())["nodes"]}

common = [n for n in oracle if panel.get(n) is not None]
mae = st.mean(abs(panel[n] - oracle[n]) for n in common)
mx = st.mean(oracle[n] for n in common)
my = st.mean(panel[n] for n in common)
num = sum((oracle[n] - mx) * (panel[n] - my) for n in common)
den = (sum((oracle[n] - mx) ** 2 for n in common) * sum((panel[n] - my) ** 2 for n in common)) ** 0.5

print(f"BH 20-rater panel vs 4-model oracle over {len(common)} nodes:")
print(f"  MAE = {mae:.3f}   r = {num / den:.3f}")
print(f"  verdict  n001 safe: panel {panel['n001']:.2f} / oracle {oracle['n001']}"
      f"   n002 catastrophe: panel {panel['n002']:.2f} / oracle {oracle['n002']}")
for n in ("n019", "n068"):
    print(f"  catastrophe crux {n}: panel {panel[n]:.2f} / oracle {oracle[n]}")
av = sorted(oracle[n] for n in anc["calibration_anchors"])
print(f"  calibration-anchor truth spread: {av[0]}..{av[-1]} (n={len(av)}) "
      f"-- clustered high, so calibration would mis-extrapolate (kept anchor-free).")
