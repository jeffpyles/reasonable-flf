"""Fold correctness + strength math (BUILD-SPEC.md §1, §4a)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reasonable.fold import fold, to_graph_json  # noqa: E402


def ev(seq, agent, verb, payload, ts=None):
    return {"seq": seq, "ts": ts or f"2026-01-01T00:00:{seq:02d}+00:00", "agent": agent, "verb": verb,
            "payload": payload}


class FoldBasicsTest(unittest.TestCase):
    def test_create_node_becomes_phrasing_p0(self):
        events = [ev(1, "agent-01", "create_node", {"id": "n001", "kind": "claim", "text": "hello",
                                                      "source": None, "title": None})]
        state = fold(events)
        gj = to_graph_json(state)
        self.assertEqual(len(gj["nodes"]), 1)
        node = gj["nodes"][0]
        self.assertEqual(node["id"], "n001")
        # the assessment layer enriches each phrasing with a `scores` block (R/C
        # aggregates -- ASSESSMENT-SPEC §5); assert the structural fields plus its presence.
        self.assertEqual(len(node["phrasings"]), 1)
        ph = node["phrasings"][0]
        self.assertEqual({k: ph[k] for k in ("id", "text", "agrees", "agents")},
                         {"id": "p0", "text": "hello", "agrees": 0, "agents": []})
        self.assertIn("scores", ph)
        self.assertEqual(node["primary_phrasing"], "p0")
        self.assertIsNone(node["primary_title"])
        self.assertEqual(node["author"], "agent-01")
        self.assertEqual(node["created_seq"], 1)

    def test_external_anchor_carries_source(self):
        events = [ev(1, "agent-01", "create_node", {"id": "n001", "kind": "external_anchor",
                                                      "text": "cited claim", "source": "http://x", "title": None})]
        gj = to_graph_json(fold(events))
        self.assertEqual(gj["nodes"][0]["source_ref"], "http://x")
        # fold NEVER rewrites a stored kind -- a legacy `external_anchor` log
        # still folds to `external_anchor`, so old graph.json is byte-identical.
        self.assertEqual(gj["nodes"][0]["kind"], "external_anchor")

    def test_evidence_and_ought_kinds_preserved(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "evidence",
                                        "text": "a study finding", "source": "http://x", "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "ought",
                                        "text": "you should X", "source": None, "title": None}),
        ]
        gj = to_graph_json(fold(events))
        kinds = {n["id"]: n["kind"] for n in gj["nodes"]}
        self.assertEqual(kinds["n001"], "evidence")
        self.assertEqual(kinds["n002"], "ought")

    def test_supersede_demotes_restores_and_is_byte_safe(self):
        # SPEC §3.2: demote sets a conditional `demoted` marker; only the
        # demoted target carries it (so undemoted graphs stay byte-identical);
        # restore removes it (latest event wins).
        base = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "x",
                                        "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "y",
                                        "source": None, "title": None}),
        ]
        self.assertNotIn("demoted", to_graph_json(fold(base))["nodes"][0])

        dem = base + [ev(3, "a2", "supersede", {"target": "n001", "action": "demote", "reason": "why"})]
        byid = {n["id"]: n for n in to_graph_json(fold(dem))["nodes"]}
        self.assertEqual(byid["n001"]["demoted"]["reason"], "why")
        self.assertEqual(byid["n001"]["demoted"]["agent"], "a2")
        self.assertNotIn("demoted", byid["n002"])   # untouched node has no marker

        res = dem + [ev(4, "a2", "supersede", {"target": "n001", "action": "restore"})]
        byid2 = {n["id"]: n for n in to_graph_json(fold(res))["nodes"]}
        self.assertNotIn("demoted", byid2["n001"])

    def test_flag_type_creates_no_structural_object(self):
        # SPEC §1: flag_type is recorded in the log but folds to nothing
        # structural in §1 (its poll/graph surface is §2). It must not add or
        # alter any node/edge/set/friction/group -- only the meta counters and
        # the time-relative heat clock advance (as they do for ANY appended
        # event). This is why the three existing graphs, which carry no
        # flag_type events, still rebuild byte-identically.
        base = [ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "x",
                                            "source": None, "title": None})]
        with_flag = base + [ev(2, "a2", "flag_type", {"id": "ft1", "node": "n001", "as": "ought"})]
        gj_base, gj_flag = to_graph_json(fold(base)), to_graph_json(fold(with_flag))
        for section in ("nodes", "ground_edges", "conjunction_groups", "antithesis_sets", "frictions"):
            self.assertEqual(len(gj_base[section]), len(gj_flag[section]), section)
        self.assertEqual([n["id"] for n in gj_flag["nodes"]], ["n001"])

    def test_ground_edge_and_strength_math(self):
        events = [
            ev(1, "agent-01", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "agent-01", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "agent-02", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            ev(4, "agent-03", "agree", {"target": "e001"}),
            ev(5, "agent-04", "agree", {"target": "e001"}),
        ]
        gj = to_graph_json(fold(events))
        edge = gj["ground_edges"][0]
        self.assertEqual(edge["from"], "n001")
        self.assertEqual(edge["to"], "n002")
        self.assertEqual(edge["agrees"], 2)
        # strength = agrees + 1 (author counts as one) -- FROZEN convention.
        self.assertEqual(edge["strength"], 3)
        self.assertEqual(sorted(edge["agents"]), ["agent-03", "agent-04"])

    def test_conjunction_group_collects_members(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a1", "create_node", {"id": "n003", "kind": "claim", "text": "C", "source": None, "title": None}),
            ev(4, "a2", "draw_ground", {"id": "e001", "from": "n001", "to": "n003", "group": "g1"}),
            ev(5, "a2", "draw_ground", {"id": "e002", "from": "n002", "to": "n003", "group": "g1"}),
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(len(gj["conjunction_groups"]), 1)
        group = gj["conjunction_groups"][0]
        self.assertEqual(group["id"], "g1")
        self.assertEqual(group["to"], "n003")
        self.assertEqual(group["members"], ["n001", "n002"])

    def test_antithesis_belonging_math(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a2", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a1", "add_antithesis", {"set": "s1", "node": "n001"}),
            ev(4, "a1", "add_antithesis", {"set": "s1", "node": "n002"}),
            ev(5, "a3", "agree", {"target": "set:s1:n002"}),
        ]
        gj = to_graph_json(fold(events))
        s = gj["antithesis_sets"][0]
        by_node = {m["node"]: m for m in s["members"]}
        self.assertEqual(by_node["n001"]["agrees"], 0)
        self.assertEqual(by_node["n001"]["belonging"], 1)
        self.assertEqual(by_node["n002"]["agrees"], 1)
        self.assertEqual(by_node["n002"]["belonging"], 2)
        self.assertEqual(by_node["n001"]["author"], "a1")

    def test_primary_phrasing_tie_break_is_earliest(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "first", "source": None, "title": None}),
            ev(2, "a1", "propose_phrasing", {"id": "p1", "node": "n001", "text": "second"}),
            # both p0 and p1 stay at 0 agrees -> earliest (p0) wins.
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(gj["nodes"][0]["primary_phrasing"], "p0")

    def test_primary_phrasing_prefers_higher_agrees(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "first", "source": None, "title": None}),
            ev(2, "a1", "propose_phrasing", {"id": "p1", "node": "n001", "text": "second"}),
            ev(3, "a2", "agree", {"target": "phrasing:n001:p1"}),
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(gj["nodes"][0]["primary_phrasing"], "p1")

    def test_friction_record(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "flag_friction", {"id": "f1", "text": "couldn't express X", "refs": ["n001"]}),
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(len(gj["frictions"]), 1)
        f = gj["frictions"][0]
        self.assertEqual(f["id"], "f1")
        self.assertEqual(f["agent"], "a1")
        self.assertEqual(f["refs"], ["n001"])

    def test_meta_generated_ts_is_last_event_ts_not_wallclock(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None},
               ts="2020-01-01T00:00:00+00:00"),
        ]
        gj = to_graph_json(fold(events))
        self.assertEqual(gj["meta"]["generated_ts"], "2020-01-01T00:00:00+00:00")
        self.assertEqual(gj["meta"]["event_count"], 1)

    def test_empty_log_yields_empty_graph(self):
        gj = to_graph_json(fold([]))
        self.assertEqual(gj["nodes"], [])
        self.assertEqual(gj["ground_edges"], [])
        self.assertEqual(gj["meta"]["event_count"], 0)
        self.assertIsNone(gj["meta"]["generated_ts"])


if __name__ == "__main__":
    unittest.main()
