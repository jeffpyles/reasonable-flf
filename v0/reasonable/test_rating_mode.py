#!/usr/bin/env python3
"""Focused tests for the blind Rating-mode read (ASSESSMENT-SPEC.md §7).

Rating mode must hide every consensus CUE (graded aggregates + comments +
rating-heat) while leaving the claim TEXT and support STRUCTURE a rater needs
to form a judgment. Run: python3 -m unittest reasonable.test_rating_mode
"""
import json
import tempfile
import unittest
from pathlib import Path

from reasonable import queries


def _graph():
    """A tiny two-node, one-edge graph with a rated aggregate, R/C scores, and
    comments on both the node and the edge (the exact leak eggs-p7 hit)."""
    node_a = {
        "id": "n001", "kind": "claim", "author": "x",
        "primary_phrasing": "p0", "primary_title": "t0",
        "agreement": {"mean": 4.05, "n": 28, "stdev": 0.87, "state": "provisional",
                      "blocs": {"b1": {"mean": 4.04, "n": 28}}, "history": [], "era": 1},
        "quality": {"R": {"mean": 3.9, "n": 10}, "C": {"mean": 4.2, "n": 10}},
        "heat": {"content": 0.03, "rating": 9.4},
        "phrasings": [{"id": "p0", "text": "Eggs are neutral for most adults.",
                       "scores": {"R": {"mean": 3.9, "n": 10}, "C": {"mean": 4.2, "n": 10},
                                  "A": {"mean": 3.0, "n": 5}}}],
        "titles": [{"id": "t0", "text": "Eggs neutral",
                    "scores": {"A": {"mean": 4.0, "n": 6}}}],
        "comments": [{"id": "c1", "author": "y", "text": "I rated this 2.5 because ...",
                      "scores": {}}],
    }
    node_b = {
        "id": "n002", "kind": "claim", "author": "x",
        "primary_phrasing": "p0", "primary_title": "t0",
        "agreement": {"mean": 2.0, "n": 12, "stdev": 1.0, "state": "provisional",
                      "blocs": {}, "history": [], "era": 1},
        "quality": {"R": {"mean": None, "n": 0}, "C": {"mean": None, "n": 0}},
        "heat": {"content": 0.0, "rating": 1.0},
        "phrasings": [{"id": "p0", "text": "Eggs raise CVD risk.", "scores": {}}],
        "titles": [], "comments": [],
    }
    edge = {
        "id": "e001", "from": "n002", "to": "n001", "group": None, "strength": 3,
        "agreement": {"mean": 2.5, "n": 8, "stdev": 0.5, "state": "provisional",
                      "blocs": {}, "history": [], "era": 1},
        "heat": {"content": 0.0, "rating": 4.0},
        "primary_typing": None,
        "comments": [{"id": "c2", "author": "z", "text": "I rated this edge at 2.5 ...",
                      "scores": {}}],
    }
    return {"nodes": [node_a, node_b], "ground_edges": [edge], "antithesis_sets": []}


class RatingModeTest(unittest.TestCase):
    def test_normal_mode_shows_cues(self):
        rec = queries.get_node(_graph(), "n001")           # rating_mode defaults False
        n = rec["node"]
        self.assertFalse(rec["rating_mode"])
        self.assertEqual(n["agreement"]["mean"], 4.05)
        self.assertEqual(n["quality"]["R"]["mean"], 3.9)
        self.assertEqual(n["comment_count"], 1)
        self.assertEqual(len(n["comments"]), 1)
        # n002 -> n001 is a GROUND of n001 (support flows into n001)
        self.assertEqual(rec["grounds"][0]["agreement"]["mean"], 2.5)
        self.assertEqual(len(rec["grounds"][0]["comments"]), 1)

    def test_rating_mode_hides_every_aggregate(self):
        rec = queries.get_node(_graph(), "n001", rating_mode=True)
        n = rec["node"]
        self.assertTrue(rec["rating_mode"])
        self.assertIsNone(n["agreement"]["mean"])
        self.assertTrue(n["agreement"]["hidden"])
        self.assertIsNone(n["quality"]["R"]["mean"])
        self.assertIsNone(n["quality"]["C"]["mean"])
        # phrasing and title scores (R/C/A) all blinded
        for dim in ("R", "C", "A"):
            self.assertIsNone(n["phrasings"][0]["scores"][dim]["mean"])
        self.assertIsNone(n["titles"][0]["scores"]["A"]["mean"])
        self.assertIsNone(n["heat"])

    def test_rating_mode_hides_comments(self):
        rec = queries.get_node(_graph(), "n001", rating_mode=True)
        self.assertEqual(rec["node"]["comment_count"], 0)
        self.assertEqual(rec["node"]["comments"], [])
        # the edge-borne comment (the eggs-p7 leak) is gone too
        grd = rec["grounds"][0]
        self.assertEqual(grd["comments"], [])
        self.assertEqual(grd["comment_count"], 0)
        self.assertIsNone(grd["agreement"]["mean"])

    def test_rating_mode_keeps_text_and_structure(self):
        rec = queries.get_node(_graph(), "n001", rating_mode=True)
        n = rec["node"]
        # the claim itself and its wording are still readable
        self.assertEqual(n["phrasings"][0]["text"], "Eggs are neutral for most adults.")
        self.assertEqual(n["titles"][0]["text"], "Eggs neutral")
        # support structure preserved: n002 -> n001 shows up as a ground edge
        self.assertEqual(len(rec["grounds"]), 1)
        self.assertEqual(rec["grounds"][0]["from"], "n002")
        # structural strength (v0 layer) is intentionally NOT blinded
        self.assertEqual(rec["grounds"][0]["strength"], 3)

    def test_neighborhood_rating_mode(self):
        g = _graph()
        rec = queries.neighborhood(g, "n001", depth=1, rating_mode=True)
        self.assertTrue(rec["rating_mode"])
        for sub in rec["nodes"]:
            self.assertIsNone(sub["agreement"]["mean"])
            self.assertIsNone(sub["quality"]["R"]["mean"])
            self.assertEqual(sub["comment_count"], 0)
        # normal mode still reveals them
        rec2 = queries.neighborhood(g, "n001", depth=1)
        means = [s["agreement"]["mean"] for s in rec2["nodes"]]
        self.assertIn(4.05, means)


class EnforcementConfigTest(unittest.TestCase):
    """The dataset-level switch that imposes Rating mode with no CLI opt-out
    (ASSESSMENT-SPEC §7 v1.5)."""

    def _dir_with_config(self, cfg):
        d = Path(tempfile.mkdtemp())
        (d / "config.json").write_text(json.dumps(cfg))
        return d

    def test_absent_defaults_off(self):
        self.assertFalse(queries.rating_mode_only(self._dir_with_config({})))

    def test_explicit_true(self):
        d = self._dir_with_config({"rating_mode_only": True, "phase2": {}})
        self.assertTrue(queries.rating_mode_only(d))
        self.assertTrue(queries.effective_config(d)["rating_mode_only"])

    def test_explicit_false(self):
        self.assertFalse(queries.rating_mode_only(
            self._dir_with_config({"rating_mode_only": False})))


if __name__ == "__main__":
    unittest.main()
