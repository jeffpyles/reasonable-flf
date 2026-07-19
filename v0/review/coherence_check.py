#!/usr/bin/env python3
"""Feasibility probe: STRUCTURAL-COHERENCE scoring -- a rater-quality signal no
current rule uses, and the only one that is both crowd-independent AND
oracle-independent.

Idea: the graph is not a flat rating matrix; it has edges with (post-v1.2)
conditional semantics. If a rater says Ground A ~ likely true (node-A high) and
the edge's inference is strong (edge-A high), then by the chain rule their
belief in the Dependent shouldn't be far below ground*edge -- p(dep) >=
p(ground)*p(edge|ground) under the v1.2 reading. A rater whose OWN ratings are
mutually incoherent (premise 5, inference 5, conclusion 1) is demonstrably
sloppy with NO reference to consensus, anchors, or any oracle. Coherence can't
prove competence (a consistently wrong worldview can be perfectly coherent --
it's necessary, not sufficient) but incoherence is a clean carelessness signal,
exactly the thing the 'care' axis wanted to measure and the noisy prompt-label
couldn't.

This probe: on eggs-p4 (the only log where the same raters rated node-A AND
edge-A), count how many (rater, edge) triples exist where the rater rated the
ground's A, the edge's A, and the dependent's A; compute each rater's mean
chain-rule violation max(0, g*e - d) over their triples (g,e,d = the three
ratings /5); and correlate with tier/care.

Expected outcome given sortition sparsity: few triples -- in which case the
finding is a DESIGN gap (assignment never co-locates a rater on an edge and
both its endpoints, so the one crowd-independent signal is unmeasurable), which
is itself worth knowing before the next run.
"""
import json, math, statistics as st, sys
from collections import defaultdict
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from reasonable import store, fold  # noqa

st4 = fold.fold(store.read_events("eggs-p4"))
roster = json.loads((HERE.parent / "eggs-p4/harness/roster.json").read_text())
tier = {a["id"]: a["tier"] for a in roster["agents"]}
care_rank = {a["id"]: (3 if a["tier"] == "expert" else {"high": 2, "mid": 1, "hasty": 0}[a["care"]])
             for a in roster["agents"]}

# rater -> {target: value} for dim A
rA = defaultdict(dict)
for target, dmap in st4["ratings"].items():
    if "A" in dmap:
        for a, v in dmap["A"].items():
            if v != "abstain" and a in tier:
                rA[a][target] = v

edges = st4["edges"]
triples_per = defaultdict(list)
for a, targets in rA.items():
    for eid, e in edges.items():
        if eid in targets and e["from"] in targets and e["to"] in targets:
            g = targets[e["from"]] / 5.0
            ee = targets[eid] / 5.0
            d = targets[e["to"]] / 5.0
            triples_per[a].append(max(0.0, g * ee - d))

n_triples = sum(len(v) for v in triples_per.values())
print(f"eggs-p4: {len(edges)} edges; raters with >=1 full (ground,edge,dependent) self-triple: "
      f"{sum(1 for v in triples_per.values() if v)}; total triples {n_triples}")
counts = sorted((len(v) for v in triples_per.values()), reverse=True)
print(f"triples per rater (top 10): {counts[:10]}")

scored = {a: st.mean(v) for a, v in triples_per.items() if len(v) >= 3}
print(f"raters with >=3 triples: {len(scored)}")
if len(scored) >= 8:
    def pear(xs, ys):
        n = len(xs); mx, my = sum(xs)/n, sum(ys)/n
        num = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
        dx = math.sqrt(sum((x-mx)**2 for x in xs)); dy = math.sqrt(sum((y-my)**2 for y in ys))
        return num/(dx*dy) if dx and dy else 0.0
    common = [a for a in scored if a in care_rank]
    print(f"corr(mean chain violation, care rank) over {len(common)} raters: "
          f"{pear([scored[a] for a in common], [care_rank[a] for a in common]):+.3f} "
          f"(negative = careful raters more coherent)")
    exp = [scored[a] for a in scored if tier[a] == 'expert']
    crd = [scored[a] for a in scored if tier[a] == 'crowd']
    if exp and crd:
        print(f"mean violation: experts {st.mean(exp):.3f}  crowd {st.mean(crd):.3f}")
else:
    print("=> TOO SPARSE to score: sortition never co-locates a rater on an edge plus both its")
    print("   endpoints. Design implication: if coherence scoring is wanted, assignment must hand")
    print("   out connected SUBGRAPHS (edge + endpoints as one unit), not independent items.")
