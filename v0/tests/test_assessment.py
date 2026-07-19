"""Tests for ASSESSMENT-SPEC.md: the `rate` verb, reputation (True_R), the
weighted-aggregation fixed-point loop, and the `reputation`/`show-config`
read verbs. Additive to the frozen v0 core -- mirrors the layering of
test_forums.py (fold-level, validate-level, ops/CLI-level, determinism)
rather than one monolithic test file. v0's `agree`/`strength` structural
consensus is untouched by any of this (see test_fold.py/test_validate.py,
still green): this file only exercises the new, parallel graded layer.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reasonable import assess, ops, queries, validate  # noqa: E402
from reasonable.fold import fold, to_graph_json  # noqa: E402

V0_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
GRAPH_PY = V0_DIR / "graph.py"


def ev(seq, agent, verb, payload):
    return {"seq": seq, "ts": f"2026-01-01T00:00:{seq:02d}+00:00", "agent": agent, "verb": verb, "payload": payload}


def run(data_dir, *args):
    cmd = [sys.executable, str(GRAPH_PY), *args, "--data", str(data_dir), "--json"]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(V0_DIR))


class TempDirMixin:
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# fold-level: rate shape, supersede semantics, scores/agreement projection
# ---------------------------------------------------------------------------

class FoldAssessmentTest(unittest.TestCase):
    def test_rate_phrasing_appears_in_scores(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a2", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": 4.0}),
        ]
        gj = to_graph_json(fold(events))
        scores = gj["nodes"][0]["phrasings"][0]["scores"]
        self.assertEqual(scores["R"]["n"], 1)
        self.assertAlmostEqual(scores["R"]["mean"], 4.0)
        self.assertEqual(scores["C"]["n"], 0)
        self.assertIsNone(scores["C"]["mean"])

    def test_rate_node_appears_in_agreement(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a2", "rate", {"target": "n001", "dim": "A", "value": 3.5}),
        ]
        gj = to_graph_json(fold(events))
        node = gj["nodes"][0]
        self.assertEqual(node["agreement"]["n"], 1)
        self.assertAlmostEqual(node["agreement"]["mean"], 3.5)

    def test_rate_comment_appears_in_scores(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a2", "comment", {"id": "c001", "target": "n001", "parent": None, "text": "hi"}),
            ev(3, "a3", "rate", {"target": "comment:c001", "dim": "C", "value": 2.0}),
        ]
        gj = to_graph_json(fold(events))
        c = gj["nodes"][0]["comments"][0]
        self.assertEqual(c["scores"]["C"]["n"], 1)
        self.assertAlmostEqual(c["scores"]["C"]["mean"], 2.0)

    def test_re_rate_supersedes_earlier_value(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a2", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": 1.0}),
            ev(3, "a2", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": 5.0}),
        ]
        gj = to_graph_json(fold(events))
        scores = gj["nodes"][0]["phrasings"][0]["scores"]
        self.assertEqual(scores["R"]["n"], 1, "re-rate must supersede, not accumulate a second rater")
        self.assertAlmostEqual(scores["R"]["mean"], 5.0)

    def test_abstain_supersedes_and_removes_prior_value(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a2", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": 4.0}),
            ev(3, "a3", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": 2.0}),
            ev(4, "a2", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": "abstain"}),
        ]
        gj = to_graph_json(fold(events))
        scores = gj["nodes"][0]["phrasings"][0]["scores"]
        self.assertEqual(scores["R"]["n"], 1, "abstain must remove a2's earlier vote from the count")
        self.assertAlmostEqual(scores["R"]["mean"], 2.0, msg="only a3's 2.0 should remain")

    def test_node_quality_inherits_top_phrasing_and_changes_when_it_flips(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "propose_phrasing", {"id": "p1", "node": "n001", "text": "A, better said"}),
            ev(3, "a2", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": 1.0}),
            ev(4, "a2", "rate", {"target": "phrasing:n001:p0", "dim": "C", "value": 1.0}),
            ev(5, "a3", "rate", {"target": "phrasing:n001:p1", "dim": "R", "value": 5.0}),
            ev(6, "a3", "rate", {"target": "phrasing:n001:p1", "dim": "C", "value": 5.0}),
        ]
        gj = to_graph_json(fold(events))
        node = gj["nodes"][0]
        self.assertEqual(node["primary_phrasing"], "p1", "the higher-rated phrasing should win primary, "
                                                          "not the older p0 -- nobody rated the node itself")
        self.assertAlmostEqual(node["quality"]["R"]["mean"], 5.0)
        self.assertAlmostEqual(node["quality"]["C"]["mean"], 5.0)

    def test_never_rated_graph_primary_phrasing_matches_old_agrees_only_behavior(self):
        # No `rate` events at all: primary_phrasing selection must degrade to
        # EXACTLY the old agrees-based algorithm (BUILD-SPEC.md's frozen
        # `_pick_primary`), so every pre-assessment graph.json rebuilds
        # byte-identically in shape/semantics, just with extra (all-null)
        # fields tacked on.
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "propose_phrasing", {"id": "p1", "node": "n001", "text": "A, restated"}),
            ev(3, "a2", "agree", {"target": "phrasing:n001:p1"}),
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(gj["nodes"][0]["primary_phrasing"], "p1")  # p1 has 1 agree, p0 has 0

    def test_meta_gains_rating_count_and_config(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a2", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": 4.0}),
            ev(3, "a3", "rate", {"target": "n001", "dim": "A", "value": 2.0}),
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(gj["meta"]["rating_count"], 2)
        self.assertIn("assessment" if False else "reputation", gj["meta"]["config"])
        self.assertEqual(gj["meta"]["config"]["reputation"]["prior"], 0.15)

    def test_accounts_present_for_every_acting_agent_sorted_by_id(self):
        events = [
            ev(1, "a2", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": 4.0}),
        ]
        gj = to_graph_json(fold(events))
        agents = [a["agent"] for a in gj["accounts"]]
        self.assertEqual(agents, sorted(agents))
        self.assertEqual(set(agents), {"a1", "a2"})


# ---------------------------------------------------------------------------
# fold-level: graded EDGE Agreement (ASSESSMENT-SPEC.md Amendments -- edges
# now also accept a graded `rate --dim A`, parallel to the untouched
# structural agrees/strength consensus).
# ---------------------------------------------------------------------------

class FoldEdgeAgreementTest(unittest.TestCase):
    def _edge_events(self, *rate_events):
        return [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "ground",
                                         "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "dependent",
                                         "source": None, "title": None}),
            ev(3, "a1", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            *rate_events,
        ]

    def test_rate_edge_appears_in_agreement(self):
        events = self._edge_events(ev(4, "a2", "rate", {"target": "e001", "dim": "A", "value": 3.2}))
        gj = to_graph_json(fold(events))
        edge = gj["ground_edges"][0]
        self.assertEqual(edge["agreement"]["n"], 1)
        self.assertAlmostEqual(edge["agreement"]["mean"], 3.2)
        # the old structural fields are untouched by a graded rating
        self.assertEqual(edge["agrees"], 0)
        self.assertEqual(edge["strength"], 1)

    def test_edge_with_no_ratings_has_null_agreement(self):
        gj = to_graph_json(fold(self._edge_events()))
        edge = gj["ground_edges"][0]
        self.assertIsNone(edge["agreement"]["mean"])
        self.assertEqual(edge["agreement"]["n"], 0)

    def test_edge_re_rate_supersedes(self):
        events = self._edge_events(
            ev(4, "a2", "rate", {"target": "e001", "dim": "A", "value": 1.0}),
            ev(5, "a2", "rate", {"target": "e001", "dim": "A", "value": 5.0}),
        )
        gj = to_graph_json(fold(events))
        edge = gj["ground_edges"][0]
        self.assertEqual(edge["agreement"]["n"], 1, "re-rate must supersede, not accumulate a second rater")
        self.assertAlmostEqual(edge["agreement"]["mean"], 5.0)

    def test_edge_abstain_supersedes_and_removes_prior_value(self):
        events = self._edge_events(
            ev(4, "a2", "rate", {"target": "e001", "dim": "A", "value": 4.0}),
            ev(5, "a3", "rate", {"target": "e001", "dim": "A", "value": 2.0}),
            ev(6, "a2", "rate", {"target": "e001", "dim": "A", "value": "abstain"}),
        )
        gj = to_graph_json(fold(events))
        edge = gj["ground_edges"][0]
        self.assertEqual(edge["agreement"]["n"], 1, "abstain must remove a2's earlier vote from the count")
        self.assertAlmostEqual(edge["agreement"]["mean"], 2.0, msg="only a3's 2.0 should remain")

    def test_edge_author_gains_reputation_credit_from_edge_ratings(self):
        # ASSESSMENT-SPEC.md Amendments: "an edge's rater's alignment / an
        # edge's author's received-ratings both feed reputation the same way
        # node/phrasing ratings already did." Six independent raters give
        # a1 (the edge's author) real evidence about a1's edge, so a1's
        # n_assessments (confidence's evidence count) must be > 0.
        events = self._edge_events(*[
            ev(3 + i, f"r{i}", "rate", {"target": "e001", "dim": "A", "value": 4.0})
            for i in range(1, 7)
        ])
        gj = to_graph_json(fold(events))
        accounts = {a["agent"]: a for a in gj["accounts"]}
        self.assertGreater(accounts["a1"]["n_assessments"], 0)


# ---------------------------------------------------------------------------
# validate-level: self-rate, dim/target mismatch, value range, abstain
# ---------------------------------------------------------------------------

class ValidateAssessmentTest(unittest.TestCase):
    def _state(self):
        events = [
            ev(1, "agent-01", "create_node", {"id": "n001", "kind": "claim", "text": "claim one",
                                                "source": None, "title": None}),
            ev(2, "agent-02", "comment", {"id": "c001", "target": "n001", "parent": None, "text": "hi"}),
        ]
        return fold(events)

    def test_self_rate_on_own_phrasing_rejected(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-01", "phrasing:n001:p0", "R", 3.0)
        self.assertTrue(any(t == "self_rate" for t, _ in errors))

    def test_self_rate_on_own_node_rejected(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-01", "n001", "A", 3.0)
        self.assertTrue(any(t == "self_rate" for t, _ in errors))

    def test_self_rate_on_own_comment_rejected(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-02", "comment:c001", "R", 3.0)
        self.assertTrue(any(t == "self_rate" for t, _ in errors))

    def test_rate_by_other_agent_ok(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-03", "phrasing:n001:p0", "R", 3.0)
        self.assertEqual(errors, [])

    def test_dim_a_invalid_for_phrasing(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-03", "phrasing:n001:p0", "A", 3.0)
        self.assertTrue(any(t == "invalid_dim" for t, _ in errors))

    def test_dim_r_invalid_for_bare_node(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-03", "n001", "R", 3.0)
        self.assertTrue(any(t == "invalid_dim" for t, _ in errors))

    def test_value_above_scale_max_rejected(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-03", "phrasing:n001:p0", "R", 5.1)
        self.assertTrue(any(t == "value_range" for t, _ in errors))

    def test_value_below_zero_rejected(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-03", "phrasing:n001:p0", "R", -0.1)
        self.assertTrue(any(t == "value_range" for t, _ in errors))

    def test_abstain_value_ok(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-03", "phrasing:n001:p0", "R", "abstain")
        self.assertEqual(errors, [])

    def test_bad_string_value_rejected(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-03", "phrasing:n001:p0", "R", "not-a-number")
        self.assertTrue(any(t == "invalid_value" for t, _ in errors))

    def test_unknown_target_rejected(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-03", "phrasing:n001:p9", "R", 3.0)
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))

    def test_configurable_scale_max_respected(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-03", "phrasing:n001:p0", "R", 7.0, scale_max=10.0)
        self.assertEqual(errors, [])


# ---------------------------------------------------------------------------
# validate-level: graded EDGE Agreement (self-rate, R/C-on-edge rejection,
# abstain, unknown edge) -- ASSESSMENT-SPEC.md Amendments.
# ---------------------------------------------------------------------------

class ValidateEdgeAssessmentTest(unittest.TestCase):
    def _state(self):
        events = [
            ev(1, "agent-01", "create_node", {"id": "n001", "kind": "claim", "text": "ground claim",
                                                "source": None, "title": None}),
            ev(2, "agent-01", "create_node", {"id": "n002", "kind": "claim", "text": "dependent claim",
                                                "source": None, "title": None}),
            ev(3, "agent-01", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
        ]
        return fold(events)

    def test_edge_agreement_rating_by_other_agent_ok(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-02", "e001", "A", 3.5)
        self.assertEqual(errors, [])

    def test_self_rate_on_own_edge_rejected(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-01", "e001", "A", 3.5)
        self.assertTrue(any(t == "self_rate" for t, _ in errors))

    def test_dim_r_invalid_for_edge(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-02", "e001", "R", 3.0)
        self.assertTrue(any(t == "invalid_dim" for t, _ in errors))

    def test_dim_c_invalid_for_edge(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-02", "e001", "C", 3.0)
        self.assertTrue(any(t == "invalid_dim" for t, _ in errors))

    def test_edge_abstain_value_ok(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-02", "e001", "A", "abstain")
        self.assertEqual(errors, [])

    def test_unknown_edge_target_rejected(self):
        state = self._state()
        errors, _ = validate.validate_rate(state, "agent-02", "e999", "A", 3.0)
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))


# ---------------------------------------------------------------------------
# ops/CLI-level: end-to-end write pipeline (validate -> append -> rebuild)
# ---------------------------------------------------------------------------

class OpsAssessmentTest(TempDirMixin, unittest.TestCase):
    def test_rate_end_to_end_updates_graph_json(self):
        r1 = ops.cmd_create_node(self.tmp, "author", "a claim")
        self.assertTrue(r1.ok)
        nid = r1.id
        r2 = ops.cmd_rate(self.tmp, "rater", f"phrasing:{nid}:p0", "R", 4.5)
        self.assertTrue(r2.ok, r2.errors)
        graph = queries.load_graph(self.tmp)
        self.assertAlmostEqual(graph["nodes"][0]["phrasings"][0]["scores"]["R"]["mean"], 4.5)

    def test_self_rate_rejected_end_to_end(self):
        r1 = ops.cmd_create_node(self.tmp, "author", "a claim")
        nid = r1.id
        r2 = ops.cmd_rate(self.tmp, "author", f"phrasing:{nid}:p0", "R", 4.5)
        self.assertFalse(r2.ok)
        self.assertTrue(any("self-rating" in e or "self_rate" in e for e in r2.errors))

    def test_re_rate_via_cmd_rate_supersedes(self):
        r1 = ops.cmd_create_node(self.tmp, "author", "a claim")
        nid = r1.id
        ops.cmd_rate(self.tmp, "rater", f"phrasing:{nid}:p0", "R", 1.0)
        ops.cmd_rate(self.tmp, "rater", f"phrasing:{nid}:p0", "R", 5.0)
        graph = queries.load_graph(self.tmp)
        scores = graph["nodes"][0]["phrasings"][0]["scores"]
        self.assertEqual(scores["R"]["n"], 1)
        self.assertAlmostEqual(scores["R"]["mean"], 5.0)

    def test_abstain_via_cmd_rate_removes_vote(self):
        r1 = ops.cmd_create_node(self.tmp, "author", "a claim")
        nid = r1.id
        ops.cmd_rate(self.tmp, "rater", f"phrasing:{nid}:p0", "R", 3.0)
        ops.cmd_rate(self.tmp, "rater", f"phrasing:{nid}:p0", "R", "abstain")
        graph = queries.load_graph(self.tmp)
        scores = graph["nodes"][0]["phrasings"][0]["scores"]
        self.assertEqual(scores["R"]["n"], 0)
        self.assertIsNone(scores["R"]["mean"])

    def test_value_out_of_range_rejected_end_to_end(self):
        r1 = ops.cmd_create_node(self.tmp, "author", "a claim")
        nid = r1.id
        r2 = ops.cmd_rate(self.tmp, "rater", f"phrasing:{nid}:p0", "R", 9.0)
        self.assertFalse(r2.ok)

    def test_dim_mismatch_rejected_end_to_end(self):
        r1 = ops.cmd_create_node(self.tmp, "author", "a claim")
        nid = r1.id
        r2 = ops.cmd_rate(self.tmp, "rater", nid, "R", 3.0)  # bare node id only accepts dim A
        self.assertFalse(r2.ok)

    def test_reputation_query_and_show_config(self):
        r1 = ops.cmd_create_node(self.tmp, "author", "a claim")
        nid = r1.id
        ops.cmd_rate(self.tmp, "rater", f"phrasing:{nid}:p0", "R", 4.0)
        graph = queries.load_graph(self.tmp)
        acc = queries.reputation(graph, "rater")
        self.assertIsNotNone(acc)
        self.assertIn("true_r", acc)
        self.assertIsNone(queries.reputation(graph, "no-such-agent"))

        cfg = queries.effective_config(self.tmp)
        self.assertEqual(cfg["assessment"]["reputation"]["prior"], 0.15)
        self.assertEqual(cfg["assessment"]["aggregation"]["iterations"], 12)


# ---------------------------------------------------------------------------
# ops/CLI-level: graded EDGE Agreement end-to-end (ASSESSMENT-SPEC.md
# Amendments).
# ---------------------------------------------------------------------------

class OpsEdgeAssessmentTest(TempDirMixin, unittest.TestCase):
    def _make_edge(self, author="author"):
        r1 = ops.cmd_create_node(self.tmp, author, "ground claim")
        r2 = ops.cmd_create_node(self.tmp, author, "dependent claim")
        r3 = ops.cmd_draw_ground(self.tmp, author, r1.id, r2.id)
        return r3.id

    def test_rate_edge_end_to_end_updates_graph_json(self):
        eid = self._make_edge()
        res = ops.cmd_rate(self.tmp, "rater", eid, "A", 3.2)
        self.assertTrue(res.ok, res.errors)
        graph = queries.load_graph(self.tmp)
        edge = graph["ground_edges"][0]
        self.assertAlmostEqual(edge["agreement"]["mean"], 3.2)
        self.assertEqual(edge["agreement"]["n"], 1)
        # structural fields must stay untouched by the graded layer
        self.assertEqual(edge["agrees"], 0)
        self.assertEqual(edge["strength"], 1)

    def test_rc_on_edge_rejected_end_to_end(self):
        eid = self._make_edge()
        res = ops.cmd_rate(self.tmp, "rater", eid, "R", 3.2)
        self.assertFalse(res.ok)
        res = ops.cmd_rate(self.tmp, "rater", eid, "C", 3.2)
        self.assertFalse(res.ok)

    def test_self_rate_edge_rejected_end_to_end(self):
        eid = self._make_edge()
        res = ops.cmd_rate(self.tmp, "author", eid, "A", 3.2)
        self.assertFalse(res.ok)
        self.assertTrue(any("self-rating" in e or "self_rate" in e for e in res.errors))

    def test_edge_re_rate_supersedes_end_to_end(self):
        eid = self._make_edge()
        ops.cmd_rate(self.tmp, "rater", eid, "A", 1.0)
        ops.cmd_rate(self.tmp, "rater", eid, "A", 4.5)
        graph = queries.load_graph(self.tmp)
        edge = graph["ground_edges"][0]
        self.assertEqual(edge["agreement"]["n"], 1)
        self.assertAlmostEqual(edge["agreement"]["mean"], 4.5)

    def test_edge_abstain_removes_vote_end_to_end(self):
        eid = self._make_edge()
        ops.cmd_rate(self.tmp, "rater", eid, "A", 3.0)
        ops.cmd_rate(self.tmp, "rater", eid, "A", "abstain")
        graph = queries.load_graph(self.tmp)
        edge = graph["ground_edges"][0]
        self.assertEqual(edge["agreement"]["n"], 0)
        self.assertIsNone(edge["agreement"]["mean"])

    def test_weighted_edge_aggregate_high_true_r_rater_moves_it_more(self):
        eid = self._make_edge()
        baseline = [f"base{i}" for i in range(1, 7)]
        for rater in baseline:
            res = ops.cmd_rate(self.tmp, rater, eid, "A", 3.0)
            self.assertTrue(res.ok, res.errors)
        graph = queries.load_graph(self.tmp)
        self.assertAlmostEqual(graph["ground_edges"][0]["agreement"]["mean"], 3.0,
                                msg="unanimous baseline -> mean exactly 3.0 regardless of weighting")

        # Give H a well-regarded authoring history (unanimously rated 5.0 by
        # the same baseline) so True_R climbs meaningfully above `prior`
        # BEFORE H ever rates the target edge.
        rh = ops.cmd_create_node(self.tmp, "H", "H's excellent claim")
        for rater in baseline:
            ops.cmd_rate(self.tmp, rater, f"phrasing:{rh.id}:p0", "R", 5.0)
        res = ops.cmd_rate(self.tmp, "H", eid, "A", 0.0)
        self.assertTrue(res.ok, res.errors)
        graph = queries.load_graph(self.tmp)
        mean_after_h = graph["ground_edges"][0]["agreement"]["mean"]
        self.assertLess(mean_after_h, 3.0, "H's high-True_R deviant vote should pull the mean down")

    def test_edge_author_reputation_gains_received_credit(self):
        # ASSESSMENT-SPEC.md Amendments: an edge author earns "received"
        # reputation credit from graded ratings on their edge, same as a
        # node/phrasing author already did.
        eid = self._make_edge(author="edge-author")
        for rater in ("r1", "r2", "r3", "r4", "r5", "r6"):
            ops.cmd_rate(self.tmp, rater, eid, "A", 4.0)
        graph = queries.load_graph(self.tmp)
        acc = queries.reputation(graph, "edge-author")
        self.assertIsNotNone(acc)
        self.assertGreater(acc["n_assessments"], 0)


# ---------------------------------------------------------------------------
# The reputation + weighted-aggregation mechanism itself (ASSESSMENT-SPEC §3/§4)
# ---------------------------------------------------------------------------

class ReputationMathTest(TempDirMixin, unittest.TestCase):
    """(a) a high-True_R rater moves an aggregate more than a low-True_R one;
    (b) reputation reflects BOTH authoring and rating-alignment inputs;
    (c) a brand-new agent sits near `prior`."""

    BASELINE_RATERS = [f"base{i}" for i in range(1, 7)]  # 6 raters

    def _build_baseline(self, data_dir):
        """author creates n001/p0; 6 baseline raters all rate it R=3.0 (a
        unanimous consensus, so the pre-perturbation aggregate is EXACTLY
        3.0 regardless of how those 6 raters happen to be weighted)."""
        r = ops.cmd_create_node(data_dir, "author", "the target claim")
        nid = r.id
        for rater in self.BASELINE_RATERS:
            res = ops.cmd_rate(data_dir, rater, f"phrasing:{nid}:p0", "R", 3.0)
            self.assertTrue(res.ok, res.errors)
        return nid

    def test_high_true_r_rater_moves_aggregate_more_than_low_true_r_rater(self):
        # --- Scenario A: a HIGH-True_R agent ("H") casts one deviant vote ---
        tmp_a = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp_a, ignore_errors=True)
        nid_a = self._build_baseline(tmp_a)
        # Give H an established, well-regarded authoring history: H's OWN
        # node/phrasing, unanimously rated 5.0 (max) by the same 6 baseline
        # raters -- so H accumulates real confidence (n_received=6) and a
        # high authoring input (auth=1.0) BEFORE H ever touches the target.
        rh = ops.cmd_create_node(tmp_a, "H", "H's excellent claim")
        for rater in self.BASELINE_RATERS:
            ops.cmd_rate(tmp_a, rater, f"phrasing:{rh.id}:p0", "R", 5.0)
        # Now H rates the TARGET at the opposite extreme (0.0).
        res = ops.cmd_rate(tmp_a, "H", f"phrasing:{nid_a}:p0", "R", 0.0)
        self.assertTrue(res.ok, res.errors)
        graph_a = queries.load_graph(tmp_a)
        mean_a = graph_a["nodes"][0]["phrasings"][0]["scores"]["R"]["mean"]
        true_r_h = queries.reputation(graph_a, "H")["true_r"]

        # --- Scenario B: a brand-new, LOW-True_R agent ("L") casts the SAME
        # deviant vote (0.0) on an otherwise-identical baseline, with no
        # authoring history at all. ---
        tmp_b = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp_b, ignore_errors=True)
        nid_b = self._build_baseline(tmp_b)
        res = ops.cmd_rate(tmp_b, "L", f"phrasing:{nid_b}:p0", "R", 0.0)
        self.assertTrue(res.ok, res.errors)
        graph_b = queries.load_graph(tmp_b)
        mean_b = graph_b["nodes"][0]["phrasings"][0]["scores"]["R"]["mean"]
        true_r_l = queries.reputation(graph_b, "L")["true_r"]

        # H must have accumulated meaningfully more reputation than L can
        # possibly have on their very first action (confidence ~ n/(n+K)).
        self.assertGreater(true_r_h, true_r_l)
        prior = assess.DEFAULT_ASSESSMENT_CONFIG["reputation"]["prior"]
        self.assertLess(abs(true_r_l - prior), 0.15, "a first-action newcomer should sit near `prior`")

        # Both pull the 3.0 unanimous baseline down (same deviant value,
        # opposite direction from consensus); H, with far more weight,
        # must pull it down BY MORE than L does.
        self.assertLess(mean_a, 3.0)
        self.assertLess(mean_b, 3.0)
        self.assertGreater(3.0 - mean_a, 3.0 - mean_b,
                            f"high-True_R rater (true_r={true_r_h:.4f}) should move the aggregate "
                            f"more than the low-True_R rater (true_r={true_r_l:.4f}): "
                            f"mean_a={mean_a:.4f} mean_b={mean_b:.4f}")

    def test_new_account_sits_near_prior(self):
        r = ops.cmd_create_node(self.tmp, "author", "a claim")
        nid = r.id
        res = ops.cmd_rate(self.tmp, "newcomer", f"phrasing:{nid}:p0", "R", 3.0)
        self.assertTrue(res.ok, res.errors)
        graph = queries.load_graph(self.tmp)
        acc = queries.reputation(graph, "newcomer")
        prior = assess.DEFAULT_ASSESSMENT_CONFIG["reputation"]["prior"]
        self.assertLess(acc["confidence"], 0.2, "conf should be near 0 for a first-action account")
        self.assertLess(abs(acc["true_r"] - prior), 0.15)

    def test_reputation_reflects_authoring_input(self):
        # "author" authors a phrasing that several others rate highly, and
        # never rates anything themself (authoring-only input).
        r = ops.cmd_create_node(self.tmp, "author", "a well-received claim")
        nid = r.id
        for rater in ("r1", "r2", "r3", "r4", "r5", "r6"):
            ops.cmd_rate(self.tmp, rater, f"phrasing:{nid}:p0", "R", 5.0)
        graph = queries.load_graph(self.tmp)
        acc = queries.reputation(graph, "author")
        prior = assess.DEFAULT_ASSESSMENT_CONFIG["reputation"]["prior"]
        self.assertEqual(acc["rated"], 0, "author never rated anything themselves")
        self.assertGreater(acc["authored"], 0)
        self.assertGreater(acc["true_r"], prior, "consistently well-rated authorship should raise True_R above prior")

    def test_reputation_reflects_rating_alignment_input(self):
        # "aligner" authors nothing, but rates several already-multiply-rated
        # items in close agreement with the emerging consensus (rating-only
        # input).
        r = ops.cmd_create_node(self.tmp, "author", "claim one")
        nid1 = r.id
        r2 = ops.cmd_create_node(self.tmp, "author2", "claim two")
        nid2 = r2.id
        for target_nid in (nid1, nid2):
            for rater in ("r1", "r2", "r3", "r4", "r5", "r6"):
                ops.cmd_rate(self.tmp, rater, f"phrasing:{target_nid}:p0", "R", 4.0)
            # aligner agrees closely with the 4.0 consensus every time
            ops.cmd_rate(self.tmp, "aligner", f"phrasing:{target_nid}:p0", "R", 4.0)
        graph = queries.load_graph(self.tmp)
        acc = queries.reputation(graph, "aligner")
        prior = assess.DEFAULT_ASSESSMENT_CONFIG["reputation"]["prior"]
        self.assertEqual(acc["authored"], 0)
        self.assertEqual(acc["rated"], 2)
        self.assertGreater(acc["true_r"], prior, "consistently well-aligned rating should raise True_R above prior")

    def test_abstains_excluded_from_aggregate(self):
        r = ops.cmd_create_node(self.tmp, "author", "a claim")
        nid = r.id
        ops.cmd_rate(self.tmp, "r1", f"phrasing:{nid}:p0", "R", 5.0)
        ops.cmd_rate(self.tmp, "r2", f"phrasing:{nid}:p0", "R", "abstain")
        graph = queries.load_graph(self.tmp)
        scores = graph["nodes"][0]["phrasings"][0]["scores"]
        self.assertEqual(scores["R"]["n"], 1, "abstaining agent must not count toward n")
        self.assertAlmostEqual(scores["R"]["mean"], 5.0)


# ---------------------------------------------------------------------------
# Determinism: the fixed-point loop must not break BUILD-SPEC.md §3's
# byte-for-byte rebuild guarantee.
# ---------------------------------------------------------------------------

class DeterminismAssessmentTest(unittest.TestCase):
    SAMPLE_EVENTS = [
        ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
        ev(2, "a2", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
        ev(3, "a1", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
        ev(4, "a3", "propose_phrasing", {"id": "p1", "node": "n001", "text": "A restated"}),
        ev(5, "a4", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": 4.0}),
        ev(6, "a5", "rate", {"target": "phrasing:n001:p0", "dim": "C", "value": 3.5}),
        ev(7, "a2", "rate", {"target": "phrasing:n001:p1", "dim": "R", "value": 2.0}),
        ev(8, "a3", "rate", {"target": "n002", "dim": "A", "value": 4.5}),
        ev(9, "a4", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": "abstain"}),
        ev(10, "a1", "rate", {"target": "phrasing:n001:p0", "dim": "R", "value": 1.0}),
        ev(11, "a5", "rate", {"target": "phrasing:n001:p1", "dim": "R", "value": 4.0}),
    ]

    def test_fold_plus_serialize_is_byte_stable_across_runs(self):
        outputs = []
        for _ in range(6):
            gj = to_graph_json(fold(self.SAMPLE_EVENTS))
            outputs.append(json.dumps(gj, sort_keys=True, indent=2))
        self.assertEqual(len(set(outputs)), 1, "rebuild with ratings present must be byte-for-byte deterministic")

    def test_fixed_point_converges_before_iteration_cap(self):
        # A small, simple scenario should stabilize True_R well within the
        # default 12-iteration cap -- sanity check that the loop is actually
        # converging, not merely bounded.
        state = fold(self.SAMPLE_EVENTS)
        computed = assess.compute(state)
        self.assertTrue(computed["true_r"])  # non-empty
        for v in computed["true_r"].values():
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0)


class DeterminismAssessmentRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_write_rate_events_then_rebuild_is_idempotent(self):
        r1 = ops.cmd_create_node(self.tmp, "author", "hello world")
        nid = r1.id
        for i, agent in enumerate(["r1", "r2", "r3", "r4"]):
            ops.cmd_rate(self.tmp, agent, f"phrasing:{nid}:p0", "R", float(i))

        before = (self.tmp / "graph.json").read_text()
        ops.rebuild(self.tmp)
        after = (self.tmp / "graph.json").read_text()
        self.assertEqual(before, after)
        ops.rebuild(self.tmp)
        after2 = (self.tmp / "graph.json").read_text()
        self.assertEqual(after, after2)


# ---------------------------------------------------------------------------
# Determinism with graded EDGE Agreement present (ASSESSMENT-SPEC.md
# Amendments) -- the fixed-point loop must stay byte-for-byte deterministic
# with edge ratings mixed in, same guarantee test_fold_plus_serialize_is_
# byte_stable_across_runs already covers for node/phrasing ratings.
# ---------------------------------------------------------------------------

class DeterminismEdgeAssessmentTest(unittest.TestCase):
    SAMPLE_EVENTS = [
        ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
        ev(2, "a2", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
        ev(3, "a1", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
        ev(4, "a3", "rate", {"target": "e001", "dim": "A", "value": 3.5}),
        ev(5, "a4", "rate", {"target": "e001", "dim": "A", "value": 1.0}),
        ev(6, "a3", "rate", {"target": "e001", "dim": "A", "value": "abstain"}),
        ev(7, "a5", "rate", {"target": "n001", "dim": "A", "value": 4.0}),
    ]

    def test_fold_plus_serialize_is_byte_stable_with_edge_ratings(self):
        outputs = []
        for _ in range(6):
            gj = to_graph_json(fold(self.SAMPLE_EVENTS))
            outputs.append(json.dumps(gj, sort_keys=True, indent=2))
        self.assertEqual(len(set(outputs)), 1, "rebuild with edge ratings present must be byte-for-byte deterministic")


class DeterminismEdgeAssessmentRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_write_edge_rate_events_then_rebuild_is_idempotent(self):
        r1 = ops.cmd_create_node(self.tmp, "author", "ground claim")
        r2 = ops.cmd_create_node(self.tmp, "author", "dependent claim")
        r3 = ops.cmd_draw_ground(self.tmp, "author", r1.id, r2.id)
        eid = r3.id
        for i, agent in enumerate(["r1", "r2", "r3", "r4"]):
            ops.cmd_rate(self.tmp, agent, eid, "A", float(i))

        before = (self.tmp / "graph.json").read_text()
        ops.rebuild(self.tmp)
        after = (self.tmp / "graph.json").read_text()
        self.assertEqual(before, after)
        ops.rebuild(self.tmp)
        after2 = (self.tmp / "graph.json").read_text()
        self.assertEqual(after, after2)


# ---------------------------------------------------------------------------
# CLI-level smoke tests (subprocess, exercising graph.py's argparse wiring)
# ---------------------------------------------------------------------------

class CliAssessmentSmokeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_help_documents_new_verbs(self):
        r = subprocess.run([sys.executable, str(GRAPH_PY), "--help"], capture_output=True, text=True,
                            cwd=str(V0_DIR))
        self.assertEqual(r.returncode, 0)
        for verb in ("rate", "reputation", "show-config"):
            self.assertIn(verb, r.stdout)

    def test_rate_reputation_show_config_end_to_end(self):
        r = run(self.tmp, "create-node", "--agent", "author", "--text", "a claim for rating")
        nid = json.loads(r.stdout)["id"]

        r = run(self.tmp, "rate", "--agent", "rater", "--target", f"phrasing:{nid}:p0", "--dim", "R", "--value", "4.0")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout)["ok"])

        # self-rate rejected via CLI
        r = run(self.tmp, "rate", "--agent", "author", "--target", f"phrasing:{nid}:p0", "--dim", "R", "--value", "4.0")
        self.assertEqual(r.returncode, 1)
        self.assertFalse(json.loads(r.stdout)["ok"])

        # abstain accepted as a value
        r = run(self.tmp, "rate", "--agent", "rater2", "--target", f"phrasing:{nid}:p0", "--dim", "R",
                "--value", "abstain")
        self.assertEqual(r.returncode, 0, r.stderr)

        r = run(self.tmp, "reputation")
        self.assertEqual(r.returncode, 0, r.stderr)
        accounts = json.loads(r.stdout)["accounts"]
        self.assertTrue(any(a["agent"] == "rater" for a in accounts))

        r = run(self.tmp, "reputation", "--agent", "rater")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout)["account"]["agent"], "rater")

        r = run(self.tmp, "show-config")
        self.assertEqual(r.returncode, 0, r.stderr)
        cfg = json.loads(r.stdout)["assessment"]
        self.assertEqual(cfg["reputation"]["prior"], 0.15)
        self.assertEqual(cfg["aggregation"]["iterations"], 12)

    def test_show_config_honors_config_json_overrides(self):
        (self.tmp).mkdir(parents=True, exist_ok=True)
        (self.tmp / "config.json").write_text(json.dumps({
            "question": "custom question?",
            "assessment": {"reputation": {"K": 20}},
        }))
        r = run(self.tmp, "show-config")
        self.assertEqual(r.returncode, 0, r.stderr)
        cfg = json.loads(r.stdout)
        self.assertEqual(cfg["question"], "custom question?")
        self.assertEqual(cfg["assessment"]["reputation"]["K"], 20)
        # untouched knobs still fall back to their documented defaults
        self.assertEqual(cfg["assessment"]["reputation"]["prior"], 0.15)
        self.assertEqual(cfg["assessment"]["scale_max"], 5.0)

    def test_get_node_and_neighborhood_gain_assessment_fields(self):
        r = run(self.tmp, "create-node", "--agent", "author", "--text", "a claim")
        nid = json.loads(r.stdout)["id"]
        run(self.tmp, "rate", "--agent", "rater", "--target", f"phrasing:{nid}:p0", "--dim", "R", "--value", "4.0")
        run(self.tmp, "rate", "--agent", "rater", "--target", nid, "--dim", "A", "--value", "3.0")

        # PHASE2-SPEC.md §1/§8: with only n=1 ratings (< the default quorum
        # of 5) this target is "sealed" -- get-node/neighborhood mask its
        # mean by default now; --include-sealed opts back into seeing it
        # (used here since this test is about the assessment fields
        # existing/being wired through, not about the sealing convention
        # itself -- see test_lifecycle.py for sealed-surface coverage).
        r = run(self.tmp, "get-node", nid, "--include-sealed")
        rec = json.loads(r.stdout)
        self.assertIn("agreement", rec["node"])
        self.assertIn("quality", rec["node"])
        self.assertAlmostEqual(rec["node"]["agreement"]["mean"], 3.0)

        r = run(self.tmp, "neighborhood", "--node", nid, "--include-sealed")
        rec = json.loads(r.stdout)
        self.assertIn("agreement", rec["nodes"][0])
        self.assertIn("quality", rec["nodes"][0])

    def test_rate_edge_end_to_end_cli(self):
        r = run(self.tmp, "create-node", "--agent", "author", "--text", "ground claim")
        nid1 = json.loads(r.stdout)["id"]
        r = run(self.tmp, "create-node", "--agent", "author", "--text", "dependent claim")
        nid2 = json.loads(r.stdout)["id"]
        r = run(self.tmp, "draw-ground", "--agent", "author", "--from", nid1, "--to", nid2)
        eid = json.loads(r.stdout)["id"]

        r = run(self.tmp, "rate", "--agent", "rater", "--target", eid, "--dim", "A", "--value", "3.2")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout)["ok"])

        # R rejected on an edge (dim/target mismatch)
        r = run(self.tmp, "rate", "--agent", "rater", "--target", eid, "--dim", "R", "--value", "3.2")
        self.assertEqual(r.returncode, 1)
        self.assertFalse(json.loads(r.stdout)["ok"])

        # self-rate rejected (author drew the edge)
        r = run(self.tmp, "rate", "--agent", "author", "--target", eid, "--dim", "A", "--value", "3.2")
        self.assertEqual(r.returncode, 1)

        # n=1 rating is sealed by default (see the note in
        # test_get_node_and_neighborhood_gain_assessment_fields above).
        r = run(self.tmp, "get-node", nid2, "--include-sealed")
        rec = json.loads(r.stdout)
        ground = rec["grounds"][0]
        self.assertIn("agreement", ground)
        self.assertAlmostEqual(ground["agreement"]["mean"], 3.2)
        self.assertEqual(ground["agreement"]["n"], 1)
        # structural fields untouched
        self.assertEqual(ground["agrees"], 0)
        self.assertEqual(ground["strength"], 1)


if __name__ == "__main__":
    unittest.main()
