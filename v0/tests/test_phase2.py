"""Tests for PHASE2-SPEC.md: lifecycle states (§1), dispersion (§2), heat
(§3), eras/reopen (§4), blocs (§5), detectors (§6), group targets/nudge/chain
(§7). Additive to the frozen v0 core + v1 assessment layer -- mirrors the
layering of test_assessment.py/test_forums.py (fold-level, ops-level,
read-surface-level, determinism) rather than one monolithic file.
"""
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reasonable import chain as chain_mod  # noqa: E402
from reasonable import lifecycle, ops, queries  # noqa: E402
from reasonable.fold import fold, to_graph_json  # noqa: E402


def ev(seq, agent, verb, payload):
    return {"seq": seq, "ts": f"2026-01-01T00:00:{seq:02d}+00:00", "agent": agent, "verb": verb, "payload": payload}


class TempDirMixin:
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)


# ---------------------------------------------------------------------------
# §1: lifecycle state boundaries
# ---------------------------------------------------------------------------

class LifecycleStateTest(unittest.TestCase):
    CFG = {"quorum": 2, "confirm": 3, "contested_threshold": 1.0,
           "heat_half_life": 300.0, "heat_diffuse": 0.15, "cold_factor": 0.5}

    def _rated_node(self, values, cfg=None):
        events = [ev(1, "author", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                                    "source": None, "title": None})]
        for i, v in enumerate(values):
            events.append(ev(i + 2, f"r{i}", "rate", {"target": "n001", "dim": "A", "value": v, "era": 1}))
        gj = to_graph_json(fold(events), phase2_config=cfg or self.CFG)
        return gj["nodes"][0]["agreement"]

    def test_n_below_quorum_is_sealed(self):
        block = self._rated_node([3.0])  # n=1 < quorum=2
        self.assertEqual(block["state"], "sealed")
        self.assertEqual(block["n"], 1)

    def test_n_zero_is_sealed(self):
        block = self._rated_node([])
        self.assertEqual(block["state"], "sealed")
        self.assertEqual(block["n"], 0)
        self.assertIsNone(block["mean"])

    def test_n_at_quorum_below_confirm_is_provisional(self):
        block = self._rated_node([3.0, 3.0])  # n=2 == quorum, < confirm(3)
        self.assertEqual(block["state"], "provisional")

    def test_n_at_confirm_low_stdev_cold_is_settled(self):
        # A tiny, isolated graph: after the create_node event, MANY unrelated
        # nodes are created so the target's content heat (frozen at its own
        # creation seq) decays well below the site median (a short
        # heat_half_life makes the decay pronounced over just a few events,
        # keeping the test fast/small -- see heat tests below for the decay
        # formula itself).
        cfg = dict(self.CFG, heat_half_life=2.0)
        events = [ev(1, "author", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                                    "source": None, "title": None})]
        seq = 2
        for i in range(10):
            events.append(ev(seq, "author", "create_node",
                              {"id": f"n{i+2:03d}", "kind": "claim", "text": f"filler {i}",
                               "source": None, "title": None}))
            seq += 1
        for i, v in enumerate([3.0, 3.0, 3.0]):
            events.append(ev(seq, f"r{i}", "rate", {"target": "n001", "dim": "A", "value": v, "era": 1}))
            seq += 1
        gj = to_graph_json(fold(events), phase2_config=cfg)
        node1 = gj["nodes"][0]
        self.assertEqual(node1["id"], "n001")
        block = node1["agreement"]
        self.assertEqual(block["n"], 3)
        self.assertAlmostEqual(block["stdev"], 0.0)
        self.assertEqual(block["state"], "settled", gj["meta"]["heat_medians"])

    def test_n_at_confirm_low_stdev_hot_stays_provisional(self):
        # Same shape, but rate the FRESHEST node (created just before rating
        # -- minimal decay, so it is NOT cold relative to the site median).
        cfg = dict(self.CFG, heat_half_life=2.0)
        events = [ev(1, "author", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                                    "source": None, "title": None})]
        seq = 2
        for i in range(10):
            events.append(ev(seq, "author", "create_node",
                              {"id": f"n{i+2:03d}", "kind": "claim", "text": f"filler {i}",
                               "source": None, "title": None}))
            seq += 1
        last_node = "n011"  # last of the 10 filler nodes (n002..n011)
        for i, v in enumerate([3.0, 3.0, 3.0]):
            events.append(ev(seq, f"r{i}", "rate", {"target": last_node, "dim": "A", "value": v, "era": 1}))
            seq += 1
        gj = to_graph_json(fold(events), phase2_config=cfg)
        nodes_by_id = {n["id"]: n for n in gj["nodes"]}
        block = nodes_by_id[last_node]["agreement"]
        self.assertEqual(block["n"], 3)
        self.assertEqual(block["state"], "provisional")

    def test_static_settles_hot_noncontested_target(self):
        # Identical HOT scenario to the test above, but `static: true` (frozen
        # presentation graph). The cold gate is skipped, so a converged,
        # non-contested, at-confirm target reads `settled` instead of the
        # build-order artifact `provisional`.
        cfg = dict(self.CFG, heat_half_life=2.0, static=True)
        events = [ev(1, "author", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                                    "source": None, "title": None})]
        seq = 2
        for i in range(10):
            events.append(ev(seq, "author", "create_node",
                              {"id": f"n{i+2:03d}", "kind": "claim", "text": f"filler {i}",
                               "source": None, "title": None}))
            seq += 1
        last_node = "n011"
        for i, v in enumerate([3.0, 3.0, 3.0]):
            events.append(ev(seq, f"r{i}", "rate", {"target": last_node, "dim": "A", "value": v, "era": 1}))
            seq += 1
        gj = to_graph_json(fold(events), phase2_config=cfg)
        block = {n["id"]: n for n in gj["nodes"]}[last_node]["agreement"]
        self.assertEqual(block["n"], 3)
        self.assertEqual(block["state"], "settled")   # hot but static -> settled

    def test_contested_wins_over_settled(self):
        cfg = dict(self.CFG, heat_half_life=2.0, contested_threshold=1.0)
        events = [ev(1, "author", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                                    "source": None, "title": None})]
        seq = 2
        for i in range(10):
            events.append(ev(seq, "author", "create_node",
                              {"id": f"n{i+2:03d}", "kind": "claim", "text": f"filler {i}",
                               "source": None, "title": None}))
            seq += 1
        # High dispersion: half the raters say 0, half say 5 -- cold node
        # (same shape as the settled test) but stdev way above threshold.
        for i, v in enumerate([0.0, 5.0, 0.0]):
            events.append(ev(seq, f"r{i}", "rate", {"target": "n001", "dim": "A", "value": v, "era": 1}))
            seq += 1
        gj = to_graph_json(fold(events), phase2_config=cfg)
        block = gj["nodes"][0]["agreement"]
        self.assertGreater(block["stdev"], cfg["contested_threshold"])
        self.assertEqual(block["state"], "contested")


# ---------------------------------------------------------------------------
# §2: dispersion (stdev math)
# ---------------------------------------------------------------------------

class DispersionTest(unittest.TestCase):
    def test_population_stdev_known_values(self):
        # values 2,4,4,4,5,5,7,9 -> population stdev = 2.0 (textbook example)
        self.assertAlmostEqual(lifecycle.population_stdev([2, 4, 4, 4, 5, 5, 7, 9]), 2.0)

    def test_stdev_null_below_two_values(self):
        self.assertIsNone(lifecycle.population_stdev([]))
        self.assertIsNone(lifecycle.population_stdev([3.0]))

    def test_stdev_zero_for_identical_values(self):
        self.assertEqual(lifecycle.population_stdev([3.0, 3.0, 3.0]), 0.0)

    def test_block_for_reports_raw_not_weighted_stdev(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "r1", "rate", {"target": "n001", "dim": "A", "value": 1.0, "era": 1}),
            ev(3, "r2", "rate", {"target": "n001", "dim": "A", "value": 5.0, "era": 1}),
        ]
        gj = to_graph_json(fold(events))
        block = gj["nodes"][0]["agreement"]
        # population stdev of [1,5]: mean=3, var=((1-3)^2+(5-3)^2)/2=4, sd=2
        self.assertAlmostEqual(block["stdev"], 2.0)


# ---------------------------------------------------------------------------
# §3: heat -- decay, diffusion, cold, determinism
# ---------------------------------------------------------------------------

class HeatTest(unittest.TestCase):
    def test_decay_and_diffusion_formula_on_two_node_edge(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a2", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
        ]
        state = fold(events)
        half_life, diffuse = 300.0, 0.15
        heat = lifecycle.compute_heat_and_medians(state, {"heat_half_life": half_life, "heat_diffuse": diffuse})
        content = heat["_content_raw"]

        tip = 3
        decay1 = 0.5 ** ((tip - 1) / half_life)
        decay2 = 0.5 ** ((tip - 2) / half_life)
        decay3 = 0.5 ** ((tip - 3) / half_life)
        # create n001 (seq1): frac=1.0 at n001, neighbor n002 (final adjacency)
        expected_a = 1.0 * (1 - diffuse) * decay1
        expected_b = 1.0 * diffuse * decay1
        # create n002 (seq2): frac=1.0 at n002, neighbor n001
        expected_b += 1.0 * (1 - diffuse) * decay2
        expected_a += 1.0 * diffuse * decay2
        # draw_ground (seq3): 0.5/0.5 split, each diffuses 15% to the other
        expected_a += 0.5 * (1 - diffuse) * decay3 + 0.5 * diffuse * decay3
        expected_b += 0.5 * (1 - diffuse) * decay3 + 0.5 * diffuse * decay3

        self.assertAlmostEqual(content["n001"], expected_a, places=9)
        self.assertAlmostEqual(content["n002"], expected_b, places=9)

    def test_no_neighbors_keeps_full_share_at_node(self):
        events = [ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                                "source": None, "title": None})]
        state = fold(events)
        heat = lifecycle.compute_heat_and_medians(state, {"heat_half_life": 300.0, "heat_diffuse": 0.15})
        # tip == seq of the only event -> decay factor 1.0, no neighbors -> full 1.0 stays.
        self.assertAlmostEqual(heat["_content_raw"]["n001"], 1.0)

    def test_rating_heat_is_a_separate_ledger_from_content_heat(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "r1", "rate", {"target": "n001", "dim": "A", "value": 4.0, "era": 1}),
        ]
        gj = to_graph_json(fold(events))
        h = gj["nodes"][0]["heat"]
        self.assertIn("content", h)
        self.assertIn("rating", h)
        self.assertGreater(h["content"], 0.0)
        self.assertGreater(h["rating"], 0.0)

    def test_heat_rounded_to_six_decimals(self):
        events = [ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                                "source": None, "title": None})]
        gj = to_graph_json(fold(events))
        h = gj["nodes"][0]["heat"]["content"]
        self.assertEqual(h, round(h, 6))

    def test_cold_uses_site_median_of_nonzero_history(self):
        # A cluster of "hot" (recently touched) nodes and one long-cold node
        # -- cold_factor default 0.5 against the median of the hot cluster
        # should mark the old one cold, matching the state-machine test
        # above but exercised at the heat layer directly.
        cfg = {"heat_half_life": 2.0, "heat_diffuse": 0.15, "cold_factor": 0.5}
        events = [ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                                "source": None, "title": None})]
        for i in range(2, 12):
            events.append(ev(i, "a1", "create_node", {"id": f"n{i:03d}", "kind": "claim", "text": f"f{i}",
                                                        "source": None, "title": None}))
        state = fold(events)
        heat = lifecycle.compute_heat_and_medians(state, cfg)
        median = heat["site_median_content_heat"]
        self.assertLess(heat["_content_raw"]["n001"], cfg["cold_factor"] * median)

    def test_rebuild_is_byte_identical_across_repeated_folds(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a2", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a1", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            ev(4, "r1", "rate", {"target": "n001", "dim": "A", "value": 3.0, "era": 1}),
            ev(5, "r2", "rate", {"target": "e001", "dim": "A", "value": 4.0, "era": 1}),
        ]
        import json as _json
        outputs = {_json.dumps(to_graph_json(fold(events)), sort_keys=True) for _ in range(5)}
        self.assertEqual(len(outputs), 1, "same events.jsonl + same config -> byte-identical graph.json")


class HeatRebuildDeterminismTest(TempDirMixin, unittest.TestCase):
    def test_two_full_rebuilds_from_disk_are_byte_identical(self):
        ops.cmd_create_node(self.tmp, "a1", "claim one")
        r = ops.cmd_create_node(self.tmp, "a2", "claim two")
        n2 = r.id
        ops.cmd_rate(self.tmp, "r1", "n001", "A", 3.0)
        ops.cmd_rate(self.tmp, "r2", n2, "A", 4.5, bloc="b1")

        g1 = ops.rebuild(self.tmp)
        g2 = ops.rebuild(self.tmp)
        import json as _json
        self.assertEqual(_json.dumps(g1, sort_keys=True), _json.dumps(g2, sort_keys=True))


# ---------------------------------------------------------------------------
# §4: eras / reopen
# ---------------------------------------------------------------------------

class EraTest(TempDirMixin, unittest.TestCase):
    def test_new_target_starts_at_era_one(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        gj = queries.load_graph(self.tmp)
        self.assertEqual(gj["nodes"][0]["agreement"]["era"], 1)

    def test_reopen_increments_era_and_returns_to_sealed(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        for i in range(5):
            r = ops.cmd_rate(self.tmp, f"r{i}", "n001", "A", 3.0)
            self.assertTrue(r.ok, r.errors)
        gj = queries.load_graph(self.tmp)
        self.assertEqual(gj["nodes"][0]["agreement"]["n"], 5)
        self.assertNotEqual(gj["nodes"][0]["agreement"]["state"], "sealed")

        res = ops.cmd_reopen(self.tmp, "a1", "n001", "new counter-evidence surfaced")
        self.assertTrue(res.ok, res.errors)

        gj2 = queries.load_graph(self.tmp)
        block = gj2["nodes"][0]["agreement"]
        self.assertEqual(block["era"], 2)
        self.assertEqual(block["n"], 0, "prior-era ratings must not count in the new era")
        self.assertEqual(block["state"], "sealed")

    def test_prior_era_ratings_excluded_and_appear_in_history(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        for i in range(5):
            ops.cmd_rate(self.tmp, f"r{i}", "n001", "A", 2.0)
        ops.cmd_reopen(self.tmp, "a1", "n001", "reopening for new evidence")
        for i in range(3):
            ops.cmd_rate(self.tmp, f"s{i}", "n001", "A", 4.0)

        gj = queries.load_graph(self.tmp)
        block = gj["nodes"][0]["agreement"]
        self.assertEqual(block["era"], 2)
        self.assertEqual(block["n"], 3)
        self.assertAlmostEqual(block["mean"], 4.0, places=2)
        self.assertEqual(len(block["history"]), 1)
        h = block["history"][0]
        self.assertEqual(h["era"], 1)
        self.assertEqual(h["n"], 5)
        self.assertAlmostEqual(h["mean"], 2.0)

    def test_same_era_rerate_still_supersedes(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        ops.cmd_rate(self.tmp, "r1", "n001", "A", 1.0)
        ops.cmd_rate(self.tmp, "r1", "n001", "A", 5.0)
        gj = queries.load_graph(self.tmp)
        block = gj["nodes"][0]["agreement"]
        self.assertEqual(block["n"], 1)
        self.assertAlmostEqual(block["mean"], 5.0)

    def test_reopen_validation_rejects_unknown_target(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        res = ops.cmd_reopen(self.tmp, "a1", "n999", "bad target")
        self.assertFalse(res.ok)

    def test_reopen_validation_rejects_empty_reason(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        res = ops.cmd_reopen(self.tmp, "a1", "n001", "   ")
        self.assertFalse(res.ok)


# ---------------------------------------------------------------------------
# §5: blocs
# ---------------------------------------------------------------------------

class BlocTest(unittest.TestCase):
    def test_f_statistic_known_anova_example(self):
        # Two groups, clearly separated means, small within-group spread.
        groups = {"b1": [4.0, 4.2, 3.8], "b2": [1.0, 1.2, 0.8]}
        f = lifecycle.bloc_f_statistic(groups)
        # Hand-computed: grand_mean=2.5; ss_between=3*(1.5)^2*2=13.5;
        # ss_within=0.08+0.08=0.16; ms_between=13.5/1=13.5; ms_within=0.16/4=0.04
        # F ~= 13.5/0.04 = 337.5 (within 1e-6 EPS guard).
        self.assertAlmostEqual(f, 337.5, delta=0.001)

    def test_bloc_divergence_requires_two_qualifying_blocs(self):
        events = [ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                                "source": None, "title": None})]
        # Only one bloc has >= 3 ratings; a second bloc has just 1.
        for i, (agent, val, bloc) in enumerate([
            ("r1", 4.0, "b1"), ("r2", 4.0, "b1"), ("r3", 4.0, "b1"), ("r4", 1.0, "b2"),
        ]):
            events.append(ev(i + 2, agent, "rate", {"target": "n001", "dim": "A", "value": val,
                                                      "era": 1, "bloc": bloc}))
        gj = to_graph_json(fold(events))
        block = gj["nodes"][0]["agreement"]
        self.assertIsNone(block["bloc_divergence"])
        self.assertIn("b1", block["blocs"])
        self.assertIn("b2", block["blocs"])
        self.assertEqual(block["blocs"]["b2"]["n"], 1)

    def test_bloc_divergence_present_with_two_qualifying_blocs(self):
        events = [ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                                "source": None, "title": None})]
        vals = [("r1", 4.0, "b1"), ("r2", 4.2, "b1"), ("r3", 3.8, "b1"),
                ("r4", 1.0, "b2"), ("r5", 1.2, "b2"), ("r6", 0.8, "b2")]
        for i, (agent, val, bloc) in enumerate(vals):
            events.append(ev(i + 2, agent, "rate", {"target": "n001", "dim": "A", "value": val,
                                                      "era": 1, "bloc": bloc}))
        gj = to_graph_json(fold(events))
        block = gj["nodes"][0]["agreement"]
        self.assertIsNotNone(block["bloc_divergence"])
        self.assertGreater(block["bloc_divergence"], 3.0)
        self.assertAlmostEqual(block["blocs"]["b1"]["mean"], 4.0)
        self.assertAlmostEqual(block["blocs"]["b2"]["mean"], 1.0)

    def test_unbloc_d_ratings_excluded_from_bloc_breakdown(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "r1", "rate", {"target": "n001", "dim": "A", "value": 3.0, "era": 1}),  # no bloc
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(gj["nodes"][0]["agreement"]["blocs"], {})


# ---------------------------------------------------------------------------
# §7: group rating target
# ---------------------------------------------------------------------------

class GroupTargetTest(TempDirMixin, unittest.TestCase):
    def _make_conjunction(self):
        ops.cmd_create_node(self.tmp, "a1", "ground one")   # n001
        ops.cmd_create_node(self.tmp, "a1", "ground two")   # n002
        ops.cmd_create_node(self.tmp, "a1", "dependent")    # n003
        ops.cmd_draw_ground(self.tmp, "creator", "n001", "n003", group="new")
        # group id is assigned by ops as the edge's group field, not returned
        # directly by cmd_draw_ground -- read it back from graph.json.
        gj = queries.load_graph(self.tmp)
        gid = gj["conjunction_groups"][0]["id"]
        ops.cmd_draw_ground(self.tmp, "someone_else", "n002", "n003", group=gid)
        return gid

    def test_group_must_exist(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        res = ops.cmd_rate(self.tmp, "r1", "group:g999", "A", 3.0)
        self.assertFalse(res.ok)

    def test_group_dim_must_be_a(self):
        gid = self._make_conjunction()
        res = ops.cmd_rate(self.tmp, "r1", f"group:{gid}", "R", 3.0)
        self.assertFalse(res.ok)

    def test_group_creator_self_rate_rejected(self):
        gid = self._make_conjunction()
        # "creator" drew the first edge with --group new -- the group's author.
        res = ops.cmd_rate(self.tmp, "creator", f"group:{gid}", "A", 3.0)
        self.assertFalse(res.ok)

    def test_group_aggregates_with_full_lifecycle_block(self):
        gid = self._make_conjunction()
        for i in range(5):
            r = ops.cmd_rate(self.tmp, f"r{i}", f"group:{gid}", "A", 4.0)
            self.assertTrue(r.ok, r.errors)
        gj = queries.load_graph(self.tmp)
        group = gj["conjunction_groups"][0]
        self.assertEqual(group["id"], gid)
        self.assertIn("agreement", group)
        for key in ("mean", "n", "stdev", "state", "era", "history", "blocs", "bloc_divergence"):
            self.assertIn(key, group["agreement"])
        self.assertAlmostEqual(group["agreement"]["mean"], 4.0)
        self.assertEqual(group["agreement"]["n"], 5)


# ---------------------------------------------------------------------------
# §7: divergence nudge
# ---------------------------------------------------------------------------

class NudgeTest(TempDirMixin, unittest.TestCase):
    def test_nudge_fires_when_far_from_visible_mean(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        for i in range(5):
            ops.cmd_rate(self.tmp, f"r{i}", "n001", "A", 4.0)  # n=5 (>= default quorum), mean=4.0
        res = ops.cmd_rate(self.tmp, "outlier", "n001", "A", 0.5)  # 3.5 away >= 1.5 default
        self.assertTrue(res.ok)
        self.assertIsNotNone(res.data)
        self.assertIn("nudge", res.data)

    def test_nudge_does_not_fire_when_close(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        for i in range(5):
            ops.cmd_rate(self.tmp, f"r{i}", "n001", "A", 4.0)
        res = ops.cmd_rate(self.tmp, "close", "n001", "A", 4.2)
        self.assertTrue(res.ok)
        self.assertIsNone(res.data)

    def test_nudge_does_not_fire_while_sealed(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        ops.cmd_rate(self.tmp, "r1", "n001", "A", 4.0)  # n=1, sealed (< quorum)
        res = ops.cmd_rate(self.tmp, "r2", "n001", "A", 0.0)  # far, but still sealed
        self.assertTrue(res.ok)
        self.assertIsNone(res.data)

    def test_nudge_does_not_fire_on_abstain(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        for i in range(5):
            ops.cmd_rate(self.tmp, f"r{i}", "n001", "A", 4.0)
        res = ops.cmd_rate(self.tmp, "abstainer", "n001", "A", "abstain")
        self.assertTrue(res.ok)
        self.assertIsNone(res.data)

    def test_nudge_distance_override(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        for i in range(5):
            ops.cmd_rate(self.tmp, f"r{i}", "n001", "A", 4.0)
        # distance 0.6 wouldn't trigger the default 1.5, but does with an
        # explicit tighter override.
        res = ops.cmd_rate(self.tmp, "mild", "n001", "A", 3.4, nudge_distance=0.5)
        self.assertIsNotNone(res.data)
        self.assertIn("nudge", res.data)


# ---------------------------------------------------------------------------
# §1/§8: sealed read surfaces
# ---------------------------------------------------------------------------

class SealedReadSurfaceTest(TempDirMixin, unittest.TestCase):
    def test_get_node_masks_sealed_agreement_by_default(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        ops.cmd_rate(self.tmp, "r1", "n001", "A", 4.0)  # n=1, sealed
        graph = queries.load_graph(self.tmp)
        rec = queries.get_node(graph, "n001")
        agr = rec["node"]["agreement"]
        self.assertIsNone(agr["mean"])
        self.assertTrue(agr["pending"])
        self.assertEqual(agr["n"], 1)

    def test_get_node_include_sealed_shows_real_mean(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        ops.cmd_rate(self.tmp, "r1", "n001", "A", 4.0)
        graph = queries.load_graph(self.tmp)
        rec = queries.get_node(graph, "n001", include_sealed=True)
        agr = rec["node"]["agreement"]
        self.assertAlmostEqual(agr["mean"], 4.0)
        self.assertNotIn("pending", agr)

    def test_unsealed_target_never_masked(self):
        ops.cmd_create_node(self.tmp, "a1", "claim")
        for i in range(5):
            ops.cmd_rate(self.tmp, f"r{i}", "n001", "A", 4.0)  # n=5, provisional
        graph = queries.load_graph(self.tmp)
        rec = queries.get_node(graph, "n001")
        self.assertAlmostEqual(rec["node"]["agreement"]["mean"], 4.0)

    def test_neighborhood_masks_sealed_nodes(self):
        r = ops.cmd_create_node(self.tmp, "a1", "claim one")
        n1 = r.id
        r2 = ops.cmd_create_node(self.tmp, "a2", "claim two")
        n2 = r2.id
        ops.cmd_draw_ground(self.tmp, "a1", n1, n2)
        ops.cmd_rate(self.tmp, "r1", n2, "A", 4.5)  # n=1, sealed
        graph = queries.load_graph(self.tmp)
        rec = queries.neighborhood(graph, n1, depth=1)
        by_id = {n["id"]: n for n in rec["nodes"]}
        self.assertTrue(by_id[n2]["agreement"]["pending"])
        rec2 = queries.neighborhood(graph, n1, depth=1, include_sealed=True)
        by_id2 = {n["id"]: n for n in rec2["nodes"]}
        self.assertAlmostEqual(by_id2[n2]["agreement"]["mean"], 4.5)


# ---------------------------------------------------------------------------
# §7: chain
# ---------------------------------------------------------------------------

class ChainTest(TempDirMixin, unittest.TestCase):
    def test_product_weakest_link_partial_with_conjunction(self):
        r1 = ops.cmd_create_node(self.tmp, "a1", "n1 ancestor")
        n1 = r1.id
        r2 = ops.cmd_create_node(self.tmp, "a1", "n2 middle")
        n2 = r2.id
        r3 = ops.cmd_create_node(self.tmp, "a1", "n3 other conjunct")
        n3 = r3.id
        r4 = ops.cmd_create_node(self.tmp, "a1", "n4 descendant")
        n4 = r4.id

        re1 = ops.cmd_draw_ground(self.tmp, "creator", n1, n2, group="new")
        gj = queries.load_graph(self.tmp)
        gid = gj["conjunction_groups"][0]["id"]
        ops.cmd_draw_ground(self.tmp, "someone", n3, n2, group=gid)
        e3 = ops.cmd_draw_ground(self.tmp, "a1", n2, n4).id  # unrated on purpose

        ops.cmd_rate(self.tmp, "r1", n1, "A", 5.0)
        ops.cmd_rate(self.tmp, "r1", n2, "A", 3.0)
        ops.cmd_rate(self.tmp, "r1", n4, "A", 2.0)
        ops.cmd_rate(self.tmp, "r1", f"group:{gid}", "A", 4.0)

        graph = queries.load_graph(self.tmp)
        result = chain_mod.compute(graph, n1, n4, max_paths=16)
        self.assertTrue(result["ok"], result.get("errors"))
        self.assertEqual(len(result["paths"]), 1)
        path = result["paths"][0]
        self.assertEqual(path["nodes"], [n1, n2, n4])
        self.assertEqual(path["edges"], [re1.id, e3])

        expected_product = 1.0 * 0.6 * 0.4 * 0.8 * 0.5
        self.assertAlmostEqual(path["product"], expected_product, places=6)
        self.assertTrue(path["partial"], "e3 was never rated -> partial")
        self.assertAlmostEqual(path["weakest_link"]["factor"], 0.4)
        self.assertEqual(path["weakest_link"]["id"], n4)
        expected_geo = expected_product ** (1.0 / 5)
        self.assertAlmostEqual(path["geometric_mean"], expected_geo, places=6)
        # the grouped edge contributed via the group, not its own (never
        # separately rated) Agreement.
        group_factor = next(f for f in path["factors"] if f["kind"] == "group")
        self.assertAlmostEqual(group_factor["factor"], 0.8)
        self.assertEqual(group_factor["id"], gid)

    def test_unknown_endpoint_is_an_error(self):
        r1 = ops.cmd_create_node(self.tmp, "a1", "only node")
        graph = queries.load_graph(self.tmp)
        result = chain_mod.compute(graph, r1.id, "n999")
        self.assertFalse(result["ok"])

    def test_max_paths_cap_and_deterministic_order(self):
        # Two disjoint parallel paths from n1 to n4: n1->n2->n4 and n1->n3->n4.
        r1 = ops.cmd_create_node(self.tmp, "a1", "n1")
        n1 = r1.id
        r2 = ops.cmd_create_node(self.tmp, "a1", "n2")
        n2 = r2.id
        r3 = ops.cmd_create_node(self.tmp, "a1", "n3")
        n3 = r3.id
        r4 = ops.cmd_create_node(self.tmp, "a1", "n4")
        n4 = r4.id
        ops.cmd_draw_ground(self.tmp, "a1", n1, n2)
        ops.cmd_draw_ground(self.tmp, "a1", n2, n4)
        ops.cmd_draw_ground(self.tmp, "a1", n1, n3)
        ops.cmd_draw_ground(self.tmp, "a1", n3, n4)

        graph = queries.load_graph(self.tmp)
        result = chain_mod.compute(graph, n1, n4, max_paths=1)
        self.assertEqual(len(result["paths"]), 1)
        full = chain_mod.compute(graph, n1, n4, max_paths=16)
        self.assertEqual(len(full["paths"]), 2)
        # deterministic: sorted by node-id tuple, n2 < n3
        self.assertEqual(full["paths"][0]["nodes"], [n1, n2, n4])
        self.assertEqual(full["paths"][1]["nodes"], [n1, n3, n4])
        # the capped call must match the FIRST of the full, sorted order
        self.assertEqual(result["paths"][0]["nodes"], full["paths"][0]["nodes"])


# ---------------------------------------------------------------------------
# §7b: compare (last-common-ancestor chain comparison -- UI/display helper)
# ---------------------------------------------------------------------------

class CompareTest(TempDirMixin, unittest.TestCase):
    def test_two_branches_off_a_shared_root(self):
        # R grounds two competing branches: R->mA->A (strong) and R->mB->B (weak).
        R = ops.cmd_create_node(self.tmp, "a1", "shared root").id
        mA = ops.cmd_create_node(self.tmp, "a1", "middle a").id
        A = ops.cmd_create_node(self.tmp, "a1", "claim a").id
        mB = ops.cmd_create_node(self.tmp, "a1", "middle b").id
        B = ops.cmd_create_node(self.tmp, "a1", "claim b").id
        ops.cmd_draw_ground(self.tmp, "a1", R, mA)
        ops.cmd_draw_ground(self.tmp, "a1", mA, A)
        ops.cmd_draw_ground(self.tmp, "a1", R, mB)
        ops.cmd_draw_ground(self.tmp, "a1", mB, B)
        for nid, v in [(R, 5.0), (mA, 5.0), (A, 4.0), (mB, 5.0), (B, 2.0)]:
            ops.cmd_rate(self.tmp, "r1", nid, "A", v)

        graph = queries.load_graph(self.tmp)
        result = chain_mod.compare(graph, A, B, max_paths=16)
        self.assertTrue(result["ok"], result.get("errors"))
        self.assertEqual(result["common_ancestors"], [R])
        self.assertEqual(len(result["comparisons"]), 1)
        c = result["comparisons"][0]
        self.assertEqual(c["lca"], R)
        # a: 1.0*0.5*1.0*0.5*0.8 = 0.2 ; b: 1.0*0.5*1.0*0.5*0.4 = 0.1 (edges unrated -> 0.5)
        self.assertAlmostEqual(c["a_leg"]["strongest"]["product"], 0.2, places=6)
        self.assertAlmostEqual(c["b_leg"]["strongest"]["product"], 0.1, places=6)
        self.assertEqual(c["verdict"], "a")
        self.assertAlmostEqual(c["margin"], 0.1, places=6)

    def test_one_node_is_ancestor_of_the_other_trivial_leg(self):
        # R->X->Y ; compare X vs Y -> LCA is X itself, X's leg is trivial.
        R = ops.cmd_create_node(self.tmp, "a1", "root").id
        X = ops.cmd_create_node(self.tmp, "a1", "x").id
        Y = ops.cmd_create_node(self.tmp, "a1", "y").id
        ops.cmd_draw_ground(self.tmp, "a1", R, X)
        ops.cmd_draw_ground(self.tmp, "a1", X, Y)
        for nid, v in [(R, 5.0), (X, 4.0), (Y, 3.0)]:
            ops.cmd_rate(self.tmp, "r1", nid, "A", v)

        graph = queries.load_graph(self.tmp)
        result = chain_mod.compare(graph, X, Y, max_paths=16)
        self.assertEqual(result["common_ancestors"], [X])
        c = result["comparisons"][0]
        self.assertTrue(c["a_leg"]["trivial"])
        self.assertEqual(c["a_leg"]["strongest"]["nodes"], [X])
        self.assertAlmostEqual(c["a_leg"]["strongest"]["product"], 0.8, places=6)  # X's own A=4/5
        # b: X->Y = 0.8 * 0.5(unrated edge) * 0.6 = 0.24
        self.assertAlmostEqual(c["b_leg"]["strongest"]["product"], 0.24, places=6)
        self.assertEqual(c["verdict"], "a")

    def test_no_common_ancestor(self):
        P = ops.cmd_create_node(self.tmp, "a1", "p").id
        Q = ops.cmd_create_node(self.tmp, "a1", "q").id
        graph = queries.load_graph(self.tmp)
        result = chain_mod.compare(graph, P, Q)
        self.assertTrue(result["ok"])
        self.assertEqual(result["common_ancestors"], [])
        self.assertEqual(result["comparisons"], [])

    def test_same_node_is_an_error(self):
        P = ops.cmd_create_node(self.tmp, "a1", "p").id
        graph = queries.load_graph(self.tmp)
        result = chain_mod.compare(graph, P, P)
        self.assertFalse(result["ok"])


if __name__ == "__main__":
    unittest.main()
