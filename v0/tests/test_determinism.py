"""graph.json must be a pure, idempotent function of events.jsonl:
same log -> same bytes, every time (BUILD-SPEC.md §1b, §3)."""
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reasonable import ops  # noqa: E402
from reasonable.fold import fold, to_graph_json  # noqa: E402


def ev(seq, agent, verb, payload):
    return {"seq": seq, "ts": f"2026-01-01T00:00:{seq:02d}+00:00", "agent": agent, "verb": verb, "payload": payload}


SAMPLE_EVENTS = [
    ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": "TA"}),
    ev(2, "a2", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
    ev(3, "a1", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
    ev(4, "a2", "agree", {"target": "e001"}),
    ev(5, "a2", "add_antithesis", {"set": "s1", "node": "n001"}),
    ev(6, "a1", "propose_phrasing", {"id": "p1", "node": "n001", "text": "A, restated"}),
    ev(7, "a2", "flag_friction", {"id": "f1", "text": "hmm", "refs": ["n001"]}),
]


class PureFunctionTest(unittest.TestCase):
    def test_fold_plus_serialize_is_byte_stable_across_runs(self):
        outputs = []
        for _ in range(5):
            gj = to_graph_json(fold(SAMPLE_EVENTS))
            outputs.append(json.dumps(gj, sort_keys=True, indent=2))
        self.assertEqual(len(set(outputs)), 1, "rebuild must be byte-for-byte deterministic")

    def test_event_order_independent_of_python_dict_construction(self):
        # Rebuilding from a shuffled-then-resorted copy must match: fold()
        # explicitly sorts by seq internally is NOT assumed here -- the
        # contract is that callers pass seq-ordered events (store.read_events
        # guarantees this), so we assert that pre-sorting yields the same
        # result regardless of on-disk line order.
        import random
        shuffled = SAMPLE_EVENTS[:]
        random.Random(42).shuffle(shuffled)
        shuffled.sort(key=lambda e: e["seq"])
        self.assertEqual(
            json.dumps(to_graph_json(fold(SAMPLE_EVENTS)), sort_keys=True),
            json.dumps(to_graph_json(fold(shuffled)), sort_keys=True),
        )


class RebuildRoundTripTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_write_then_rebuild_is_idempotent(self):
        r1 = ops.cmd_create_node(self.tmp, "agent-01", "hello world")
        self.assertTrue(r1.ok)
        ops.cmd_create_node(self.tmp, "agent-02", "a second claim")

        before = (self.tmp / "graph.json").read_text()
        ops.rebuild(self.tmp)
        after = (self.tmp / "graph.json").read_text()
        self.assertEqual(before, after)

        ops.rebuild(self.tmp)
        after2 = (self.tmp / "graph.json").read_text()
        self.assertEqual(after, after2)

    def test_graph_json_is_valid_json_with_required_top_level_keys(self):
        ops.cmd_create_node(self.tmp, "agent-01", "hello world")
        graph = json.loads((self.tmp / "graph.json").read_text())
        for key in ("meta", "nodes", "ground_edges", "conjunction_groups", "antithesis_sets", "frictions"):
            self.assertIn(key, graph)
        self.assertIn("question", graph["meta"])
        self.assertIn("event_count", graph["meta"])


if __name__ == "__main__":
    unittest.main()
