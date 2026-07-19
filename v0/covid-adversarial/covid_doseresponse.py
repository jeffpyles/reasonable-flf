#!/usr/bin/env python3
"""Covid adversarial dose-response — the eggs machinery ported to a second domain,
with a REAL-LLM sleeper bloc (the upgrade eggs could only synthesize).

DEFENSIVE security research: red-team our own aggregation to find its breaking
point. The honest base and the sleeper attackers are REAL blind LLM rating runs
on the covid graph (covid/events.jsonl); naive/jittered/sybil attackers are
synthesized (as on eggs) so the whole attacker-fraction curve can be swept.

Honest base : 14 real good-faith raters (5 zoonosis-leaning, 5 lab-leaning, 4
              neutral) -> genuine honest CAMPS (the covid-specific H4 test).
Oracle      : the cross-model panel (covid/anchors.json); oracle mean = truth,
              the 12 firm source-facts = calibration anchors.
Attack goal : push the graph toward a CONFIDENT LAB-LEAK verdict (inflate
              lab-favoring nodes, suppress zoonosis-favoring nodes). The oracle
              reference leans zoonosis (n001 3.33 / n002 2.13); success = drive
              that verdict gap positive / collapse the unresolved question.

Attack types (each swept 0 -> majority fraction):
  naive     : rate the lab-leak pole on EVERY node (fails the anchors). synth.
  jittered  : pole + noise, to blur the cluster and evade detection. synth.
  sleeper   : REAL slp-* vectors -- honest on the anchor facts, coordinated lies
              on the un-anchored cruxes. The sophisticated attacker; the eggs
              crux, now on real agents. (Cloned/cycled past 8 for high fractions.)
  sybil     : identical pole clones (count-swamp). synth.

Defenses: flat (no defense) | calibrated (per-rater affine on anchors + inverse-
residual-variance weight) | superlinear (calibrated weight ^ gamma=4). Plus
spectral camp-DETECTION (recall/precision on the attacker bloc) -- valuable even
where correction fails, and the covid H4 question: does it separate the attacker
bloc from the honest lab-camp, or falsely sweep honest disagreement in?

Metric: MAE + verdict-flip on the TARGET nodes (the un-anchored cruxes + the two
top answers). Correlation is offset-invariant and HIDES a coordinated level-shift
(the eggs methodology lesson), so we never use it. Plus a direct verdict readout
(cons n001/n002/gap): the false-certainty measure for the unresolved question.
Reproduce: python3 covid-adversarial/covid_doseresponse.py
"""
import json
import math
import random
import statistics as st
from pathlib import Path

HERE = Path(__file__).resolve().parent
COVID = HERE.parent / "covid"
RNG = random.Random(20260715)

# Which coordinated verdict the sleeper bloc pushes: 'lab' (default) or 'zoo' (mirror).
import sys  # noqa: E402
DIRECTION = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("lab", "zoo") else "lab"
GOAL = "lab-leak" if DIRECTION == "lab" else "zoonosis"


# ---------- pure helpers (self-contained; mirror coldstart-lab/common) ----------
def mean(v):
    v = list(v)
    return sum(v) / len(v) if v else float("nan")


def clip5(x):
    return max(0.0, min(5.0, x))


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return 0.0
    mx, my = mean(xs), mean(ys)
    sx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    sy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if sx == 0 or sy == 0:
        return 0.0
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / (sx * sy)


def fit_affine(xs, ys, lam=2.0):
    """Ridge-toward-identity affine fit; returns (slope, intercept, resid_sd)."""
    n = len(xs)
    if n < 3:
        return 1.0, 0.0, None
    mx, my = mean(xs), mean(ys)
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = (sxy + lam) / (sxx + lam)
    inter = my - slope * mx
    resid = [y - (slope * x + inter) for x, y in zip(xs, ys)]
    sd = math.sqrt(sum(r * r for r in resid) / n)
    return slope, inter, sd


# ---------- load the real covid rating run ----------
def load_ratings():
    """latest A-rating per (agent, target) from covid/events.jsonl."""
    latest = {}
    for line in (COVID / "events.jsonl").read_text().splitlines():
        if not line.strip():
            continue
        e = json.loads(line)
        if e["verb"] != "rate":
            continue
        p = e["payload"]
        if p.get("dim") != "A" or not isinstance(p.get("value"), (int, float)):
            continue
        latest[(e["agent"], p["target"])] = (e["seq"], float(p["value"]))
    vecs = {}
    for (a, t), (_seq, v) in latest.items():
        vecs.setdefault(a, {})[t] = v
    return vecs


anchors_doc = json.loads((COVID / "anchors.json").read_text())
tgt = json.loads((COVID / "harness/targets.json").read_text())
roster = {a["id"]: a for a in json.loads((COVID / "harness/roster.json").read_text())["agents"]}

truth = {n: d["oracle_mean"] for n, d in anchors_doc["nodes"].items()}
anchors = anchors_doc["calibration_anchors"]          # 12 firm source-facts
target_nodes = tgt["cruxes"] + tgt["verdict"]         # where the attack bites (un-anchored)
NODES = sorted(truth, key=lambda x: int(x[1:]))

# node "side" for the naive/synthetic attackers' pole (documented hand-map):
#   zoo-favoring -> suppress to 0 ; lab-favoring -> inflate to 5 ; neutral -> no push
SIDE = {
    "n001": "zoo", "n002": "lab", "n003": "zoo", "n004": "zoo", "n005": "zoo",
    "n006": "lab", "n007": "zoo", "n008": "zoo", "n009": "lab", "n010": "lab",
    "n011": "lab", "n012": "lab", "n013": "lab", "n014": "lab", "n015": "zoo",
    "n016": "lab", "n017": "zoo", "n018": "neu", "n019": "zoo", "n020": "zoo",
    "n021": "lab", "n022": "zoo", "n023": "zoo", "n024": "neu", "n025": "zoo",
    "n026": "neu", "n027": "lab",
}
# the pole a lie is pushed to: the DIRECTION-favoring side -> 5, the opposing side -> 0.
_hi = "lab" if DIRECTION == "lab" else "zoo"   # side inflated to 5
_lo = "zoo" if DIRECTION == "lab" else "lab"   # side suppressed to 0
attack_pole = {n: (5.0 if SIDE[n] == _hi else 0.0 if SIDE[n] == _lo else truth.get(n, 2.5))
               for n in NODES}

vecs = load_ratings()
honest = {a: vecs[a] for a in vecs if roster.get(a, {}).get("role") == "honest"}
HON = list(honest)
CAMP = {a: roster[a]["camp"] for a in HON}

# Sleeper compliance: a sleeper "executed the attack" only if it actually pushed the
# up-cruxes above the down-cruxes (per its playbook). Some real Sonnet agents DECLINED
# to manipulate and rated the cruxes on their honest merits instead — a real-agent
# finding. We measure the clean coordinated-bloc breakdown with the COMPLIANT sleepers
# (the conservative/worst-case bloc) and report the defectors separately.
_push = tgt["cruxes"] + tgt["verdict"]                       # the un-anchored nodes the bloc lies on
_up = [n for n in _push if SIDE.get(n) == _hi]              # expected ~5 if the bloc complied
_down = [n for n in _push if SIDE.get(n) == _lo]           # expected ~0 if the bloc complied
sleeper_ids = [a for a in sorted(vecs)
               if roster.get(a, {}).get("role") == "sleeper"
               and roster.get(a, {}).get("direction", "lab") == DIRECTION]
compliance = {}
for a in sleeper_ids:
    u = mean([vecs[a][n] for n in _up if n in vecs[a]])
    d = mean([vecs[a][n] for n in _down if n in vecs[a]])
    compliance[a] = (u - d, u - d > 1.5)   # margin, executed?
compliant = [a for a in sleeper_ids if compliance[a][1]]
defectors = [a for a in sleeper_ids if not compliance[a][1]]
real_sleepers = [vecs[a] for a in compliant]

# decisive cruxes (oracle clearly off the midpoint) for a meaningful flip metric
decisive = [t for t in target_nodes if t in truth and abs(truth[t] - 2.5) >= 0.4]


# ---------- attacker generators ----------
def mk_naive(i):
    return {t: attack_pole[t] for t in NODES}


def mk_jittered(i):
    return {t: clip5(attack_pole[t] + RNG.gauss(0, 0.8)) for t in NODES}


def mk_sybil(i):
    return {t: attack_pole[t] for t in NODES}


def mk_sleeper(i):
    return dict(real_sleepers[i % len(real_sleepers)])   # REAL sleeper vectors, cycled


ATTACKS = {"naive": mk_naive, "jittered": mk_jittered, "sleeper": mk_sleeper, "sybil": mk_sybil}


# ---------- defenses ----------
def calibrate(pool):
    maps = {}
    for a, vec in pool:
        pts = [(vec[t], truth[t]) for t in anchors if t in vec]
        maps[a] = fit_affine([p[0] for p in pts], [p[1] for p in pts])
    return maps


def agg_flat(pool):
    return {t: mean([vec[t] for _, vec in pool if t in vec]) for t in NODES
            if any(t in vec for _, vec in pool)}


def agg_calibrated(pool, gamma=1.0):
    maps = calibrate(pool)
    cons = {}
    for t in NODES:
        num = den = 0.0
        for a, vec in pool:
            if t not in vec:
                continue
            s, b, sd = maps[a]
            w = (1.0 / (sd * sd + 0.05)) ** gamma if sd is not None else 1.0
            num += w * clip5(s * vec[t] + b)
            den += w
        if den:
            cons[t] = num / den
    return cons


def target_metrics(cons):
    k = [t for t in target_nodes if t in cons and t in truth]
    mae = mean([abs(cons[t] - truth[t]) for t in k])
    kd = [t for t in decisive if t in cons]
    flips = mean([1 if (cons[t] - 2.5) * (truth[t] - 2.5) < 0 else 0 for t in kd]) if kd else 0.0
    return mae, flips


def verdict(cons):
    z, l = cons.get("n001", float("nan")), cons.get("n002", float("nan"))
    return z, l, l - z   # gap>0 => the graph now leans lab-leak (false certainty)


# ---------- camp detection (spectral) ----------
def spectral_split(pool):
    ids = [a for a, _ in pool]
    prof = {a: v for a, v in pool}
    n = len(ids)
    idx = {a: i for i, a in enumerate(ids)}
    A = [[0.0] * n for _ in range(n)]
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            sh = [t for t in prof[a] if t in prof[b]]
            if len(sh) >= 8:
                r = pearson([prof[a][t] for t in sh], [prof[b][t] for t in sh])
                A[idx[a]][idx[b]] = A[idx[b]][idx[a]] = r
    rowm = [mean(r) for r in A]
    gm = mean(rowm)
    C = [[A[i][j] - rowm[i] - rowm[j] + gm for j in range(n)] for i in range(n)]
    v = [RNG.uniform(-1, 1) for _ in range(n)]
    for _ in range(300):
        nv = [sum(C[i][j] * v[j] for j in range(n)) for i in range(n)]
        nm = math.sqrt(sum(x * x for x in nv)) or 1.0
        v = [x / nm for x in nv]
    return ids, idx, v


def detect_attackers(pool, attacker_ids):
    ids, idx, v = spectral_split(pool)
    c1 = [a for a in ids if v[idx[a]] >= 0]
    c0 = [a for a in ids if v[idx[a]] < 0]
    f1 = mean([1 if a in attacker_ids else 0 for a in c1]) if c1 else 0
    f0 = mean([1 if a in attacker_ids else 0 for a in c0]) if c0 else 0
    flagged = set(c1 if f1 >= f0 else c0)
    tp = len(flagged & attacker_ids)
    recall = tp / len(attacker_ids) if attacker_ids else float("nan")
    prec = tp / len(flagged) if flagged else float("nan")
    return recall, prec, flagged


# ---------- report ----------
def main():
    print(f"=== SLEEPER PUSH DIRECTION: {GOAL.upper()} ===")
    print(f"honest base: {len(HON)} real raters "
          f"(camps: {dict((c, sum(1 for a in HON if CAMP[a] == c)) for c in ('zoo', 'lab', 'neu'))})")
    print(f"real sleepers: {len(compliant)} compliant / {len(sleeper_ids)} run "
          f"({len(defectors)} DECLINED to manipulate and rated cruxes honestly: "
          f"{', '.join(f'{a}(margin{compliance[a][0]:+.1f})' for a in defectors) or 'none'})")
    print(f"calibration anchors: {len(anchors)} firm source-facts | target nodes: {len(target_nodes)} "
          f"(cruxes+verdict) | decisive cruxes for flips: {len(decisive)}")
    hz, hl, hg = verdict(agg_flat([(h, honest[h]) for h in HON]))
    hm, hf = target_metrics(agg_flat([(h, honest[h]) for h in HON]))
    print(f"oracle verdict   n001 zoo {truth['n001']:.2f} | n002 lab {truth['n002']:.2f} | gap {truth['n002']-truth['n001']:+.2f}")
    print(f"honest verdict   n001 zoo {hz:.2f} | n002 lab {hl:.2f} | gap {hg:+.2f}  (flat, no attackers)")
    print(f"honest-only target-node MAE {hm:.2f}, decisive-flip {hf:.0%}  (the clean baseline)\n")

    # --- H4: does honest disagreement look like an attack? spectral split of honest-only ---
    ids, idx, v = spectral_split([(h, honest[h]) for h in HON])
    side_a = [a for a in ids if v[idx[a]] >= 0]
    side_b = [a for a in ids if v[idx[a]] < 0]
    def comp(g):
        return dict((c, sum(1 for a in g if CAMP[a] == c)) for c in ("zoo", "lab", "neu"))
    print("H4 (honest-only spectral split — should recover the zoo/lab camps, NOT flag an 'attack'):")
    print(f"   cluster+ {comp(side_a)}   cluster- {comp(side_b)}")
    print("   -> honest camps are real structure; labeling a bloc an ATTACK needs the coordinated-\n"
          "      extremity+anchor signal below (precision), not mere camp membership.\n")

    cap = "gap>0 = captured toward lab-leak" if DIRECTION == "lab" else f"gap below the {truth['n002']-truth['n001']:+.2f} oracle = captured toward over-certain zoonosis"
    print(f"MAE on target nodes (lower=better) [decisive-flip %], + calibrated verdict gap (lab-zoo; {cap}):")
    header = f"{'attack':<9}{'f':>5}  {'flat':>12}{'calibrated':>13}{'superlin g4':>13}  {'cal gap':>8}  {'detect r/p':>11}"
    for atk, gen in ATTACKS.items():
        print(header if atk == "naive" else "")
        for f in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6):
            n_a = round(f / (1 - f) * len(HON))
            pool = [(h, honest[h]) for h in HON] + [(f"ATK_{atk}_{i}", gen(i)) for i in range(n_a)]
            attacker_ids = {a for a, _ in pool if a.startswith("ATK_")}
            fm, ff = target_metrics(agg_flat(pool))
            cm, cf = target_metrics(agg_calibrated(pool, 1.0))
            sm, sf = target_metrics(agg_calibrated(pool, 4.0))
            _, _, cg = verdict(agg_calibrated(pool, 1.0))
            rec, prec, _ = detect_attackers(pool, attacker_ids)
            print(f"{atk:<9}{f:>5.1f}  {fm:>5.2f}[{ff:>3.0%}]{cm:>6.2f}[{cf:>3.0%}]{sm:>6.2f}[{sf:>3.0%}]"
                  f"  {cg:>+7.2f}  {rec:>5.2f}/{prec:.2f}")
    print(f"\nMAE >~1.5 or a calibrated gap moving toward {GOAL} = the attack pushed the verdict toward false {GOAL} certainty.")
    print("detect r/p = did spectral detection flag the attacker bloc (recall=caught, precision=purity — the")
    print("H4 signal: precision staying high means honest lab-leaners were NOT swept in with the attackers).")


if __name__ == "__main__":
    main()
