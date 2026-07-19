#!/usr/bin/env python3
"""E8 — Does the flywheel work at SITE scale: sparse ratings, most users never
touching an anchor?

The eggs runs are dense (20-60 raters saturating 79 items). A real deployment
is the opposite: millions of items, each user rates a few dozen, each item has
a handful of raters, and only a small minority of users ever rate an anchor
item. Reputation must then PROPAGATE: anchors calibrate the users who touched
them -> those users' weighted consensus fixes ordinary items -> tracking that
fixed consensus scores users who never saw an anchor (one more hop, and so on).
Whether that chain survives sparsity is THE architecture question for scale,
and no dense dataset can answer it.

Synthetic world calibrated to the eggs measurements:
  items:  frac_contested carry a shared directional bias target (like p6's
          cholesterol cluster); anchors sit INSIDE the contested set (the p6
          placement lesson).
  users:  evidence-trackers (12%, corr~0.9), blunt crowd (gain 0.7 + noise,
          like p5's 0.87-mean crowd), hawks (share the bias on contested
          items, like p6's 16). Hawk share is the stress knob; default 55% --
          a biased local majority on contested items.
  assignment: uniform random k items/user (sortition), optionally with a
          routed probe slice (a fraction of each user's budget spent on
          anchor/probe items -- the E3/E5 entrance-exam design).

Mechanism (two-hop, no oracle beyond the anchors):
  hop 0: flat consensus.
  hop 1: users with >=3 anchor ratings get anchor-agreement scores; weighted
         consensus with those scores (others at prior), gamma-concentrated.
  hop 2: every user scored by disc-vs-hop-1-consensus (shrunk by n/(n+K),
         K=20 per E2), blended with anchor score where available; final
         consensus with gamma.
Measured: consensus~truth on contested NON-anchor items (the held-out test),
reputation~competence for anchor-exposed vs non-exposed users separately (the
propagation test), at several sparsity levels x routing fractions.
"""
import math
import random
import statistics as st
from collections import defaultdict
from common import pearson, spearman, mean

RNG = random.Random(20260710)

N_USERS = 1200
N_ITEMS = 2400
FRAC_CONTESTED = 0.25
N_ANCHORS = 30
CENTER = 2.75
K_SHRINK = 20.0
PRIOR = 0.15
GAMMA = 4.0


def build_world(hawk_share=0.55):
    items = []
    for i in range(N_ITEMS):
        q = RNG.uniform(0.3, 4.7)
        contested = i < N_ITEMS * FRAC_CONTESTED
        # shared bias target on contested items: hawks see danger everywhere
        # (low agreement with pro-safety claims, high with alarm claims):
        # model as a pull toward (5 - q) -- an ordering inversion, p6-style.
        b = (5.0 - q) if contested else q
        items.append({"q": q, "b": b, "contested": contested})
    anchors = list(range(0, int(N_ITEMS * FRAC_CONTESTED)))[:N_ANCHORS]  # contested anchors
    users = []
    for u in range(N_USERS):
        r = RNG.random()
        if r < 0.12:
            users.append({"type": "expert", "gain": 1.0, "noise": 0.5, "bias_w": 0.0})
        elif r < 0.12 + (1 - 0.12) * (1 - hawk_share):
            users.append({"type": "crowd", "gain": 0.7, "noise": 0.8, "bias_w": 0.0})
        else:
            users.append({"type": "hawk", "gain": 0.8, "noise": 0.7, "bias_w": 0.85})
    return items, anchors, users


def rate(user, item):
    perceived = (1 - user["bias_w"]) * item["q"] + user["bias_w"] * item["b"] \
        if item["contested"] else item["q"]
    v = CENTER + user["gain"] * (perceived - CENTER) + RNG.gauss(0, user["noise"])
    return max(0.0, min(5.0, v))


def simulate(items, anchors, users, k_per_user, route_frac):
    """Returns ratings[item] = {user: value}."""
    anchor_set = set(anchors)
    ratings = defaultdict(dict)
    n_route = int(k_per_user * route_frac)
    for uid, u in enumerate(users):
        routed = RNG.sample(anchors, min(n_route, len(anchors)))
        rest = RNG.sample(range(N_ITEMS), k_per_user)  # may overlap; fine
        chosen = list(dict.fromkeys(routed + rest))[:k_per_user]
        for i in chosen:
            ratings[i][uid] = rate(u, items[i])
    return ratings


def weighted_consensus(ratings, w, gamma=GAMMA):
    cons = {}
    for i, cell in ratings.items():
        num = den = 0.0
        for uid, v in cell.items():
            wa = w.get(uid, PRIOR) ** gamma
            num += wa * v; den += wa
        cons[i] = num / den if den else st.mean(cell.values())
    return cons


def run_mechanism(items, anchors, users, ratings):
    anchor_set = set(anchors)
    truth = {i: items[i]["q"] for i in range(N_ITEMS)}
    by_user = defaultdict(dict)
    for i, cell in ratings.items():
        for uid, v in cell.items():
            by_user[uid][i] = v

    # hop 1: anchor-agreement scores where >=3 anchor ratings
    anchor_score = {}
    for uid, sub in by_user.items():
        pts = [abs(sub[i] - truth[i]) / 5 for i in sub if i in anchor_set]
        if len(pts) >= 3:
            anchor_score[uid] = 1 - mean(pts)
    w1 = {}
    for uid in by_user:
        if uid in anchor_score:
            n = sum(1 for i in by_user[uid] if i in anchor_set)
            conf = n / (n + 5.0)
            w1[uid] = PRIOR + conf * (anchor_score[uid] - PRIOR)
        else:
            w1[uid] = PRIOR
    cons1 = weighted_consensus(ratings, w1)

    # hop 2: disc vs cons1, shrunk; blend with anchor score where available
    w2 = {}
    for uid, sub in by_user.items():
        pts = [(v, cons1[i]) for i, v in sub.items() if i in cons1]
        d = pearson([p[0] for p in pts], [p[1] for p in pts]) if len(pts) >= 5 else 0.0
        d = max(0.0, d)
        conf = len(pts) / (len(pts) + K_SHRINK)
        disc_part = PRIOR + conf * (d - PRIOR)
        if uid in anchor_score:
            w2[uid] = 0.6 * (PRIOR + (sum(1 for i in sub if i in anchor_set) /
                                      (sum(1 for i in sub if i in anchor_set) + 5.0)) *
                             (anchor_score[uid] - PRIOR)) + 0.4 * disc_part
        else:
            w2[uid] = disc_part
    cons2 = weighted_consensus(ratings, w2)
    return w1, w2, cons1, cons2, anchor_score


def eval_world(items, anchors, users, ratings, w2, cons_by_hop):
    anchor_set = set(anchors)
    truth = {i: items[i]["q"] for i in range(N_ITEMS)}
    contested_eval = [i for i in ratings
                     if items[i]["contested"] and i not in anchor_set]
    normal_eval = [i for i in ratings if not items[i]["contested"]]

    # true competence per user (corr of ratings with truth) -- for evaluation only
    by_user = defaultdict(dict)
    for i, cell in ratings.items():
        for uid, v in cell.items():
            by_user[uid][i] = v
    comp = {}
    for uid, sub in by_user.items():
        if len(sub) >= 8:
            comp[uid] = pearson([v for v in sub.values()], [truth[i] for i in sub])

    out = {}
    for hop, cons in cons_by_hop.items():
        keys = [i for i in contested_eval if i in cons and len(ratings[i]) >= 2]
        out[f"contested_corr_{hop}"] = pearson([cons[i] for i in keys],
                                               [truth[i] for i in keys])
        keysn = [i for i in normal_eval if i in cons and len(ratings[i]) >= 2]
        out[f"normal_corr_{hop}"] = pearson([cons[i] for i in keysn],
                                            [truth[i] for i in keysn])
    exposed = {uid for uid, sub in by_user.items()
               if sum(1 for i in sub if i in anchor_set) >= 3}
    for grp, uids in (("exposed", [u for u in comp if u in exposed]),
                      ("unexposed", [u for u in comp if u not in exposed])):
        if len(uids) >= 20:
            out[f"rep~comp_{grp}"] = spearman([w2[u] for u in uids],
                                              [comp[u] for u in uids])
            out[f"n_{grp}"] = len(uids)
    return out


print(f"world: {N_USERS} users x {N_ITEMS} items, {FRAC_CONTESTED:.0%} contested, "
      f"{N_ANCHORS} contested anchors, hawks 55% (biased local majority), gamma={GAMMA}")
print(f"\n{'k/user':>6} {'route':>6} {'raters/item':>11} {'%exposed':>9} "
      f"{'contested flat->h1->h2':>24} {'normal h2':>10} {'rep~comp exp/unexp':>19}")
for k_per_user in (10, 20, 40):
    for route_frac in (0.0, 0.2):
        RNG.seed(1000 + k_per_user * 10 + int(route_frac * 10))
        items, anchors, users = build_world()
        ratings = simulate(items, anchors, users, k_per_user, route_frac)
        w1, w2, cons1, cons2, ascore = run_mechanism(items, anchors, users, ratings)
        flat = {i: st.mean(c.values()) for i, c in ratings.items()}
        res = eval_world(items, anchors, users, ratings, w2,
                         {"flat": flat, "h1": cons1, "h2": cons2})
        rpi = mean([len(c) for c in ratings.values()])
        exposed_frac = res.get("n_exposed", 0) / max(
            1, res.get("n_exposed", 0) + res.get("n_unexposed", 0))
        print(f"{k_per_user:>6} {route_frac:>6.1f} {rpi:>11.1f} {exposed_frac:>9.2f} "
              f"{res['contested_corr_flat']:>8.2f} {res['contested_corr_h1']:>7.2f} "
              f"{res['contested_corr_h2']:>7.2f} {res['normal_corr_h2']:>10.2f} "
              f"{res.get('rep~comp_exposed', float('nan')):>9.2f}/"
              f"{res.get('rep~comp_unexposed', float('nan')):<8.2f}")

print("""
Reading: 'contested flat' is the biased baseline; h1 = anchors fix the exposed
users' consensus; h2 = disc-vs-fixed-consensus propagates to unexposed users.
The propagation claim holds if (a) h2 > h1 > flat on contested items, and
(b) rep~comp for UNEXPOSED users is well above zero -- reputation reaching
users the anchors never touched. route=0.2 spends 20% of each user's budget on
anchor items (entrance-exam routing); compare %exposed and h2 against route=0.
""")
