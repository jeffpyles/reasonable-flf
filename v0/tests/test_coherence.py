"""Coherence lint (SPEC-evidence-argument-ought-ghosts.md §4 + §3.3 redundant
paths). Deterministic structural pass over graph.json — no ratings involved."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reasonable import queries  # noqa: E402
from reasonable.fold import fold, to_graph_json  # noqa: E402


def ev(seq, agent, verb, payload):
    return {"seq": seq, "ts": f"2026-01-01T00:00:{seq:02d}+00:00", "agent": agent, "verb": verb,
            "payload": payload}


def node(seq, nid, text):
    return ev(seq, "a1", "create_node", {"id": nid, "kind": "claim", "text": text,
                                          "source": None, "title": None})


class CoherenceLintTest(unittest.TestCase):
    def _graph(self, events):
        return to_graph_json(fold(events))

    def test_hub_orphan_malformed_question_negation_redundant(self):
        events = [
            node(1, "n001", "Top answer hub."),
            node(2, "n002", "Ground two."),
            node(3, "n003", "Ground three."),
            node(4, "n004", "Ground four."),
            node(5, "n005", "Ground five (also a shortcut)."),
            node(6, "n006", "Is this a claim?"),          # question-shaped
            node(7, "n007", "No randomized trial exists."),  # negation-framed
            node(8, "n008", "A lonely orphan claim."),     # orphan
            # n002..n005 all ground the hub n001 -> in-degree 4
            ev(9, "a1", "draw_ground", {"id": "e1", "from": "n002", "to": "n001", "group": None}),
            ev(10, "a1", "draw_ground", {"id": "e2", "from": "n003", "to": "n001", "group": None}),
            ev(11, "a1", "draw_ground", {"id": "e3", "from": "n004", "to": "n001", "group": None}),
            ev(12, "a1", "draw_ground", {"id": "e4", "from": "n005", "to": "n001", "group": None}),
            # layered path n005 -> n004 -> n001 makes the direct n005->n001 redundant
            ev(13, "a1", "draw_ground", {"id": "e5", "from": "n005", "to": "n004", "group": None}),
            # a 1-member antithesis set (malformed)
            ev(14, "a1", "add_antithesis", {"set": "s1", "node": "n006"}),
        ]
        rep = queries.coherence_lint(self._graph(events), hub_threshold=4)
        s = rep["summary"]
        self.assertEqual([h["node"] for h in rep["hub_nodes"]], ["n001"])
        self.assertEqual(rep["hub_nodes"][0]["direct_grounds"], 4)
        self.assertIn("n008", rep["orphan_nodes"])
        self.assertEqual(s["malformed_antithesis_sets"], 1)
        self.assertEqual(rep["malformed_antithesis_sets"][0]["set"], "s1")
        self.assertEqual([q["node"] for q in rep["question_shaped_nodes"]], ["n006"])
        self.assertEqual([n["node"] for n in rep["negation_framed_nodes"]], ["n007"])
        self.assertTrue(any(r["edge"] == "e4" for r in rep["redundant_paths"]))
        # n002/n003 are direct-only grounds with no alternate path -> not redundant
        self.assertFalse(any(r["edge"] in ("e1", "e2") for r in rep["redundant_paths"]))

    def test_clean_graph_is_quiet(self):
        events = [
            node(1, "n001", "Conclusion."),
            node(2, "n002", "A supporting reason."),
            ev(3, "a1", "draw_ground", {"id": "e1", "from": "n002", "to": "n001", "group": None}),
        ]
        rep = queries.coherence_lint(self._graph(events), hub_threshold=8)
        self.assertEqual(sum(rep["summary"].values()), 0)


if __name__ == "__main__":
    unittest.main()
