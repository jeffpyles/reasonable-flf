"""Decomposition routing (SPEC-evidence-argument-ought-ghosts §2.3):
a quorum-met-but-split type poll is an is/ought-conflation decomposition
candidate; resolved and under-quorum polls are not."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from reasonable import decompose, typepoll  # noqa: E402

Q, R = typepoll.DEFAULT_QUORUM, typepoll.DEFAULT_RATIO


def poll(node, yes, no, yes_share):
    n_votes = yes + no
    resolved = n_votes >= Q and yes_share is not None and yes_share >= R
    return {
        "node": node, "question": "type:ought", "yes": yes, "no": no, "decline": 0,
        "n_votes": n_votes, "yes_w": 0.0, "no_w": 0.0, "yes_share": yes_share,
        "resolved": resolved, "resolved_kind": "ought" if resolved else None,
        "reopen_required": False,
    }


class DecomposeRoutingTest(unittest.TestCase):
    def test_only_split_quorum_met_polls_are_candidates(self):
        result = {
            "split|type:ought": poll("n_split", 3, 3, 0.50),      # quorum met, split -> candidate
            "yes|type:ought": poll("n_yes", 5, 0, 1.00),          # resolved yes -> not
            "no|type:ought": poll("n_no", 0, 5, 0.00),            # resolved no  -> not
            "thin|type:ought": poll("n_thin", 2, 1, 0.50),        # split but under quorum -> not
        }
        cands = {c["node"] for c in decompose.decompose_candidates(result)}
        self.assertEqual(cands, {"n_split"})

    def test_band_edges(self):
        # just inside the band (below the Yes threshold) with quorum -> candidate;
        # exactly at/above the ratio resolves Yes -> not a candidate.
        just_below = poll("n_a", 3, 2, R - 0.01)
        at_ratio = poll("n_b", 4, 1, R)
        cands = {c["node"] for c in decompose.decompose_candidates(
            {"a|type:ought": just_below, "b|type:ought": at_ratio})}
        self.assertIn("n_a", cands)
        self.assertNotIn("n_b", cands)

    def test_ought_hint_names_the_value_premise(self):
        c = decompose.decompose_candidates({"s|type:ought": poll("n1", 3, 3, 0.5)})[0]
        self.assertIn("value premise", c["hint"])


if __name__ == "__main__":
    unittest.main()
