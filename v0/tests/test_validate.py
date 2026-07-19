"""Every validation rule from BUILD-SPEC.md §2, tested directly against the
importable validate.py functions (no CLI/subprocess involved)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reasonable import validate  # noqa: E402
from reasonable.fold import fold  # noqa: E402


def ev(seq, agent, verb, payload):
    return {"seq": seq, "ts": f"2026-01-01T00:00:{seq:02d}+00:00", "agent": agent, "verb": verb, "payload": payload}


def make_node_graph():
    """Two nodes (n001 by agent-01, n002 by agent-02), one edge n001->n002
    authored by agent-01, one antithesis set s1 with n001 (author agent-01),
    one extra title/phrasing on n001 authored by agent-01."""
    events = [
        ev(1, "agent-01", "create_node", {"id": "n001", "kind": "claim", "text": "claim one",
                                           "source": None, "title": "Title One"}),
        ev(2, "agent-02", "create_node", {"id": "n002", "kind": "claim", "text": "claim two",
                                           "source": None, "title": None}),
        ev(3, "agent-01", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
        ev(4, "agent-01", "add_antithesis", {"set": "s1", "node": "n001"}),
    ]
    return fold(events)


class ReferentialIntegrityTest(unittest.TestCase):
    def test_create_node_evidence_requires_source(self):
        state = make_node_graph()
        errors, _ = validate.validate_create_node(state, "agent-03", "evidence", "cited", None, None)
        tags = [t for t, _m in errors]
        self.assertIn("evidence_source", tags)

    def test_create_node_evidence_with_source_ok(self):
        state = make_node_graph()
        errors, _ = validate.validate_create_node(state, "agent-03", "evidence", "cited", "http://x", None)
        self.assertEqual(errors, [])

    def test_create_node_legacy_external_anchor_still_requires_source(self):
        # `external_anchor` is a permanent READ ALIAS for `evidence`: still a
        # valid kind, still source-required (now under the evidence_source tag).
        state = make_node_graph()
        errors, _ = validate.validate_create_node(state, "agent-03", "external_anchor", "cited", None, None)
        tags = [t for t, _m in errors]
        self.assertIn("evidence_source", tags)
        ok, _ = validate.validate_create_node(state, "agent-03", "external_anchor", "cited", "http://x", None)
        self.assertEqual(ok, [])

    def test_create_node_ought_kind_ok_no_source_needed(self):
        state = make_node_graph()
        errors, _ = validate.validate_create_node(state, "agent-03", "ought", "you should X", None, None)
        self.assertEqual(errors, [])

    def test_create_node_invalid_kind_rejected(self):
        state = make_node_graph()
        errors, _ = validate.validate_create_node(state, "agent-03", "nonsense", "x", None, None)
        self.assertTrue(any(t == "invalid_kind" for t, _ in errors))

    def test_draw_ground_hume_rule_ought_may_not_ground_is(self):
        # n003 is an Ought, n001 is a claim: Ought grounding a claim is rejected.
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "eggs raise CVD risk",
                                        "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n003", "kind": "ought", "text": "you should avoid eggs",
                                        "source": None, "title": None}),
        ]
        state = fold(events)
        errors, _ = validate.validate_draw_ground(state, "a2", "n003", "n001", None)
        self.assertTrue(any(t == "hume_violation" for t, _ in errors))

    def test_draw_ground_ought_grounds_ought_allowed(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n003", "kind": "ought", "text": "you should be healthy",
                                        "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n004", "kind": "ought", "text": "you should avoid eggs",
                                        "source": None, "title": None}),
        ]
        state = fold(events)
        errors, _ = validate.validate_draw_ground(state, "a2", "n004", "n003", None)
        self.assertEqual([t for t, _ in errors], [])

    def test_draw_ground_into_evidence_warns(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "a claim",
                                        "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "evidence", "text": "a study finding",
                                        "source": "http://x", "title": None}),
        ]
        state = fold(events)
        errors, warnings = validate.validate_draw_ground(state, "a2", "n001", "n002", None)
        self.assertEqual([t for t, _ in errors], [])
        self.assertTrue(any(t == "evidence_grounded" for t, _ in warnings))

    def test_supersede_target_and_restore_guard(self):
        state = make_node_graph()  # n001, n002, edge e001
        errs, _ = validate.validate_supersede(state, "a3", "n999", "demote")
        self.assertTrue(any(t == "missing_ref" for t, _ in errs))
        # demoting an existing node, edge, or antithesis set is fine
        self.assertEqual(validate.validate_supersede(state, "a3", "n001", "demote")[0], [])
        self.assertEqual(validate.validate_supersede(state, "a3", "e001", "demote")[0], [])
        self.assertEqual(validate.validate_supersede(state, "a3", "s1", "demote")[0], [])  # set
        # restoring something not currently demoted is rejected
        errs2, _ = validate.validate_supersede(state, "a3", "n001", "restore")
        self.assertTrue(any(t == "not_demoted" for t, _ in errs2))
        # bad action
        errs3, _ = validate.validate_supersede(state, "a3", "n001", "nonsense")
        self.assertTrue(any(t == "invalid_action" for t, _ in errs3))

    def test_flag_type_valid_and_invalid(self):
        state = make_node_graph()
        ok, _ = validate.validate_flag_type(state, "a2", "n001", "ought")
        self.assertEqual(ok, [])
        bad_node, _ = validate.validate_flag_type(state, "a2", "n999", "ought")
        self.assertTrue(any(t == "missing_ref" for t, _ in bad_node))
        bad_kind, _ = validate.validate_flag_type(state, "a2", "n001", "claim")
        self.assertTrue(any(t == "invalid_flag_type" for t, _ in bad_kind))

    def test_draw_ground_missing_from_node(self):
        state = make_node_graph()
        errors, _ = validate.validate_draw_ground(state, "agent-03", "n999", "n002", None)
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))

    def test_draw_ground_missing_to_node(self):
        state = make_node_graph()
        errors, _ = validate.validate_draw_ground(state, "agent-03", "n001", "n999", None)
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))

    def test_draw_ground_self_loop_rejected(self):
        state = make_node_graph()
        errors, _ = validate.validate_draw_ground(state, "agent-03", "n001", "n001", None)
        self.assertTrue(any(t == "self_ground" for t, _ in errors))

    def test_draw_ground_multi_node_cycle_allowed(self):
        # A -> B -> C -> A is three separate draw-ground calls, each of which
        # individually validates fine (no self-loop). Simulate the sequence.
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a1", "create_node", {"id": "n003", "kind": "claim", "text": "C", "source": None, "title": None}),
            ev(4, "a2", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            ev(5, "a2", "draw_ground", {"id": "e002", "from": "n002", "to": "n003", "group": None}),
        ]
        state = fold(events)
        # closing the cycle: n003 -> n001
        errors, _ = validate.validate_draw_ground(state, "a2", "n003", "n001", None)
        self.assertEqual(errors, [], "multi-node cycles must be ALLOWED per BUILD-SPEC.md rule 4")

    def test_draw_ground_group_conflict(self):
        # g1 already targets n002; joining g1 while targeting n003 must be rejected.
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a1", "create_node", {"id": "n003", "kind": "claim", "text": "C", "source": None, "title": None}),
            ev(4, "a2", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": "g1"}),
        ]
        state = fold(events)
        errors, _ = validate.validate_draw_ground(state, "a2", "n003", "n003", "g1")
        self.assertTrue(any(t == "group_conflict" for t, _ in errors))
        self.assertTrue(any(t == "self_ground" for t, _ in errors))

    def test_draw_ground_group_join_same_target_ok(self):
        events = [
            ev(1, "a1", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "a1", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "a1", "create_node", {"id": "n003", "kind": "claim", "text": "C", "source": None, "title": None}),
            ev(4, "a2", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": "g1"}),
        ]
        state = fold(events)
        errors, _ = validate.validate_draw_ground(state, "a2", "n003", "n002", "g1")
        self.assertEqual(errors, [])

    def test_add_antithesis_duplicate_membership_rejected(self):
        state = make_node_graph()
        errors, _ = validate.validate_add_antithesis(state, "agent-01", "n001", "s1")
        self.assertTrue(any(t == "duplicate_set_membership" for t, _ in errors))

    def test_add_antithesis_unknown_set_rejected(self):
        state = make_node_graph()
        errors, _ = validate.validate_add_antithesis(state, "agent-01", "n002", "s999")
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))

    def test_flag_friction_unknown_ref_rejected(self):
        state = make_node_graph()
        errors, _ = validate.validate_flag_friction(state, "agent-03", "text", ["n999"])
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))


class SelfAgreeAndDuplicateAgreeTest(unittest.TestCase):
    def test_self_agree_on_edge_rejected(self):
        state = make_node_graph()
        errors, _ = validate.validate_agree(state, "agent-01", "e001")  # agent-01 drew e001
        self.assertTrue(any(t == "self_agree" for t, _ in errors))

    def test_self_agree_on_node_own_phrasing_rejected(self):
        state = make_node_graph()
        errors, _ = validate.validate_agree(state, "agent-01", "phrasing:n001:p0")
        self.assertTrue(any(t == "self_agree" for t, _ in errors))

    def test_self_agree_on_own_title_rejected(self):
        state = make_node_graph()
        errors, _ = validate.validate_agree(state, "agent-01", "title:n001:t0")
        self.assertTrue(any(t == "self_agree" for t, _ in errors))

    def test_self_agree_on_own_antithesis_membership_rejected(self):
        state = make_node_graph()
        errors, _ = validate.validate_agree(state, "agent-01", "set:s1:n001")
        self.assertTrue(any(t == "self_agree" for t, _ in errors))

    def test_agree_by_other_agent_ok(self):
        state = make_node_graph()
        errors, _ = validate.validate_agree(state, "agent-02", "e001")
        self.assertEqual(errors, [])

    def test_duplicate_agree_rejected(self):
        events = [
            ev(1, "agent-01", "create_node", {"id": "n001", "kind": "claim", "text": "A", "source": None, "title": None}),
            ev(2, "agent-02", "create_node", {"id": "n002", "kind": "claim", "text": "B", "source": None, "title": None}),
            ev(3, "agent-01", "draw_ground", {"id": "e001", "from": "n001", "to": "n002", "group": None}),
            ev(4, "agent-03", "agree", {"target": "e001"}),
        ]
        state = fold(events)
        errors, _ = validate.validate_agree(state, "agent-03", "e001")
        self.assertTrue(any(t == "duplicate_agree" for t, _ in errors))

    def test_agree_on_unknown_target_rejected(self):
        state = make_node_graph()
        errors, _ = validate.validate_agree(state, "agent-02", "e999")
        self.assertTrue(any(t == "missing_ref" for t, _ in errors))


class SoftCapAndDuplicateTextTest(unittest.TestCase):
    def test_over_cap_is_warning_not_error(self):
        state = make_node_graph()
        long_text = "x" * 400
        errors, warnings = validate.validate_create_node(state, "agent-03", "claim", long_text, None, None,
                                                           max_claim_chars=350)
        self.assertEqual(errors, [], "over-cap must be a WARNING, not an error (BUILD-SPEC.md rule 5)")
        self.assertTrue(any(t == "over_cap" for t, _ in warnings))

    def test_under_cap_no_warning(self):
        state = make_node_graph()
        errors, warnings = validate.validate_create_node(state, "agent-03", "claim", "short", None, None,
                                                           max_claim_chars=350)
        self.assertEqual(errors, [])
        self.assertFalse(any(t == "over_cap" for t, _ in warnings))

    def test_duplicate_text_warning_on_create_node(self):
        state = make_node_graph()
        errors, warnings = validate.validate_create_node(state, "agent-03", "claim", "claim one", None, None)
        self.assertEqual(errors, [])
        self.assertTrue(any(t == "duplicate_text" for t, _ in warnings))

    def test_duplicate_text_warning_is_case_and_whitespace_insensitive(self):
        state = make_node_graph()
        errors, warnings = validate.validate_create_node(state, "agent-03", "claim", "  CLAIM   ONE  ", None, None)
        self.assertTrue(any(t == "duplicate_text" for t, _ in warnings))

    def test_duplicate_text_warning_on_propose_phrasing(self):
        state = make_node_graph()
        errors, warnings = validate.validate_propose_phrasing(state, "agent-02", "n002", "claim one")
        self.assertEqual(errors, [])
        self.assertTrue(any(t == "duplicate_text" for t, _ in warnings))

    def test_no_duplicate_warning_for_novel_text(self):
        state = make_node_graph()
        _errors, warnings = validate.validate_create_node(state, "agent-03", "claim", "something totally new",
                                                            None, None)
        self.assertFalse(any(t == "duplicate_text" for t, _ in warnings))


if __name__ == "__main__":
    unittest.main()
