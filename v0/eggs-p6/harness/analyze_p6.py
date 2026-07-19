#!/usr/bin/env python3
"""eggs-p6 biased-bootstrap flywheel analysis.

Population: 16 biased Haiku + 4 competent Sonnet, saturated on 79 nodes.
Truth oracle (independent): eggs-p5's 8 experts' mean per node.
Competence of a p6 rater := correlation of their ratings with oracle truth.

Three scoring arms, each a True_R-weighted fixed-point, compared on how close the
resulting consensus gets to truth — especially on the biased cluster:
  A FLAT           — unweighted mean (no reputation).
  B DISC-ONLY      — reputation = discrimination vs the (weighted) consensus. Self-
                     referential: the competent minority anti-correlates with the
                     biased consensus, so this is predicted to FAIL to find them.
  C DISC+ANCHORS   — reputation blends discrimination with agreement-vs-ANCHOR-TRUTH
                     on a few high-confidence anchor items (external ground truth,
                     independent of the crowd consensus -> breaks the self-reference).

The clean test is consensus~truth on the NON-anchor biased items — the ones anchors
did NOT directly hand over — which improve only if anchor-calibrated reputation
correctly upweights the competent minority globally.
"""
import json, math, statistics as st, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent))
from reasonable import store, fold  # noqa

PRIOR, K = 0.15, 8.0
N_ANCHORS = 10
ANCHOR_BLEND = 0.6   # weight on anchor-agreement in Raw_R (rest on discrimination)

roster = json.loads((HERE / "roster.json").read_text())
tier = {a["id"]: a["tier"] for a in roster["agents"]}

# p6 ratings
p6 = fold.fold(store.read_events("eggs-p6"))
items = {}
for t, dm in p6["ratings"].items():
    if "A" in dm and t.startswith("n"):
        cell = {a: v for a, v in dm["A"].items() if v != "abstain" and a in tier}
        if cell:
            items[t] = cell

# oracle truth + oracle confidence (stdev) from eggs-p5 experts
p5 = fold.fold(store.read_events("eggs-p5"))
r5 = json.loads((HERE.parent.parent / "eggs-p5/harness/roster.json").read_text())
etier = {a["id"]: a["tier"] for a in r5["agents"]}
truth, ostd = {}, {}
for t, dm in p5["ratings"].items():
    if "A" in dm:
        ev = [v for a, v in dm["A"].items() if etier.get(a) == "expert" and v != "abstain"]
        if len(ev) >= 3:
            truth[t] = st.mean(ev); ostd[t] = st.pstdev(ev)


def pear(xs, ys):
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs)/n, sum(ys)/n
    num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
    return num/(dx*dy) if dx and dy else 0.0


ids = [a for a in tier if any(a in items[t] for t in items)]
# external competence: each rater's corr with oracle truth
comp = {}
for a in ids:
    pts = [(items[t][a], truth[t]) for t in items if a in items[t] and t in truth]
    if len(pts) >= 5:
        comp[a] = pear([p[0] for p in pts], [p[1] for p in pts])

# anchors = highest-confidence oracle items (lowest expert stdev, tie-break extremeness)
anchor_items = sorted([t for t in truth if t in items],
                      key=lambda t: (ostd[t], -abs(truth[t]-2.5)))[:N_ANCHORS]
anchor_set = set(anchor_items)

# biased cluster = items where the FLAT (unweighted) consensus is farthest from truth
flat = {t: st.mean(items[t].values()) for t in items}
biased_cluster = sorted([t for t in items if t in truth],
                        key=lambda t: -abs(flat[t]-truth[t]))[:18]
nonanchor_biased = [t for t in biased_cluster if t not in anchor_set]


def weighted_consensus(w):
    out = {}
    for t, cell in items.items():
        num = den = 0.0
        for a, v in cell.items():
            wa = w.get(a, PRIOR); num += wa*v; den += wa
        out[t] = num/den if den else st.mean(cell.values())
    return out


def discrimination(cons):
    by = defaultdict(list)
    for t, cell in items.items():
        for a, v in cell.items():
            by[a].append((v, cons[t]))
    return {a: pear([p[0] for p in pr], [p[1] for p in pr]) for a, pr in by.items() if len(pr) >= 5}


# anchors ON the contested cluster (where the bias bites) — the realistic strategy:
# you anchor the CONTROVERSIAL questions you have a defensible answer to, not the obvious ones.
anchors_contested = sorted([t for t in biased_cluster if t in truth],
                           key=lambda t: ostd[t])[:10]


def anchor_score_for(a, aset):
    pts = [abs(items[t][a]-truth[t])/5 for t in aset if a in items[t]]
    return (1 - sum(pts)/len(pts)) if pts else None


n_given = {a: sum(1 for t in items if a in items[t]) for a in ids}


def wcons_gamma(w, gamma):
    out = {}
    for t, cell in items.items():
        num = den = 0.0
        for a, v in cell.items():
            wa = (w.get(a, PRIOR)) ** gamma
            num += wa*v; den += wa
        out[t] = num/den if den else st.mean(cell.values())
    return out


def run_arm(mode, aset=None, eval_biased=None, blend=ANCHOR_BLEND, gamma=1.0):
    ANCH = {a: anchor_score_for(a, aset) for a in ids} if aset else {}
    eval_biased = eval_biased if eval_biased is not None else nonanchor_biased
    w = {a: PRIOR for a in ids}
    for _ in range(30):
        cons = wcons_gamma(w, gamma)
        disc = discrimination(cons)
        neww = {}
        for a in ids:
            d = max(0.0, disc.get(a, 0.0))
            if mode == "flat":
                raw = PRIOR
            elif mode == "disc":
                raw = d
            else:  # disc+anchors
                an = ANCH.get(a)
                raw = (blend*an + (1-blend)*d) if an is not None else d
            conf = n_given[a]/(n_given[a]+K)
            neww[a] = PRIOR + conf*(raw - PRIOR)
        if max(abs(neww[a]-w[a]) for a in ids) < 1e-4:
            w = neww; break
        w = neww
    cons = wcons_gamma(w, gamma)

    def ctruth(keys):
        keys = [t for t in keys if t in truth]
        return pear([cons[t] for t in keys], [truth[t] for t in keys]), \
            st.mean([abs(cons[t]-truth[t]) for t in keys])
    all_c, all_m = ctruth(list(items))
    bc_c, bc_m = ctruth(biased_cluster)
    nab_c, nab_m = ctruth(eval_biased)
    comp_ids = [a for a in ids if a in comp]
    rep_comp = pear([comp[a] for a in comp_ids], [w[a] for a in comp_ids])
    w_competent = st.mean([w[a] for a in ids if tier[a] == "competent"])
    w_biased = st.mean([w[a] for a in ids if tier[a] == "biased"])
    return dict(all_corr=all_c, all_mae=all_m, bc_corr=bc_c, bc_mae=bc_m,
                nab_corr=nab_c, nab_mae=nab_m, rep_comp=rep_comp,
                w_comp=w_competent, w_bias=w_biased)


print(f"p6 population: {sum(1 for a in ids if tier[a]=='biased')} biased, "
      f"{sum(1 for a in ids if tier[a]=='competent')} competent; {len(items)} nodes")
print(f"external competence (corr w/ oracle truth): "
      f"biased mean {st.mean([comp[a] for a in comp if tier[a]=='biased']):.2f}, "
      f"competent mean {st.mean([comp[a] for a in comp if tier[a]=='competent']):.2f}")
print(f"anchors: {len(anchor_items)} highest-confidence items; biased cluster: {len(biased_cluster)} "
      f"items ({len(nonanchor_biased)} of them NON-anchor)\n")
contested_nonanchor = [t for t in biased_cluster if t not in set(anchors_contested)]
arms = [
    ("A flat", "flat", None, nonanchor_biased),
    ("B disc-only", "disc", None, nonanchor_biased),
    ("C anchors=easy", "anchors", anchor_items, nonanchor_biased),
    ("D anchors=contested", "anchors", anchors_contested, contested_nonanchor),
]
print(f"{'arm':<20}{'cons~truth(all)':>16}{'biasedClust':>13}{'held-out bias':>15}{'rep~comp':>9}{'w:comp/bias':>13}")
for name, mode, aset, evb in arms:
    r = run_arm(mode, aset, evb)
    print(f"{name:<20}{r['all_corr']:>9.2f}(M{r['all_mae']:.2f}){r['bc_corr']:>8.2f}(M{r['bc_mae']:.2f})"
          f"{r['nab_corr']:>8.2f}(M{r['nab_mae']:.2f}){r['rep_comp']:>9.2f}{r['w_comp']:>6.2f}/{r['w_bias']:.2f}")
print("\nrep~comp: +1 = reputation tracks true competence, - = inverted (competent buried).")
print("held-out bias = cons~truth on biased items NOT used as anchors (the generalization test).")
print("C anchors on easy/uncontested items vs D anchors on the CONTESTED cluster where the bias bites.")

print("\n--- Can ANY scheme fix the consensus? contested anchors, sweep anchor-trust (blend) x weight-power (gamma) ---")
print(f"{'blend':>6}{'gamma':>6}{'rep~comp':>9}{'held-out bias corr':>20}{'w:comp/bias':>13}")
for blend in (0.6, 0.9, 0.99):
    for gamma in (1.0, 3.0, 6.0):
        r = run_arm("anchors", anchors_contested, contested_nonanchor, blend=blend, gamma=gamma)
        print(f"{blend:>6.2f}{gamma:>6.1f}{r['rep_comp']:>9.2f}{r['nab_corr']:>13.2f}(M{r['nab_mae']:.2f})"
              f"{r['w_comp']:>7.2f}/{r['w_bias']:.2f}")
print("\nIf even high anchor-trust + steep weighting can't flip held-out bias corr positive, then LINEAR/weighted")
print("aggregation cannot beat a 4:1 biased supermajority -- you must change the POOL (routing/gating), not just weights.")
