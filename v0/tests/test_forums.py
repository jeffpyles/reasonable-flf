"""Tests for FORUMS-SPEC.md: `comment`, `propose_typing`, and the extended
`agree` targets (`comment:<cid>`, `typing:<edge>:<tyid>`). Additive to the
frozen BUILD-SPEC core -- mirrors the layering of the existing test files
(fold-level, validate-level, CLI-level, determinism) rather than adding a
single monolithic test.
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

from reasonable import ops, queries, validate  # noqa: E402
from reasonable.fold import fold, to_graph_json  # noqa: E402

V0_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
GRAPH_PY = V0_DIR / "graph.py"


def ev(seq, agent, verb, payload):
    return {"seq": seq, "ts": f"2026-01-01T00:00:{seq:02d}+00:00", "agent": agent, "verb": verb, "payload": payload}


# ---------------------------------------------------------------------------
# fold-level: comment / typing shape, thread structure, primary_typing math
# ---------------------------------------------------------------------------

class FoldForumsTest(unittest.TestCase):
    def test_comment_on_node_appears_in_node_record_flat_and_in_comment_count(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a2", "comment", {"id": "c001", "target": "n001", "parent": None, "text": "hi"}),
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(len(gj["nodes"][0]["comments"]), 1)
        c = gj["nodes"][0]["comments"][0]
        # PHASE2-SPEC.md §2: scores blocks now carry the full lifecycle
        # envelope, not just {mean, n} -- see test_fold.py's equivalent note.
        _empty_dim = {"mean": None, "n": 0, "stdev": None, "state": "sealed", "era": 1,
                      "history": [], "blocs": {}, "bloc_divergence": None}
        self.assertEqual(c, {"id": "c001", "parent": None, "agent": "a2", "ts": "2026-01-01T00:00:02+00:00",
                             "text": "hi", "agrees": 0, "agents": [],
                             "scores": {"R": dict(_empty_dim), "C": dict(_empty_dim)}})
        self.assertEqual(gj["meta"]["comment_count"], 1)

    def test_comment_on_edge_appears_in_edge_record(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a2", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            ev(4, "a2", "comment", {"id": "c001", "target": "e001", "parent": None, "text": "what inference?"}),
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(len(gj["ground_edges"][0]["comments"]), 1)
        self.assertEqual(gj["nodes"][0]["comments"], [])  # not leaked onto the node

    def test_reply_threading_via_parent_field(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a2", "comment", {"id": "c001", "target": "n001", "parent": None, "text": "top"}),
            ev(3, "a3", "comment", {"id": "c002", "target": "n001", "parent": "c001", "text": "reply"}),
        ]
        gj = to_graph_json(fold(events))
        comments = gj["nodes"][0]["comments"]
        self.assertEqual(len(comments), 2)
        by_id = {c["id"]: c for c in comments}
        self.assertIsNone(by_id["c001"]["parent"])
        self.assertEqual(by_id["c002"]["parent"], "c001")

    def test_agree_on_comment_increments_agrees_and_agents(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a2", "comment", {"id": "c001", "target": "n001", "parent": None, "text": "top"}),
            ev(3, "a3", "agree", {"target": "comment:c001"}),
        ]
        gj = to_graph_json(fold(events))
        c = gj["nodes"][0]["comments"][0]
        self.assertEqual(c["agrees"], 1)
        self.assertEqual(c["agents"], ["a3"])

    def test_typing_with_node_and_typing_with_label_shapes(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a2", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            ev(4, "a3", "propose_typing", {"id": "ty1", "edge": "e001", "node": "n001", "label": None}),
            ev(5, "a4", "propose_typing", {"id": "ty2", "edge": "e001", "node": None, "label": "free text typing"}),
        ]
        gj = to_graph_json(fold(events))
        edge = gj["ground_edges"][0]
        self.assertEqual(len(edge["typings"]), 2)
        ty1, ty2 = edge["typings"]
        self.assertEqual(ty1, {"id": "ty1", "node": "n001", "label": None, "agrees": 0, "agents": [], "author": "a3"})
        self.assertEqual(ty2, {"id": "ty2", "node": None, "label": "free text typing", "agrees": 0, "agents": [],
                                "author": "a4"})

    def test_primary_typing_prefers_higher_agrees(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a2", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            ev(4, "a3", "propose_typing", {"id": "ty1", "edge": "e001", "node": "n001", "label": None}),
            ev(5, "a4", "propose_typing", {"id": "ty2", "edge": "e001", "node": None, "label": "x"}),
            ev(6, "a5", "agree", {"target": "typing:e001:ty2"}),
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(gj["ground_edges"][0]["primary_typing"], "ty2")

    def test_primary_typing_tie_break_is_earliest(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a2", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            ev(4, "a3", "propose_typing", {"id": "ty1", "edge": "e001", "node": "n001", "label": None}),
            ev(5, "a4", "propose_typing", {"id": "ty2", "edge": "e001", "node": None, "label": "x"}),
            # both stay at 0 agrees -> earliest (ty1) wins, same convention as titles/phrasings.
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(gj["ground_edges"][0]["primary_typing"], "ty1")

    def test_edge_with_no_typings_has_null_primary_typing_and_empty_list(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a2", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
        ]
        gj = to_graph_json(fold(events))
        edge = gj["ground_edges"][0]
        self.assertEqual(edge["typings"], [])
        self.assertIsNone(edge["primary_typing"])


# ---------------------------------------------------------------------------
# validate-level: mutual exclusivity, referential integrity, self-agree reuse
# ---------------------------------------------------------------------------

class ValidateForumsTest(unittest.TestCase):
    def _state_with_node_edge_comment(self):
        events = [
            ev(1, "agent-01", "create_node", {"id": "n001", "kind": "claim", "text": "claim one",
                                               "source": None, "title": None}),
            ev(2, "agent-02", "create_node", {"id": "n002", "kind": "claim", "text": "claim two",
                                               "source": None, "title": None}),
            ev(3, "agent-01", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            ev(4, "agent-01", "comment", {"id": "c001", "target": "n001", "parent": None, "text": "root comment"}),
        ]
        return fold(events)

    def test_comment_requires_exactly_one_of_target_or_reply_to(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_comment(state, "agent-02", None, "text", None)
        self.assertTrue(any(t == "target_parent_conflict" for t, _ in errors))
        errors, _ = validate.validate_comment(state, "agent-02", "n001", "text", "c001")
        self.assertTrue(any(t == "target_parent_conflict" for t, _ in errors))

    def test_comment_missing_target_rejected(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_comment(state, "agent-02", "n999", "text", None)
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))

    def test_comment_bad_parent_rejected(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_comment(state, "agent-02", None, "text", "c999")
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))

    def test_comment_on_edge_target_ok(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_comment(state, "agent-02", "e001", "text", None)
        self.assertEqual(errors, [])

    def test_comment_reply_ok(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_comment(state, "agent-02", None, "a reply", "c001")
        self.assertEqual(errors, [])

    def test_comment_empty_text_rejected(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_comment(state, "agent-02", "n001", "   ", None)
        self.assertTrue(any(t == "empty_text" for t, _ in errors))

    def test_comment_over_cap_is_warning_not_error(self):
        state = self._state_with_node_edge_comment()
        long_text = "x" * 2500
        errors, warnings = validate.validate_comment(state, "agent-02", "n001", long_text, None,
                                                       max_comment_chars=2000)
        self.assertEqual(errors, [])
        self.assertTrue(any(t == "over_cap" for t, _ in warnings))

    def test_propose_typing_requires_exactly_one_of_node_or_label(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_propose_typing(state, "agent-02", "e001", None, None)
        self.assertTrue(any(t == "typing_node_label_conflict" for t, _ in errors))
        errors, _ = validate.validate_propose_typing(state, "agent-02", "e001", "n001", "also a label")
        self.assertTrue(any(t == "typing_node_label_conflict" for t, _ in errors))

    def test_propose_typing_unknown_edge_rejected(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_propose_typing(state, "agent-02", "e999", "n001", None)
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))

    def test_propose_typing_bad_node_ref_rejected(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_propose_typing(state, "agent-02", "e001", "n999", None)
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))

    def test_propose_typing_with_node_ok(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_propose_typing(state, "agent-02", "e001", "n001", None)
        self.assertEqual(errors, [])

    def test_propose_typing_with_label_ok(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_propose_typing(state, "agent-02", "e001", None, "a free-text typing")
        self.assertEqual(errors, [])

    def test_self_agree_on_own_comment_rejected(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_agree(state, "agent-01", "comment:c001")
        self.assertTrue(any(t == "self_agree" for t, _ in errors))

    def test_agree_on_comment_by_other_agent_ok(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_agree(state, "agent-02", "comment:c001")
        self.assertEqual(errors, [])

    def test_agree_on_unknown_comment_rejected(self):
        state = self._state_with_node_edge_comment()
        errors, _ = validate.validate_agree(state, "agent-02", "comment:c999")
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))

    def test_self_agree_on_own_typing_rejected(self):
        events = [
            ev(1, "agent-01", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                               "source": None, "title": None}),
            ev(2, "agent-01", "create_node", {"id": "n002", "kind": "claim", "text": "B",
                                               "source": None, "title": None}),
            ev(3, "agent-01", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            ev(4, "agent-02", "propose_typing", {"id": "ty1", "edge": "e001", "node": "n001", "label": None}),
        ]
        state = fold(events)
        errors, _ = validate.validate_agree(state, "agent-02", "typing:e001:ty1")
        self.assertTrue(any(t == "self_agree" for t, _ in errors))
        errors, _ = validate.validate_agree(state, "agent-03", "typing:e001:ty1")
        self.assertEqual(errors, [])

    def test_agree_on_unknown_typing_rejected(self):
        events = [
            ev(1, "agent-01", "create_node", {"id": "n001", "kind": "claim", "text": "A",
                                               "source": None, "title": None}),
            ev(2, "agent-01", "create_node", {"id": "n002", "kind": "claim", "text": "B",
                                               "source": None, "title": None}),
            ev(3, "agent-01", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
        ]
        state = fold(events)
        errors, _ = validate.validate_agree(state, "agent-02", "typing:e001:ty9")
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))
        errors, _ = validate.validate_agree(state, "agent-02", "typing:e999:ty1")
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))


# ---------------------------------------------------------------------------
# ops-level: full locked write pipeline (append -> rebuild), reply target
# inheritance, ranking via queries.thread_comments
# ---------------------------------------------------------------------------

class OpsForumsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_reply_inherits_parents_target(self):
        n1 = ops.cmd_create_node(self.tmp, "agent-01", "claim one").id
        c1 = ops.cmd_comment(self.tmp, "agent-02", target=n1, text="top-level").id
        c2 = ops.cmd_comment(self.tmp, "agent-03", reply_to=c1, text="a reply").id

        graph = queries.load_graph(self.tmp)
        rec = queries.list_comments(graph, n1)
        ids = {c["id"] for c in rec["comments"]}
        self.assertEqual(ids, {c1, c2})  # reply landed on the SAME target as its parent

    def test_agree_ranking_orders_siblings_by_agrees_desc_then_seq(self):
        n1 = ops.cmd_create_node(self.tmp, "agent-01", "claim one").id
        c1 = ops.cmd_comment(self.tmp, "agent-02", target=n1, text="first").id
        c2 = ops.cmd_comment(self.tmp, "agent-03", target=n1, text="second").id
        c3 = ops.cmd_comment(self.tmp, "agent-04", target=n1, text="third").id
        # c3 gets two agrees, c2 gets one, c1 gets none -> ranked c3, c2, c1
        ops.cmd_agree(self.tmp, "agent-01", f"comment:{c3}")
        ops.cmd_agree(self.tmp, "agent-05", f"comment:{c3}")
        ops.cmd_agree(self.tmp, "agent-01", f"comment:{c2}")

        graph = queries.load_graph(self.tmp)
        rec = queries.list_comments(graph, n1)
        ranked = queries.thread_comments(rec["comments"])
        self.assertEqual([c["id"] for c in ranked], [c3, c2, c1])

    def test_self_agree_on_comment_rejected_end_to_end(self):
        n1 = ops.cmd_create_node(self.tmp, "agent-01", "claim one").id
        c1 = ops.cmd_comment(self.tmp, "agent-02", target=n1, text="top-level").id
        res = ops.cmd_agree(self.tmp, "agent-02", f"comment:{c1}")
        self.assertFalse(res.ok)
        self.assertTrue(any("self-agree" in e for e in res.errors))

    def test_duplicate_agree_on_comment_rejected(self):
        n1 = ops.cmd_create_node(self.tmp, "agent-01", "claim one").id
        c1 = ops.cmd_comment(self.tmp, "agent-02", target=n1, text="top-level").id
        r1 = ops.cmd_agree(self.tmp, "agent-03", f"comment:{c1}")
        self.assertTrue(r1.ok)
        r2 = ops.cmd_agree(self.tmp, "agent-03", f"comment:{c1}")
        self.assertFalse(r2.ok)

    def test_propose_typing_node_and_label_end_to_end(self):
        n1 = ops.cmd_create_node(self.tmp, "agent-01", "claim one").id
        n2 = ops.cmd_create_node(self.tmp, "agent-02", "claim two").id
        e1 = ops.cmd_draw_ground(self.tmp, "agent-01", n1, n2).id

        r_node = ops.cmd_propose_typing(self.tmp, "agent-03", e1, node=n1)
        self.assertTrue(r_node.ok)
        self.assertEqual(r_node.id, "ty1")

        r_label = ops.cmd_propose_typing(self.tmp, "agent-04", e1, label="a free-text typing")
        self.assertTrue(r_label.ok)
        self.assertEqual(r_label.id, "ty2")

        graph = queries.load_graph(self.tmp)
        edge = next(e for e in graph["ground_edges"] if e["id"] == e1)
        self.assertEqual(len(edge["typings"]), 2)
        self.assertEqual(edge["typings"][0]["node"], n1)
        self.assertIsNone(edge["typings"][0]["label"])
        self.assertEqual(edge["typings"][1]["label"], "a free-text typing")
        self.assertIsNone(edge["typings"][1]["node"])

    def test_primary_typing_resolves_to_trunk_node_title_via_get_node(self):
        n1 = ops.cmd_create_node(self.tmp, "agent-01", "claim one", title="Trunk Title").id
        n2 = ops.cmd_create_node(self.tmp, "agent-02", "claim two").id
        e1 = ops.cmd_draw_ground(self.tmp, "agent-01", n1, n2).id
        ops.cmd_propose_typing(self.tmp, "agent-03", e1, node=n1)

        graph = queries.load_graph(self.tmp)
        rec = queries.get_node(graph, n1)
        dep = rec["dependents"][0]
        self.assertEqual(dep["primary_typing"], "ty1")
        self.assertEqual(dep["primary_typing_text"], "Trunk Title")

    def test_primary_typing_resolves_to_label_text_when_no_node_ref(self):
        n1 = ops.cmd_create_node(self.tmp, "agent-01", "claim one").id
        n2 = ops.cmd_create_node(self.tmp, "agent-02", "claim two").id
        e1 = ops.cmd_draw_ground(self.tmp, "agent-01", n1, n2).id
        ops.cmd_propose_typing(self.tmp, "agent-03", e1, label="analogical support")

        graph = queries.load_graph(self.tmp)
        rec = queries.get_node(graph, n1)
        dep = rec["dependents"][0]
        self.assertEqual(dep["primary_typing_text"], "analogical support")

    def test_comment_count_on_node_and_edge_and_meta(self):
        n1 = ops.cmd_create_node(self.tmp, "agent-01", "claim one").id
        n2 = ops.cmd_create_node(self.tmp, "agent-02", "claim two").id
        e1 = ops.cmd_draw_ground(self.tmp, "agent-01", n1, n2).id
        ops.cmd_comment(self.tmp, "agent-02", target=n1, text="on the node")
        ops.cmd_comment(self.tmp, "agent-02", target=e1, text="on the edge")
        ops.cmd_comment(self.tmp, "agent-03", target=e1, text="another on the edge")

        graph = queries.load_graph(self.tmp)
        self.assertEqual(graph["meta"]["comment_count"], 3)
        node_rec = queries.get_node(graph, n1)
        self.assertEqual(node_rec["node"]["comment_count"], 1)
        # comment_count on a bare ground_edges record is only computed by the
        # read-verb augmentation (get-node/neighborhood); check it there.
        dep = next(e for e in node_rec["dependents"] if e["id"] == e1)
        self.assertEqual(dep["comment_count"], 2)


# ---------------------------------------------------------------------------
# determinism with forums present
# ---------------------------------------------------------------------------

class DeterminismForumsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_rebuild_is_byte_stable_with_comments_and_typings(self):
        n1 = ops.cmd_create_node(self.tmp, "agent-01", "claim one").id
        n2 = ops.cmd_create_node(self.tmp, "agent-02", "claim two").id
        e1 = ops.cmd_draw_ground(self.tmp, "agent-01", n1, n2).id
        c1 = ops.cmd_comment(self.tmp, "agent-02", target=n1, text="root").id
        ops.cmd_comment(self.tmp, "agent-01", reply_to=c1, text="reply")
        ops.cmd_propose_typing(self.tmp, "agent-02", e1, node=n1)
        ops.cmd_agree(self.tmp, "agent-03", f"comment:{c1}")

        before = (self.tmp / "graph.json").read_text()
        ops.rebuild(self.tmp)
        after = (self.tmp / "graph.json").read_text()
        self.assertEqual(before, after)
        ops.rebuild(self.tmp)
        after2 = (self.tmp / "graph.json").read_text()
        self.assertEqual(after, after2)

    def test_fold_plus_serialize_is_byte_stable_across_runs_with_forums(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": "TA"}),
            ev(2, "a2", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a1", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            ev(4, "a2", "comment", {"id": "c001", "target": "n001", "parent": None, "text": "root"}),
            ev(5, "a1", "comment", {"id": "c002", "target": "n001", "parent": "c001", "text": "reply"}),
            ev(6, "a2", "propose_typing", {"id": "ty1", "edge": "e001", "node": "n001", "label": None}),
            ev(7, "a1", "agree", {"target": "comment:c001"}),
            ev(8, "a2", "agree", {"target": "typing:e001:ty1"}),
        ]
        outputs = [json.dumps(to_graph_json(fold(events)), sort_keys=True, indent=2) for _ in range(5)]
        self.assertEqual(len(set(outputs)), 1, "rebuild must be byte-for-byte deterministic with forums present")


# ---------------------------------------------------------------------------
# CLI-level smoke tests (subprocess), matching test_cli.py's style
# ---------------------------------------------------------------------------

def run(data_dir, *args):
    cmd = [sys.executable, str(GRAPH_PY), *args, "--data", str(data_dir), "--json"]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(V0_DIR))


class CliForumsSmokeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_comment_reply_typing_agree_end_to_end_via_cli(self):
        r = run(self.tmp, "create-node", "--agent", "agent-01", "--text", "claim one placeholder")
        n1 = json.loads(r.stdout)["id"]
        r = run(self.tmp, "create-node", "--agent", "agent-02", "--text", "claim two placeholder")
        n2 = json.loads(r.stdout)["id"]
        r = run(self.tmp, "draw-ground", "--agent", "agent-01", "--from", n1, "--to", n2)
        e1 = json.loads(r.stdout)["id"]

        r = run(self.tmp, "comment", "--agent", "agent-02", "--target", n1, "--text", "root comment")
        self.assertEqual(r.returncode, 0, r.stderr)
        c1 = json.loads(r.stdout)["id"]

        r = run(self.tmp, "comment", "--agent", "agent-01", "--reply-to", c1, "--text", "a reply")
        self.assertEqual(r.returncode, 0, r.stderr)

        r = run(self.tmp, "comment", "--agent", "agent-01", "--target", n1, "--reply-to", c1, "--text", "bad")
        self.assertEqual(r.returncode, 1)  # mutually exclusive

        r = run(self.tmp, "agree", "--agent", "agent-03", "--target", f"comment:{c1}")
        self.assertEqual(r.returncode, 0, r.stderr)

        r = run(self.tmp, "agree", "--agent", "agent-02", "--target", f"comment:{c1}")
        self.assertEqual(r.returncode, 1)  # self-agree rejected

        r = run(self.tmp, "propose-typing", "--agent", "agent-02", "--edge", e1, "--node", n1)
        self.assertEqual(r.returncode, 0, r.stderr)
        ty1 = json.loads(r.stdout)["id"]

        r = run(self.tmp, "propose-typing", "--agent", "agent-03", "--edge", e1, "--label", "free text")
        self.assertEqual(r.returncode, 0, r.stderr)

        r = run(self.tmp, "propose-typing", "--agent", "agent-02", "--edge", e1)
        self.assertEqual(r.returncode, 1)  # neither --node nor --label

        r = run(self.tmp, "agree", "--agent", "agent-04", "--target", f"typing:{e1}:{ty1}")
        self.assertEqual(r.returncode, 0, r.stderr)

        r = run(self.tmp, "list-comments", "--target", n1)
        self.assertEqual(r.returncode, 0, r.stderr)
        payload = json.loads(r.stdout)
        self.assertEqual(len(payload["comments"]), 2)

        r = run(self.tmp, "get-node", n1)
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        # n1 has 2 comments: the root comment and its reply (a reply's target
        # is inherited from its parent, so both land on n1, not on the reply
        # attempt that was rejected for supplying both --target and --reply-to).
        self.assertEqual(rec["node"]["comment_count"], 2)
        self.assertEqual(rec["dependents"][0]["primary_typing"], ty1)

        r = run(self.tmp, "neighborhood", "--node", n1, "--depth", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        edge_rec = next(e for e in rec["edges"] if e["id"] == e1)
        self.assertEqual(edge_rec["primary_typing"], ty1)
        node_rec = next(n for n in rec["nodes"] if n["id"] == n1)
        self.assertEqual(node_rec["comment_count"], 2)

        r = run(self.tmp, "rebuild")
        self.assertEqual(r.returncode, 0, r.stderr)
        graph = json.loads((self.tmp / "graph.json").read_text())
        self.assertEqual(graph["meta"]["comment_count"], 2)

    def test_help_documents_new_verbs(self):
        r = subprocess.run([sys.executable, str(GRAPH_PY), "--help"], capture_output=True, text=True,
                            cwd=str(V0_DIR))
        self.assertEqual(r.returncode, 0)
        for verb in ("comment", "list-comments", "propose-typing"):
            self.assertIn(verb, r.stdout)

    def test_comment_missing_target_rejected_via_cli(self):
        r = run(self.tmp, "comment", "--agent", "agent-01", "--target", "n999", "--text", "x")
        self.assertEqual(r.returncode, 1)
        self.assertFalse(json.loads(r.stdout)["ok"])

    def test_comment_requires_target_or_reply_to_via_cli(self):
        r = run(self.tmp, "comment", "--agent", "agent-01", "--text", "x")
        self.assertEqual(r.returncode, 1)
        self.assertFalse(json.loads(r.stdout)["ok"])

    def test_propose_typing_bad_node_ref_rejected_via_cli(self):
        r = run(self.tmp, "create-node", "--agent", "agent-01", "--text", "claim one placeholder")
        n1 = json.loads(r.stdout)["id"]
        r = run(self.tmp, "create-node", "--agent", "agent-02", "--text", "claim two placeholder")
        n2 = json.loads(r.stdout)["id"]
        r = run(self.tmp, "draw-ground", "--agent", "agent-01", "--from", n1, "--to", n2)
        e1 = json.loads(r.stdout)["id"]
        r = run(self.tmp, "propose-typing", "--agent", "agent-02", "--edge", e1, "--node", "n999")
        self.assertEqual(r.returncode, 1)
        self.assertFalse(json.loads(r.stdout)["ok"])

    def test_list_comments_unknown_target_errors(self):
        r = run(self.tmp, "list-comments", "--target", "n999")
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
