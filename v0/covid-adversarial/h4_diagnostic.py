#!/usr/bin/env python3
"""H4 diagnostic: on a genuinely camp-split question, can crude spectral camp-
detection separate the coordinated attacker bloc from the honest SAME-SIDE camp,
or does it only flag "the lab-leaning side"? And does the coordinated-extremity
signal recover the separation the spectral split alone misses?
"""
import statistics as st
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import covid_doseresponse as cd  # noqa: E402

TARGETS = cd.tgt["cruxes"] + cd.tgt["verdict"]


def extremity(vec):
    xs = [vec[n] for n in TARGETS if n in vec]
    return st.mean(abs(x - 2.5) for x in xs) if xs else float("nan")


def main():
    for f in (0.2, 0.3, 0.4):
        n_a = round(f / (1 - f) * len(cd.HON))
        pool = [(h, cd.honest[h]) for h in cd.HON] + [(f"ATK_{i}", cd.mk_sleeper(i)) for i in range(n_a)]
        pool_d = {a: v for a, v in pool}
        aid = {a for a, _ in pool if a.startswith("ATK_")}
        rec, prec, flagged = cd.detect_attackers(pool, aid)

        def camp(a):
            return "ATK" if a.startswith("ATK_") else cd.CAMP.get(a, "?")
        fl = Counter(camp(a) for a in flagged)
        unfl = Counter(camp(a) for a, _ in pool if a not in flagged)
        atk_ext = st.mean(extremity(pool_d[a]) for a in flagged if a.startswith("ATK_"))
        lab_in = [a for a in flagged if camp(a) == "lab"]
        lab_ext = st.mean(extremity(pool_d[a]) for a in lab_in) if lab_in else float("nan")
        print(f"sleeper f={f}: {n_a} attackers | recall {rec:.2f} precision {prec:.2f}")
        print(f"   flagged cluster:   {dict(fl)}")
        print(f"   unflagged cluster: {dict(unfl)}")
        print(f"   crux extremity |rating-2.5|: attackers {atk_ext:.2f} vs honest-lab-in-flagged "
              f"{lab_ext:.2f}  (gap = the isolating signal spectral split ignores)")
        print()
    print("Read: 100% recall = the bloc is always inside the flagged cluster. But on a camp-split")
    print("question the flagged cluster ALSO holds the honest same-side (lab) camp, so the spectral")
    print("split alone would tar honest lab-leaners as suspicious. The attackers' crux-extremity is")
    print("markedly higher than honest lab-leaners' — that coordinated-extremity signal is what")
    print("separates a manufactured bloc from honest disagreement, and is the recommended second stage.")


if __name__ == "__main__":
    main()
