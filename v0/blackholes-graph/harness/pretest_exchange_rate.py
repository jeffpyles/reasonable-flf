#!/usr/bin/env python3
"""Pre-analysis grounding the tiering-test design (TIERING-TEST-PLAN.md §2).

Mines EXISTING eggs-p5 data (52 Haiku "crowd" + 8 Sonnet "expert" raters on 79
shared items) to estimate, before spending on any new run:
  - the cheap-swarm-vs-expert-panel MEAN exchange rate + plateau (how many cheap
    raters approximate the expert panel's mean), and
  - whether the cheap swarm reproduces the expert DISPERSION map.

No agents; pure computation over committed logs. Re-run: `python3 pretest_exchange_rate.py`.
"""
import json, math, statistics as st, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent          # v0/
sys.path.insert(0, str(ROOT))
from reasonable import store, fold  # noqa

SRC = "eggs-p5"   # expert-saturation run: 8 Sonnet experts rated all items
roster = json.loads((ROOT / SRC / "harness/roster.json").read_text())["agents"]
tier = {a["id"]: a["tier"] for a in roster}
f = fold.fold(store.read_events(ROOT / SRC))


def pear(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx and dy else float("nan")


crowd, expert = {}, {}
for t, dm in f["ratings"].items():
    if "A" not in dm:
        continue
    cv = [v for a, v in dm["A"].items() if tier.get(a) == "crowd" and isinstance(v, (int, float))]
    ev = [v for a, v in dm["A"].items() if tier.get(a) == "expert" and isinstance(v, (int, float))]
    if len(ev) >= 6 and len(cv) >= 8:
        crowd[t], expert[t] = cv, ev

items = sorted(crowd)
emean = {t: st.mean(expert[t]) for t in items}
RNG = random.Random(42)
print(f"source={SRC}  comparable items (>=6 expert & >=8 crowd): {len(items)}")
print(f"full {max(len(crowd[t]) for t in items)}-max-crowd mean vs expert mean: "
      f"r={pear([st.mean(crowd[t]) for t in items], [emean[t] for t in items]):.3f}")
print(f"crowd-vs-expert mean bias: "
      f"{st.mean([st.mean(crowd[t]) for t in items]) - st.mean(list(emean.values())):+.2f}\n")

print(f"{'K cheap raters':>15}   r(cheap-mean vs expert-mean)")
for K in (1, 2, 3, 5, 8, 12, 20, 32):
    rs = []
    for _ in range(60):
        cm = [st.mean(crowd[t] if K >= len(crowd[t]) else RNG.sample(crowd[t], K)) for t in items]
        r = pear(cm, [emean[t] for t in items])
        if not math.isnan(r):
            rs.append(r)
    print(f"{K:>15}   {st.mean(rs):.3f}")

cstd = [st.pstdev(crowd[t]) for t in items]
estd = [st.pstdev(expert[t]) for t in items]
print(f"\ndispersion map — r(crowd-stdev vs expert-stdev): {pear(cstd, estd):.3f}")
print("interpretation: mean plateaus by K~6-8 near the ceiling; dispersion does NOT reproduce")
print("(second moment, noisy at this N, and eggs crowd was biased). See TIERING-TEST-PLAN.md §2.")
