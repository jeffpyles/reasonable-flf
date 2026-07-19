#!/usr/bin/env python3
"""Denser-reference resolution of the dispersion question (TIERING-RESULTS.md follow-up).

The tiering test found the Haiku-vs-Sonnet dispersion correlation near zero, but the
Sonnet reference was only 4 raters, so its dispersion estimate was itself noisy —
we could only make the conditional claim. This adds 8 more Sonnet lens-raters on a
fixed ~69-node structural subset (12 Sonnet total) and reports:
  1. the Sonnet 6v6 dispersion self-reliability CEILING (is dispersion even a
     reproducible signal for the expert panel?),
  2. the Haiku 8v8 self-reliability on the same subset,
  3. the observed Haiku-16 vs Sonnet-12 dispersion correlation (overall + within
     contested-by-design), against the old Haiku-16 vs Sonnet-4 number, and
  4. an attenuation-corrected estimate of the true correlation.
Node ratings only, on the committed subset. Stdlib + reasonable package.
"""
import json, math, statistics as st, random, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
sys.path.insert(0, str(ROOT))
from reasonable import store  # noqa
RNG = random.Random(101)

sub = json.loads((HERE / "dispersion_subset.json").read_text())
SUBSET = sub["subset"]
CONTESTED = [n for n in sub["contested_by_design"] if n in set(SUBSET)]

SONNET4 = ["panel-evidential", "panel-bayesian", "panel-skeptic", "panel-domain"]
SONNET_NEW = [f"{l}-s{s}" for l in ("ev", "bayes", "skeptic", "domain") for s in (2, 3)]
SONNET12 = SONNET4 + SONNET_NEW
HAIKU16 = [f"{l}-h{s}" for l in ("ev", "bayes", "skeptic", "domain") for s in (1, 2, 3, 4)]

R = {}
for e in store.read_events(ROOT / "covid-graph"):
    if e["verb"] != "rate":
        continue
    p = e["payload"]
    if p.get("dim") != "A" or p.get("target") not in set(SUBSET):
        continue
    v = p.get("value")
    if isinstance(v, (int, float)):
        R.setdefault(e["agent"], {})[p["target"]] = v

present = [a for a in SONNET12 if a in R]
print(f"subset: {len(SUBSET)} nodes ({len(CONTESTED)} contested-by-design + {len(SUBSET)-len(CONTESTED)} settled)")
print(f"Sonnet raters present: {len(present)}/12  ·  Haiku present: {sum(a in R for a in HAIKU16)}/16\n")


def disp(raters, t):
    vals = [R[a][t] for a in raters if a in R and t in R[a]]
    return st.pstdev(vals) if len(vals) >= 2 else None


def pear(xs, ys):
    pr = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    n = len(pr)
    if n < 2:
        return float("nan")
    xs, ys = zip(*pr)
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((a-mx)*(b-my) for a, b in zip(xs, ys))
    dx = math.sqrt(sum((a-mx)**2 for a in xs)); dy = math.sqrt(sum((b-my)**2 for b in ys))
    return num/(dx*dy) if dx and dy else float("nan")


def dvec(raters, nodes):
    return [disp(raters, t) for t in nodes]


def splithalf(raters, nodes, draws=300):
    rs = []
    for _ in range(draws):
        sh = raters[:]; RNG.shuffle(sh)
        h = len(sh)//2
        r = pear(dvec(sh[:h], nodes), dvec(sh[h:2*h], nodes))
        if not math.isnan(r):
            rs.append(r)
    return st.mean(rs)


for label, nodes in (("ALL subset", SUBSET), ("contested-only", CONTESTED)):
    print(f"=== {label} ({len(nodes)} nodes) ===")
    sonnet_ceiling = splithalf(present, nodes)          # 6v6 among the 12 Sonnet
    haiku_rel = splithalf(HAIKU16, nodes)               # 8v8 among the 16 Haiku
    r_h_s12 = pear(dvec(HAIKU16, nodes), dvec(present, nodes))
    r_h_s4 = pear(dvec(HAIKU16, nodes), dvec(SONNET4, nodes))
    r_s12_s4 = pear(dvec(present, nodes), dvec(SONNET4, nodes))
    # Spearman-Brown: split-half r (halves of size n/2) -> reliability of the FULL panel.
    def sb(rhalf):
        return (2 * rhalf) / (1 + rhalf) if rhalf > -1 else float("nan")
    rel_sonnet_full = sb(sonnet_ceiling)   # reliability of the 12-Sonnet dispersion estimate
    rel_haiku_full = sb(haiku_rel)         # reliability of the 16-Haiku dispersion estimate
    denom = math.sqrt(max(rel_sonnet_full, 1e-6) * max(rel_haiku_full, 1e-6))
    corrected = r_h_s12 / denom if denom else float("nan")
    print(f"  Sonnet 6v6 dispersion split-half (independent halves):{sonnet_ceiling:.3f}"
          f"  -> full-12 reliability {rel_sonnet_full:.3f}")
    print(f"  Haiku  8v8 dispersion split-half:                     {haiku_rel:.3f}"
          f"  -> full-16 reliability {rel_haiku_full:.3f}")
    print(f"  Haiku-16 vs Sonnet-12 dispersion r (observed):        {r_h_s12:.3f}")
    print(f"  Haiku-16 vs Sonnet-4  dispersion r (old reference):   {r_h_s4:.3f}")
    print(f"  Sonnet-12 vs Sonnet-4 dispersion r (OVERLAP-inflated, 4 in 12): {r_s12_s4:.3f}")
    print(f"  attenuation-corrected true Haiku-vs-Sonnet r (approx): {corrected:.3f}")
    print()
print("Reading: if the Sonnet CEILING is high but Haiku-vs-Sonnet stays low even corrected,")
print("cheap raters genuinely miss the crux map. If the CEILING is itself low, dispersion is")
print("intrinsically hard to reproduce even for experts — a caveat on the whole signal.")
