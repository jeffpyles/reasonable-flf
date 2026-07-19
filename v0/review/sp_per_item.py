#!/usr/bin/env python3
"""The fix eggs-p5 diagnosed but never tested: a per-ITEM surprisingly-popular
(SP) decision (Prelec, Seung & McCoy 2017) instead of the per-rater multi-bucket
BTS info average.

BTS-RUN-FINDINGS cause #3 says the per-rater info score structurally rewards the
majority bucket, and names "a per-item surprisingly popular decision" as the
right shape -- but no script here ever scored it, even though the 1,653 rating+
prediction pairs to do so are already on disk. This closes that gap offline.

Per item: SP bin = argmax_b actual_fraction_b / predicted_fraction_b (the answer
more common than the crowd collectively predicted). A rater is rewarded when
their OWN bin is the SP bin. Two scorings:
  sp_hit  : mean over items of 1[rater's bin == SP bin]
  sp_wt   : mean over items of log(x_b/ybar_b) for the rater's bin, but ONLY
            counting items where the SP decision is non-trivial (SP bin != the
            plurality bin) -- the contested items where SP carries information.
Also reports the plurality-agreement baseline for comparison, and everything at
both sortition density (raw log) and using only items with >=3 expert raters.
"""
import json, math, statistics as st, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE.parent / "eggs-p4/harness"))
import bts  # noqa
from reasonable import store, fold  # noqa

roster = json.loads((HERE.parent / "eggs-p5/harness/roster.json").read_text())
tier = {a["id"]: a["tier"] for a in roster["agents"]}

preds = defaultdict(dict)
for l in open(HERE.parent / "eggs-p5/predictions.jsonl"):
    r = json.loads(l)
    preds[(r["target"], r["dim"])][r["agent"]] = r["pred"]
st_ = fold.fold(store.read_events("eggs-p5"))
items = {}
for t, dm in st_["ratings"].items():
    for d, am in dm.items():
        cell = {a: v for a, v in am.items() if v != "abstain" and a in tier}
        if len(cell) >= 3:
            items[(t, d)] = cell

B = bts.n_bins()
EPS = 1e-6


def pctile(v, pop):
    return sum(1 for x in pop if x < v) / len(pop)


def score_sp(item_keys):
    hit = defaultdict(list)      # rater -> [0/1 endorsed SP bin]
    wt = defaultdict(list)       # rater -> [log ratio on nontrivial-SP items]
    n_items = n_nontrivial = 0
    for key in item_keys:
        cell = items[key]
        pv = {a: p for a, p in preds.get(key, {}).items() if a in cell}
        if len(pv) < 3:
            continue
        counts = [0.0] * B
        binof = {}
        for a, v in cell.items():
            b = bts.bin_of(v)
            binof[a] = b
            counts[b] += 1
        s = sum(counts)
        x = [c / s for c in counts]
        ybar = bts._geo_mean_prediction(list(pv.values()), B)
        ratios = [(x[b] + EPS) / (ybar[b] + EPS) for b in range(B)]
        sp_bin = max(range(B), key=lambda b: ratios[b])
        plur_bin = max(range(B), key=lambda b: x[b])
        n_items += 1
        nontrivial = sp_bin != plur_bin
        if nontrivial:
            n_nontrivial += 1
        for a, b in binof.items():
            hit[a].append(1.0 if b == sp_bin else 0.0)
            if nontrivial:
                wt[a].append(math.log(ratios[b]))
    return hit, wt, n_items, n_nontrivial


def report(name, sc, min_items=5):
    pop = {a: st.mean(v) for a, v in sc.items() if len(v) >= min_items}
    if not pop:
        print(f"{name:<28} (insufficient data)")
        return
    vals = list(pop.values())
    ep = [pctile(pop[a], vals) for a in pop if tier[a] == "expert"]
    cp = [pctile(pop[a], vals) for a in pop if tier[a] == "crowd"]
    em = st.mean([pop[a] for a in pop if tier[a] == "expert"]) if ep else float("nan")
    cm = st.mean([pop[a] for a in pop if tier[a] == "crowd"]) if cp else float("nan")
    print(f"{name:<28} exp_pctile {st.mean(ep):5.2f}  crowd {st.mean(cp):5.2f}   "
          f"exp_mean {em:+.3f}  crowd_mean {cm:+.3f}  n_scored {len(pop)}")


all_keys = list(items)
dense_keys = [k for k in items if sum(1 for a in items[k] if tier[a] == "expert") >= 3]

print(f"eggs-p5: {len(all_keys)} items with >=3 raters; {len(dense_keys)} with >=3 experts\n")
for label, keys in (("ALL items (sortition density)", all_keys),
                    (">=3-expert items only", dense_keys)):
    hit, wt, ni, nn = score_sp(keys)
    print(f"--- {label}: {ni} scored items, {nn} with non-trivial SP (SP != plurality) ---")
    report("sp_hit (endorsed SP bin)", hit)
    report("sp_wt (nontrivial items)", wt, min_items=3)
    print()
print("Compare: BTS-RUN-FINDINGS reports bts_full expert pctile 0.150 (sortition) / 0.402")
print("(saturated). If sp_* lifts experts well above those, the diagnosed scoring-shape fix is")
print("real; if not, the p5 elicitation itself (self-anchored, hedged predictions) is the binding")
print("constraint and no scoring reformulation will rescue this dataset.")
