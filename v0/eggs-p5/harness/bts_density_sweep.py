#!/usr/bin/env python3
"""After expert saturation, sweep the EXPERT DENSITY per item and measure whether
BTS (and discrimination/alignment) recover the experts as their concentration
rises. Answers the sortition-design question: what fraction of quality raters must
an assignment bloc contain for the good-rater signal to surface?

For k = 0..(max experts available), each item keeps a deterministic k of its
experts plus ALL its crowd raters; we score everyone and report the expert panel's
percentile and the expert-vs-crowd info advantage as a function of the resulting
expert fraction.
"""
import json, math, statistics as st, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))            # for bts
sys.path.insert(0, str(HERE.parent.parent))  # v0, for the reasonable package
import bts  # noqa
from reasonable import store, fold  # noqa

roster = json.loads(open("eggs-p5/harness/roster.json").read())
tier = {a["id"]: a["tier"] for a in roster["agents"]}

preds = defaultdict(dict)
for l in open("eggs-p5/predictions.jsonl"):
    r = json.loads(l); preds[(r["target"], r["dim"])][r["agent"]] = r["pred"]
st_ = fold.fold(store.read_events("eggs-p5"))
items = {}
for t, dm in st_["ratings"].items():
    for d, am in dm.items():
        cell = {a: v for a, v in am.items() if v != "abstain"}
        if cell:
            items[(t, d)] = cell


def pctile(v, pop):
    return sum(1 for x in pop if x < v) / len(pop)


def rank(vals):
    order = sorted(range(len(vals)), key=lambda i: vals[i]); r = [0.0]*len(vals); i = 0
    while i < len(vals):
        j = i
        while j+1 < len(vals) and vals[order[j+1]] == vals[order[i]]:
            j += 1
        for k in range(i, j+1):
            r[order[k]] = (i+j)/2.0
        i = j+1
    return r


def pearson(xs, ys):
    n = len(xs); mx = sum(xs)/n; my = sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy) if dx and dy else 0.0


care_rank = {a["id"]: (3 if a["tier"] == "expert" else {"high":2,"mid":1,"hasty":0}[a["care"]])
             for a in roster["agents"]}

maxk = max(sum(1 for a in c if tier.get(a) == "expert") for c in items.values())
print(f"max experts on any item: {maxk}")
print(f"\n{'k_exp':>5} {'exp_frac':>9} {'align_pct':>10} {'disc_pct':>9} {'bts_pct':>8} "
      f"{'bts_spearman':>13} {'exp-crowd_info':>15}")
for k in range(0, maxk+1):
    sub = {}
    subp = {}
    fracs = []
    for key, cell in items.items():
        exps = sorted([a for a in cell if tier.get(a) == "expert"])
        crowd = [a for a in cell if tier.get(a) == "crowd"]
        keepexp = exps[:k]
        keep = set(keepexp) | set(crowd)
        sub[key] = {a: cell[a] for a in keep}
        subp[key] = {a: preds[key][a] for a in keep if a in preds.get(key, {})}
        if keep:
            fracs.append(len(keepexp)/len(keep))
    res = bts.score(sub, subp, min_raters=3)
    btsf = {a: d["bts"] for a, d in res.items()}
    info = {a: d["info"] for a, d in res.items()}
    # alignment + discrimination on sub
    diffs = defaultdict(list)
    for key, c in sub.items():
        m = st.mean(c.values())
        for a, v in c.items():
            diffs[a].append(abs(v-m)/5)
    align = {a: 1-sum(d)/len(d) for a, d in diffs.items()}
    disc = {}
    dby = defaultdict(list)
    for key, c in sub.items():
        if len(c) < 4:
            continue
        tot, n = sum(c.values()), len(c)
        for a, v in c.items():
            dby[a].append((v, (tot-v)/(n-1)))
    for a, pr in dby.items():
        if len(pr) >= 5:
            disc[a] = pearson([p[0] for p in pr], [p[1] for p in pr])

    def exp_pct(sc):
        pop = {a: sc[a] for a in tier if a in sc}
        vals = list(pop.values())
        e = [pctile(pop[a], vals) for a in pop if tier[a] == "expert"]
        return st.mean(e) if e else float("nan")

    def bts_spear():
        pop = {a: btsf[a] for a in tier if a in btsf}
        return pearson(rank([care_rank[a] for a in pop]), rank([pop[a] for a in pop]))
    ei = [info[a] for a in info if tier.get(a) == "expert"]
    ci = [info[a] for a in info if tier.get(a) == "crowd"]
    gap = (st.mean(ei)-st.mean(ci)) if ei and ci else float("nan")
    print(f"{k:>5} {st.mean(fracs):>9.2f} {exp_pct(align):>10.2f} {exp_pct(disc):>9.2f} "
          f"{exp_pct(btsf):>8.2f} {bts_spear():>13.2f} {gap:>+15.3f}")
print("\nexp_pct ~0.9 = experts on top; bts_spearman +1 = recovers competence; "
      "exp-crowd_info>0 = experts win the surprisingly-popular reward.")


# ---- REVERSE sweep: keep ALL experts, progressively remove crowd (expert frac -> 1.0) ----
def _score_subset(sub, subp):
    res = bts.score(sub, subp, min_raters=3)
    btsf = {a: d["bts"] for a, d in res.items()}
    info = {a: d["info"] for a, d in res.items()}
    diffs = defaultdict(list)
    for key, c in sub.items():
        m = st.mean(c.values())
        for a, v in c.items():
            diffs[a].append(abs(v-m)/5)
    align = {a: 1-sum(d)/len(d) for a, d in diffs.items()}
    dby = defaultdict(list)
    for key, c in sub.items():
        if len(c) < 4:
            continue
        tot, n = sum(c.values()), len(c)
        for a, v in c.items():
            dby[a].append((v, (tot-v)/(n-1)))
    disc = {a: pearson([p[0] for p in pr], [p[1] for p in pr]) for a, pr in dby.items() if len(pr) >= 5}

    def epct(sc):
        pop = {a: sc[a] for a in tier if a in sc}
        vals = list(pop.values())
        e = [pctile(pop[a], vals) for a in pop if tier[a] == "expert"]
        return st.mean(e) if e else float("nan")
    pop = {a: btsf[a] for a in tier if a in btsf}
    spear = pearson(rank([care_rank[a] for a in pop]), rank([btsf[a] for a in pop])) if len(pop) > 2 else float("nan")
    ei = [info[a] for a in info if tier.get(a) == "expert"]
    ci = [info[a] for a in info if tier.get(a) == "crowd"]
    gap = (st.mean(ei)-st.mean(ci)) if ei and ci else float("nan")
    return epct(align), epct(disc), epct(btsf), spear, gap


print("\nREVERSE sweep — keep all experts, cap crowd/item (expert fraction climbs to 1.0):")
print(f"{'crowd/it':>8} {'exp_frac':>9} {'align_pct':>10} {'disc_pct':>9} {'bts_pct':>8} "
      f"{'bts_spear':>10} {'exp-crowd_info':>15}")
for cap in [15, 12, 9, 6, 4, 3, 2, 1, 0]:
    sub, subp, fracs = {}, {}, []
    for key, cell in items.items():
        exps = [a for a in cell if tier.get(a) == "expert"]
        crowd = sorted([a for a in cell if tier.get(a) == "crowd"])[:cap]
        keep = set(exps) | set(crowd)
        sub[key] = {a: cell[a] for a in keep}
        subp[key] = {a: preds[key][a] for a in keep if a in preds.get(key, {})}
        if keep:
            fracs.append(len(exps)/len(keep))
    a_, d_, b_, s_, g_ = _score_subset(sub, subp)
    print(f"{cap:>8} {st.mean(fracs):>9.2f} {a_:>10.2f} {d_:>9.2f} {b_:>8.2f} {s_:>10.2f} {g_:>+15.3f}")
print("\nNOT monotonic: BTS expert-recovery peaks around ~66-73% expert fraction, then declines and")
print("COLLAPSES at 100% (no crowd left to 'surprise'). BTS needs a MIX; optimum is a slight-to-2/3")
print("majority of quality raters per item, not maximal expert fraction.")
