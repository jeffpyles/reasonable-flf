"""Tests for the corrected contested trigger (reasonable/lifecycle.py).

The trigger was raw-stdev-only; it is now STRUCTURAL contestedness (antithesis
membership) as the reliable primary signal, with stdev demoted to a conservative
secondary net (see structurally_contested() / dispersion-regimes/). These tests
pin the new behavior, which previously had no coverage.
"""
import unittest

from reasonable import lifecycle as L

CFG = {"quorum": 2, "confirm": 3, "contested_threshold": 1.0, "cold_factor": 0.5,
       "bloc_min_ratings": 3}


def make_state(ratings_by_target, sets=None):
    """Minimal fold-shaped state for block_for: era 1, one era_map per target."""
    ra = {}
    eras = {}
    for t, vals in ratings_by_target.items():
        eras[t] = 1
        ra[t] = {"A": {1: {f"r{i}": {"value": v, "bloc": None} for i, v in enumerate(vals)}}}
    return {"eras": eras, "ratings_all": ra, "sets": sets or {}, "comments": {}, "groups": {},
            "nodes": {t: {} for t in ratings_by_target}}


def block(target, state, aggregate):
    return L.block_for(target, "A", state, aggregate, content_heat={},
                       site_median_content=1.0, cfg=CFG)


class TestStructurallyContested(unittest.TestCase):
    def test_helper_picks_antithesis_members(self):
        state = {"sets": {"s1": {"members": [{"node": "n001"}, {"node": "n002"}]},
                          "s2": {"members": [{"node": "n007"}]}}}  # singleton -> not contested
        ids = L.structurally_contested(state)
        self.assertEqual(ids, {"n001", "n002"})

    def test_cached_on_state(self):
        state = {"sets": {"s1": {"members": [{"node": "n001"}, {"node": "n002"}]}}}
        L.structurally_contested(state)
        self.assertIn("_structurally_contested", state)


class TestContestedTrigger(unittest.TestCase):
    def test_antithesis_member_contested_even_when_ratings_converge(self):
        # the key new behavior: a rival claim in a live antithesis is contested
        # even though its own ratings agree (disagreement is externalized to structure).
        state = make_state({"n001": [3.0, 3.0, 3.0]},
                           sets={"s1": {"members": [{"node": "n001"}, {"node": "n002"}]}})
        b = block("n001", state, {("n001", "A"): (3.0, 3)})
        self.assertEqual(b["stdev"], 0.0)
        self.assertEqual(b["state"], "contested")

    def test_high_stdev_nonmember_still_contested(self):
        # the demoted secondary net: a non-antithesis target with very spread
        # ratings still trips contested (fails safe toward review).
        state = make_state({"n003": [0.0, 5.0, 0.0, 5.0]})
        b = block("n003", state, {("n003", "A"): (2.5, 4)})
        self.assertGreater(b["stdev"], 1.0)
        self.assertEqual(b["state"], "contested")

    def test_converged_nonmember_settles(self):
        # not structurally contested and not spread -> not contested (settles when cold).
        state = make_state({"n004": [3.0, 3.0, 3.0]})
        b = block("n004", state, {("n004", "A"): (3.0, 3)})
        self.assertEqual(b["stdev"], 0.0)
        self.assertNotEqual(b["state"], "contested")
        self.assertEqual(b["state"], "settled")


class TestHistogram(unittest.TestCase):
    def test_bins_count_ratings_rounded_half_up_and_clamped(self):
        # values -> bins: 0.4->0, 0.6->1, 2.5->3 (half up), 4.9->5, 5.0->5.
        state = make_state({"n001": [0.4, 0.6, 2.5, 4.9, 5.0]})
        b = block("n001", state, {("n001", "A"): (2.68, 5)})
        self.assertEqual(b["histogram"], [1, 1, 0, 1, 0, 2])
        self.assertEqual(sum(b["histogram"]), b["n"])

    def test_absent_when_no_ratings(self):
        state = make_state({"n002": []})
        b = block("n002", state, {("n002", "A"): (None, 0)})
        self.assertNotIn("histogram", b, "unrated blocks carry no histogram (viewer falls back to stdev)")

    def test_abstains_do_not_bin(self):
        state = make_state({"n003": [3.0, "abstain", 3.0]})
        b = block("n003", state, {("n003", "A"): (3.0, 2)})
        self.assertEqual(b["histogram"], [0, 0, 0, 2, 0, 0])


if __name__ == "__main__":
    unittest.main()
