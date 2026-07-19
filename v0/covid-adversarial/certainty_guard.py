#!/usr/bin/env python3
"""Verdict-certainty guardrail (ROADMAP-NEXT-VERSION Tier-1 #1).

The covid mirror run found an attack calibration can't stop and MAE can't see: a
sleeper bloc pushing toward the *existing* consensus can't flip the verdict, so it
manufactures false CERTAINTY instead — hardening a genuinely-live question past what
the evidence warrants and burying the legitimate minority. Distance-to-oracle MAE
misses it because pushing toward the consensus keeps the cruxes NEAR the oracle values
even as the top verdict overshoots.

This guardrail measures the right thing: how much MORE DECISIVE the aggregate is than
the reference (oracle) warrants. It has two signals, and fires if either trips:

  1. VERDICT signal (primary, sensitive): compare the top answers' lead margin to the
     oracle's warranted margin.
       - wrong leader (a FLIP) with a real margin  -> fire (caught as soon as the lead crosses)
       - same leader but margin > oracle margin + tol  -> over-certainty (hardening past warrant)
  2. FRONTIER signal (corroborating): the mean, over the contested cruxes, of how much
     further from the midpoint the aggregate sits than the oracle warrants.

Runtime inputs are exactly what the system already has — the aggregate consensus and the
oracle reference (mean + spread) on the contested nodes, the same reference calibration
relies on. It needs no knowledge of who the attackers are.

LIMITATION: this detects hardening BEYOND THE REFERENCE, so it is only as good as the
oracle — it flags manufactured over-certainty relative to the best available reference,
not ground-truth over-confidence. Pairs with denser/rotating anchors and the extremity
detector, not a standalone truth oracle.
"""


def decisiveness(x):
    return abs(x - 2.5)


def verdict_certainty(cons, oracle_mean, verdict_nodes, tol=0.15):
    """Over-certainty on the top answers. Returns (score>=0, is_flip).
    Fires (score>0) on a flipped leader with real margin, or a lead margin wider than
    the oracle warrants by more than tol."""
    cv = {n: cons[n] for n in verdict_nodes if n in cons}
    ov = {n: oracle_mean[n] for n in verdict_nodes if n in oracle_mean}
    if len(cv) < 2 or len(ov) < 2:
        return 0.0, False
    lead_c = max(cv, key=cv.get)
    lead_o = max(ov, key=ov.get)
    margin_c = max(cv.values()) - min(cv.values())
    margin_o = max(ov.values()) - min(ov.values())
    if lead_c != lead_o and margin_c > tol:
        return round(margin_c + margin_o, 3), True          # wrong leader with a real margin
    return round(max(0.0, margin_c - margin_o - tol), 3), False


def frontier_over_certainty(cons, oracle_mean, oracle_sds, nodes, tol_floor=0.2):
    """Mean per-node unwarranted decisiveness over the contested frontier: how much
    further from the midpoint the aggregate sits than the oracle warrants."""
    per = {}
    for n in nodes:
        if n in cons and n in oracle_mean:
            tol = tol_floor + oracle_sds.get(n, 0.0)
            per[n] = max(0.0, decisiveness(cons[n]) - decisiveness(oracle_mean[n]) - tol)
    total = sum(per.values())
    mean = total / len(per) if per else 0.0
    worst = max(per.items(), key=lambda kv: kv[1]) if per else (None, 0.0)
    return {"per_node": per, "mean": round(mean, 3), "worst": (worst[0], round(worst[1], 3))}


def guard(cons, oracle_mean, oracle_sds, verdict_nodes, frontier_nodes,
          verdict_tol=0.15, frontier_tol_floor=0.2, verdict_thresh=0.1, frontier_thresh=0.2):
    """Full guardrail. Fires if the verdict signal OR the frontier signal trips."""
    v_score, is_flip = verdict_certainty(cons, oracle_mean, verdict_nodes, verdict_tol)
    f = frontier_over_certainty(cons, oracle_mean, oracle_sds, frontier_nodes, frontier_tol_floor)
    fired = (v_score > verdict_thresh) or (f["mean"] > frontier_thresh)
    reason = []
    if v_score > verdict_thresh:
        reason.append("FLIP" if is_flip else "verdict-hardening")
    if f["mean"] > frontier_thresh:
        reason.append("frontier-hardening")
    return {"fired": fired, "verdict_score": v_score, "is_flip": is_flip,
            "frontier_mean": f["mean"], "frontier_worst": f["worst"],
            "reason": "+".join(reason) or "-"}
