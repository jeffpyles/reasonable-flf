"""Tests for the Ought endorsement treatment (assess.py).

SPEC-evidence-argument-ought-ghosts §2.1: Ought nodes are rated on ENDORSEMENT (a
value), so (a) their Agreement aggregate is DEMOCRATIC (unweighted -- never
truth/reputation-weighted), and (b) their ratings do not feed truth-reputation.
"""
import unittest

from reasonable import assess, fold


def ev(seq, agent, verb, payload):
    return {"seq": seq, "ts": f"2026-01-01T00:00:{seq:02d}+00:00",
            "agent": agent, "verb": verb, "payload": payload}


def node(seq, agent, nid, kind, text):
    return ev(seq, agent, "create_node",
              {"id": nid, "kind": kind, "text": text, "source": None, "title": None})


def rate(seq, agent, target, value, dim="A"):
    return ev(seq, agent, "rate", {"target": target, "dim": dim, "value": value})


class TestOughtDemocratic(unittest.TestCase):
    def test_ought_aggregate_is_unweighted_while_claim_is_reputation_weighted(self):
        # Give "hi" high reputation (authors a phrasing rated R=5) and "lo" low
        # (authored phrasing rated R=0). Both rate a claim and an Ought [5, 1].
        events = [
            node(1, "hi", "n001", "claim", "a claim hi authored"),
            node(2, "lo", "n004", "claim", "a claim lo authored"),
            rate(3, "judge", "phrasing:n001:p0", 5.0, dim="R"),   # hi -> high auth
            rate(4, "judge", "phrasing:n004:p0", 0.0, dim="R"),   # lo -> low auth
            node(5, "x", "n002", "claim", "a neutral claim to rate"),
            node(6, "x", "n003", "ought", "you should do the thing"),
            rate(7, "hi", "n002", 5.0), rate(8, "lo", "n002", 1.0),   # claim
            rate(9, "hi", "n003", 5.0), rate(10, "lo", "n003", 1.0),  # ought
        ]
        out = assess.compute(fold.fold(events))
        tr = out["true_r"]
        agg = {t: m for (t, d), (m, n) in out["aggregate"].items() if d == "A"}
        self.assertGreater(tr["hi"], tr["lo"], "fixture must create a real reputation gap")
        # Ought: exactly the unweighted mean of [5, 1] = 3.0, ignoring the gap.
        self.assertAlmostEqual(agg["n003"], 3.0, places=6)
        # Claim: True_R-weighted toward the higher-rep rater -> strictly above 3.0.
        self.assertGreater(agg["n002"], 3.0)

    def test_ought_endorsements_do_not_affect_truth_reputation(self):
        base = [
            node(1, "x", "n001", "claim", "a claim"),
            node(2, "x", "n002", "ought", "you should do it"),
            rate(3, "r", "n001", 3.0), rate(4, "s", "n001", 3.0),   # r aligns on the claim
        ]
        without = assess.compute(fold.fold(base))["true_r"]["r"]
        # r ALSO casts a wild Ought endorsement -- must not change r's truth-reputation.
        with_ought = assess.compute(fold.fold(base + [rate(5, "r", "n002", 5.0)]))["true_r"]["r"]
        self.assertAlmostEqual(without, with_ought, places=9,
                               msg="an Ought endorsement must not move the rater's True_R")


if __name__ == "__main__":
    unittest.main()
