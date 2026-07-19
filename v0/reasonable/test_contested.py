"""Tests for the shared contestedness service (reasonable/contested.py)."""
import unittest

from reasonable import contested as C


def state(matrix, sets=None):
    return {"ratings": {n: {"A": dict(cell)} for n, cell in matrix.items()},
            "sets": sets or {}}


def agg(pairs):
    """pairs: {target: (mean, n)} on dim A -> aggregate dict."""
    return {(t, "A"): mn for t, mn in pairs.items()}


class TestContestedness(unittest.TestCase):
    def setUp(self):
        # n001/n002 are antithesis rivals; n003/n004 stand alone; converged ratings
        # (no belief camps at this size) so the STRUCTURAL signal drives.
        m = {n: {f"r{i}": 3.0 for i in range(3)} for n in ("n001", "n002", "n003", "n004")}
        self.st = state(m, sets={"s1": {"members": [{"node": "n001"}, {"node": "n002"}]}})

    def test_antithesis_member_is_contested_and_never_ghosts_even_when_low(self):
        # the minority-truth guarantee: a rival that lost its stack stays ALIVE.
        r = C.assess_contestedness(self.st, agg({"n001": (0.8, 5), "n002": (4.2, 5)}))
        self.assertEqual(r["nodes"]["n001"]["verdict"], "contested")
        self.assertTrue(r["nodes"]["n001"]["lost_rival"])          # it did lose the stack
        self.assertNotEqual(r["nodes"]["n001"]["verdict"], "ghost_eligible")

    def test_standalone_low_node_is_ghost_eligible(self):
        r = C.assess_contestedness(self.st, agg({"n003": (0.9, 6)}))
        self.assertEqual(r["nodes"]["n003"]["verdict"], "ghost_eligible")

    def test_standalone_healthy_node_is_settled(self):
        r = C.assess_contestedness(self.st, agg({"n004": (3.8, 6)}))
        self.assertEqual(r["nodes"]["n004"]["verdict"], "settled")

    def test_low_edge_ghost_eligible(self):
        r = C.assess_contestedness(self.st, agg({"e001": (0.7, 5)}))
        self.assertEqual(r["nodes"]["e001"]["verdict"], "ghost_eligible")


class TestCampContested(unittest.TestCase):
    def setUp(self):
        # two camps disagree on n001..n006, agree on n007..n012 (>= min_shared).
        m = {f"n{i:03d}": {} for i in range(1, 13)}
        for i in range(3):
            for k in range(1, 7):
                m[f"n{k:03d}"][f"a{i}"] = 4.5
                m[f"n{k:03d}"][f"b{i}"] = 0.5
            for k in range(7, 13):
                m[f"n{k:03d}"][f"a{i}"] = 3.0
                m[f"n{k:03d}"][f"b{i}"] = 3.0
        self.st = state(m)

    def test_camp_disagreed_node_is_contested_not_ghost(self):
        # n001: camps split, so mean sits mid/low -- must read contested, not ghost.
        r = C.assess_contestedness(self.st, agg({"n001": (2.5, 6), "n007": (3.0, 6)}))
        self.assertEqual(r["nodes"]["n001"]["verdict"], "contested")
        self.assertIsNotNone(r["nodes"]["n001"]["camp_gap"])
        self.assertEqual(r["nodes"]["n007"]["verdict"], "settled")
        self.assertGreater(r["between_group_fraction"], 0.5)


if __name__ == "__main__":
    unittest.main()
