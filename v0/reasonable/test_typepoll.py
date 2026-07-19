"""Tests for the categorical type-poll (typepoll.py + fold/assess wiring).

SPEC-evidence-argument-ought-ghosts §2.2: a poll opened by `flag_type` and voted by
`poll_vote` resolves REPUTATION-WEIGHTED (quorum + ratio, decline abstains); a
resolved-Ought node then gets the democratic endorsement treatment in assess.py.
Dormant (unvoted) polls emit nothing -> existing graphs stay byte-identical.
"""
import unittest

from reasonable import assess, fold, typepoll


# ---- resolver unit tests (synthetic state + True_R; no fold needed) ----------
def _state(polls, kinds=None, eras=None):
    return {"nodes": {n: {"kind": k} for n, k in (kinds or {}).items()},
            "eras": eras or {}, "polls": polls}


def _poll(node, question, votes):
    return {f"{node}|{question}": {
        "node": node, "question": question, "opened_seq": 1,
        "votes": {a: {"value": v, "seq": i + 2} for i, (a, v) in enumerate(votes.items())}}}


class TestResolver(unittest.TestCase):
    def test_resolves_yes_on_quorum_plus_supermajority(self):
        votes = {f"v{i}": "yes" for i in range(5)}
        st = _state(_poll("n001", "type:ought", votes), kinds={"n001": "claim"})
        r = typepoll.resolve_polls(st, {a: 0.5 for a in votes})["n001|type:ought"]
        self.assertTrue(r["resolved"])
        self.assertEqual(r["resolved_kind"], "ought")
        self.assertTrue(r["reopen_required"], "a claim->ought flip in era 1 needs a reopen")

    def test_below_quorum_stays_open(self):
        votes = {f"v{i}": "yes" for i in range(4)}       # 4 < quorum 5
        st = _state(_poll("n001", "type:ought", votes), kinds={"n001": "claim"})
        r = typepoll.resolve_polls(st, {a: 0.9 for a in votes})["n001|type:ought"]
        self.assertFalse(r["resolved"])

    def test_ratio_not_met_stays_open(self):
        votes = {**{f"y{i}": "yes" for i in range(3)}, **{f"n{i}": "no" for i in range(3)}}
        st = _state(_poll("n001", "type:ought", votes), kinds={"n001": "claim"})
        r = typepoll.resolve_polls(st, {a: 0.5 for a in votes})["n001|type:ought"]
        self.assertAlmostEqual(r["yes_share"], 0.5, places=6)
        self.assertFalse(r["resolved"], "a bare 50% must not clear the 2/3 ratio")

    def test_reputation_outweighs_a_low_rep_majority(self):
        # 3 high-rep Yes vs 4 low-rep No: MORE voters say No, but reputation says Yes.
        votes = {**{f"y{i}": "yes" for i in range(3)}, **{f"n{i}": "no" for i in range(4)}}
        tr = {**{f"y{i}": 0.9 for i in range(3)}, **{f"n{i}": 0.1 for i in range(4)}}
        r = typepoll.resolve_polls(_state(_poll("n001", "type:ought", votes),
                                          kinds={"n001": "claim"}), tr)["n001|type:ought"]
        self.assertGreater(r["yes_share"], 0.66)
        self.assertTrue(r["resolved"], "reputation-weighted Yes supermajority resolves it")

    def test_low_rep_majority_cannot_force_resolution(self):
        # inverse: 4 low-rep Yes vs 3 high-rep No -> must NOT resolve.
        votes = {**{f"y{i}": "yes" for i in range(4)}, **{f"n{i}": "no" for i in range(3)}}
        tr = {**{f"y{i}": 0.1 for i in range(4)}, **{f"n{i}": 0.9 for i in range(3)}}
        r = typepoll.resolve_polls(_state(_poll("n001", "type:ought", votes),
                                          kinds={"n001": "claim"}), tr)["n001|type:ought"]
        self.assertLess(r["yes_share"], 0.66)
        self.assertFalse(r["resolved"])

    def test_decline_abstains_from_the_ratio(self):
        votes = {**{f"y{i}": "yes" for i in range(5)}, **{f"d{i}": "decline" for i in range(3)}}
        r = typepoll.resolve_polls(_state(_poll("n001", "type:ought", votes),
                                          kinds={"n001": "claim"}), {a: 0.5 for a in votes})["n001|type:ought"]
        self.assertEqual((r["n_votes"], r["decline"]), (5, 3))
        self.assertTrue(r["resolved"], "decline is recorded but does not dilute the Yes-share")

    def test_already_ought_in_bumped_era_needs_no_reopen(self):
        votes = {f"v{i}": "yes" for i in range(5)}
        st = _state(_poll("n001", "type:ought", votes), kinds={"n001": "ought"}, eras={"n001": 2})
        r = typepoll.resolve_polls(st, {a: 0.5 for a in votes})["n001|type:ought"]
        self.assertTrue(r["resolved"])
        self.assertFalse(r["reopen_required"])


# ---- integration: fold + assess wiring --------------------------------------
def ev(seq, agent, verb, payload):
    return {"seq": seq, "ts": f"2026-01-01T00:00:{seq:02d}+00:00",
            "agent": agent, "verb": verb, "payload": payload}


def node(seq, agent, nid, kind, text):
    return ev(seq, agent, "create_node",
              {"id": nid, "kind": kind, "text": text, "source": None, "title": None})


def rate(seq, agent, target, value, dim="A"):
    return ev(seq, agent, "rate", {"target": target, "dim": dim, "value": value})


class TestPollWiring(unittest.TestCase):
    def test_dormant_flag_emits_no_poll_surface_but_a_vote_does(self):
        base = [node(1, "a", "n001", "claim", "a claim"),
                ev(2, "b", "flag_type", {"id": "ft1", "node": "n001", "as": "ought"})]
        gj = fold.to_graph_json(fold.fold(base))
        self.assertNotIn("polls", gj, "a dormant (unvoted) flag must add no graph surface")
        voted = base + [ev(3, "b", "poll_vote",
                           {"node": "n001", "question": "type:ought", "value": "yes"})]
        gj2 = fold.to_graph_json(fold.fold(voted))
        self.assertIn("polls", gj2)
        self.assertEqual(gj2["polls"][0]["node"], "n001")

    def test_poll_resolution_flips_node_to_democratic_ought_treatment(self):
        # Reputation gap: "hi" authors a phrasing rated R=5, "lo" one rated R=0.
        # n001 is a claim; a 5-voter Yes poll re-types it to Ought. Then hi & lo
        # rate n001 [5, 1]: as a resolved Ought it aggregates DEMOCRATICALLY (3.0),
        # while the control claim n002 with the same two raters is rep-weighted > 3.
        events = [
            node(1, "hi", "n001", "claim", "the node under a type poll"),
            node(2, "lo", "n004", "claim", "a claim lo authored"),
            rate(3, "judge", "phrasing:n001:p0", 5.0, dim="R"),   # hi -> high auth
            rate(4, "judge", "phrasing:n004:p0", 0.0, dim="R"),   # lo -> low auth
            node(5, "x", "n002", "claim", "a control claim"),
            ev(6, "flagger", "flag_type", {"id": "ft1", "node": "n001", "as": "ought"}),
        ]
        seq = 7
        for i in range(5):                                        # 5 Yes votes -> resolves
            events.append(ev(seq, f"voter{i}", "poll_vote",
                             {"node": "n001", "question": "type:ought", "value": "yes"}))
            seq += 1
        events += [rate(seq, "hi", "n001", 5.0), rate(seq + 1, "lo", "n001", 1.0),
                   rate(seq + 2, "hi", "n002", 5.0), rate(seq + 3, "lo", "n002", 1.0)]

        out = assess.compute(fold.fold(events))
        self.assertTrue(out["polls"]["n001|type:ought"]["resolved"])
        self.assertEqual(out["polls"]["n001|type:ought"]["resolved_kind"], "ought")
        agg = {t: m for (t, d), (m, n) in out["aggregate"].items() if d == "A"}
        self.assertAlmostEqual(agg["n001"], 3.0, places=6,
                               msg="a poll-resolved Ought aggregates democratically")
        self.assertGreater(agg["n002"], 3.0,
                           "the un-flagged control claim stays reputation-weighted")


if __name__ == "__main__":
    unittest.main()
