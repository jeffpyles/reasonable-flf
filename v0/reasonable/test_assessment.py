"""Tests for the validated assessment stack (reasonable/assessment.py).

Controlled fixtures prove each component does what the research claimed:
  - calibration down-weights anchor-failing raters and recovers truth under a
    biased majority (the defense align-to-consensus / plain mean cannot give);
  - camp-detection recovers a planted belief split and its between-camp diagnostic;
  - camp_contested flags the nodes the camps disagree on (not raw-stdev);
  - the certainty guardrail fires on a flip / over-hardened verdict and stays quiet
    on a warranted one;
  - everything is deterministic (no RNG) -- same input, same output.
"""
import unittest

from reasonable import assessment as A


def state(matrix):
    """matrix: {node: {agent: value}} -> a minimal fold state for dim A."""
    return {"ratings": {n: {"A": dict(cell)} for n, cell in matrix.items()}}


def compute_state(matrix):
    """A minimal state assess.compute() accepts (empty structural collections;
    agents come from the ratings)."""
    return {"node_order": [], "nodes": {}, "edge_order": [], "edges": {},
            "comment_order": [], "comments": {},
            "ratings": {n: {"A": dict(cell)} for n, cell in matrix.items()}}


class TestCalibration(unittest.TestCase):
    def setUp(self):
        # 4 anchors (spread truth) + 2 targets; 3 honest raters + 4 biased-flat (rate everything 5).
        self.truth = {"n001": 5.0, "n002": 0.0, "n003": 2.5, "n004": 4.0}
        target_truth = {"n005": 1.0, "n006": 4.0}
        all_truth = {**self.truth, **target_truth}
        m = {n: {} for n in all_truth}
        for i in range(3):                        # honest: track truth closely
            a = f"hon{i}"
            for n, t in all_truth.items():
                m[n][a] = max(0.0, min(5.0, t + (0.1 if i == 1 else -0.1 if i == 2 else 0.0)))
        for i in range(4):                        # biased majority: rate everything 5 (fail anchors)
            a = f"bad{i}"
            for n in all_truth:
                m[n][a] = 5.0
        self.m = m
        self.target_truth = target_truth

    def test_anchor_failers_are_downweighted(self):
        cal = A.calibrated_consensus(state(self.m), self.truth)
        w_hon = cal["raters"]["hon0"][3]
        w_bad = cal["raters"]["bad0"][3]
        self.assertGreater(w_hon, 5 * w_bad, "honest rater must vastly outweigh an anchor-failer")

    def test_calibration_beats_plain_mean_under_biased_majority(self):
        cal = A.calibrated_consensus(state(self.m), self.truth)
        for n, t in self.target_truth.items():
            plain = sum(self.m[n].values()) / len(self.m[n])
            calib = cal["consensus"][n]
            self.assertLess(abs(calib - t), abs(plain - t),
                            f"{n}: calibrated {calib:.2f} should beat plain mean {plain:.2f} vs truth {t}")

    def test_compute_aggregate_uses_calibration_when_anchored(self):
        from reasonable import assess
        cal = A.calibrated_consensus(state(self.m), self.truth)["consensus"]
        out = assess.compute(compute_state(self.m), anchors=self.truth)
        agg = {t: mean for (t, d), (mean, _n) in out["aggregate"].items() if d == "A"}
        for n in self.target_truth:
            self.assertAlmostEqual(agg[n], cal[n], places=9,
                                   msg=f"{n}: node-A aggregate must be the calibrated consensus")

    def test_compute_aggregate_unchanged_without_anchors(self):
        from reasonable import assess
        out = assess.compute(compute_state(self.m))          # no anchors -> True_R-weighted
        agg = {t: mean for (t, d), (mean, _n) in out["aggregate"].items() if d == "A"}
        cal = A.calibrated_consensus(state(self.m), self.truth)["consensus"]
        # the anchored aggregate down-weights the biased bloc; the unanchored one
        # does not -> they must differ on a bias-bitten target node.
        self.assertNotAlmostEqual(agg["n005"], cal["n005"], places=3)


class TestCampDetection(unittest.TestCase):
    def setUp(self):
        # 12 nodes; camp A (a0..a2) and camp B (b0..b2). Disagree on n001..n006, agree on n007..n012.
        m = {f"n{i:03d}": {} for i in range(1, 13)}
        for i in range(3):
            for k in range(1, 7):
                m[f"n{k:03d}"][f"a{i}"] = 4.5      # camp A high on contested
                m[f"n{k:03d}"][f"b{i}"] = 0.5      # camp B low on contested
            for k in range(7, 13):
                m[f"n{k:03d}"][f"a{i}"] = 3.0      # both agree on settled
                m[f"n{k:03d}"][f"b{i}"] = 3.0
        self.st = state(m)

    def test_recovers_the_split(self):
        camps = A.detect_camps(self.st)
        b = camps["blocs"]
        a_labels = {b[f"a{i}"] for i in range(3)}
        b_labels = {b[f"b{i}"] for i in range(3)}
        self.assertEqual(len(a_labels), 1, "camp A must be one cluster")
        self.assertEqual(len(b_labels), 1, "camp B must be one cluster")
        self.assertNotEqual(a_labels, b_labels, "the two camps must be separated")
        self.assertGreater(camps["split_strength"], 0.5, "a real split should score high")
        self.assertGreater(camps["between_group_fraction"], 0.5,
                           "camp-driven dispersion => high between-group share (valid contested signal)")

    def test_camp_contested_flags_the_disagreed_nodes(self):
        camps = A.detect_camps(self.st)
        contested = {d["node"] for d in A.camp_contested(self.st["ratings"], camps["blocs"], threshold=1.0)}
        self.assertEqual(contested, {f"n{i:03d}" for i in range(1, 7)},
                         "exactly the camps-disagree nodes are contested (not the settled ones)")

    def test_deterministic(self):
        a = A.detect_camps(self.st)
        b = A.detect_camps(self.st)
        self.assertEqual(a["blocs"], b["blocs"])
        self.assertEqual(a["split_strength"], b["split_strength"])


class TestDiscrimination(unittest.TestCase):
    def setUp(self):
        # truth alternates 5/0; a truth-tracker T vs a biased bloc that rates
        # everything ~4.5 (fails the anchors, flat ordering).
        self.truth = {f"n{i:03d}": (5.0 if i % 2 == 1 else 0.0) for i in range(1, 9)}
        m = {n: {} for n in self.truth}
        for n, t in self.truth.items():
            m[n]["T"] = t
            for i in range(5):
                m[n][f"B{i}"] = 4.5
        self.st = state(m)

    def test_anchored_discrimination_ranks_truth_tracker_above_biased_bloc(self):
        d = A.discrimination_scores(self.st, self.truth, min_overlap=4)
        self.assertGreater(d["T"], 0.8, "truth-tracker should score high vs the anchored consensus")
        self.assertLess(d["B0"], 0.65, "a flat/biased bloc rater should score near chance")
        self.assertGreater(d["T"], d["B0"])

    def test_spearman_deterministic_and_signed(self):
        self.assertAlmostEqual(A.spearman([1, 2, 3], [1, 2, 3]), 1.0)
        self.assertAlmostEqual(A.spearman([1, 2, 3], [3, 2, 1]), -1.0)
        self.assertEqual(A.spearman([1, 2, 3], [1, 2, 3]), A.spearman([1, 2, 3], [1, 2, 3]))


class TestCertaintyGuard(unittest.TestCase):
    def setUp(self):
        self.ref_means = {"n001": 3.0, "n002": 2.0, "c1": 3.5, "c2": 2.0}  # leader n001, margin 1.0
        self.ref_sds = {k: 0.1 for k in self.ref_means}
        self.verdict = ["n001", "n002"]
        self.frontier = ["c1", "c2"]

    def test_flip_fires(self):
        cons = {"n001": 1.0, "n002": 4.0, "c1": 2.0, "c2": 3.5}   # leader flipped to n002
        g = A.certainty_guard(cons, self.ref_means, self.ref_sds, self.verdict, self.frontier)
        self.assertTrue(g["fired"])
        self.assertTrue(g["is_flip"])
        self.assertIn("FLIP", g["reason"])

    def test_over_hardening_fires(self):
        cons = {"n001": 5.0, "n002": 0.0, "c1": 3.5, "c2": 2.0}   # same leader, margin 5 >> warranted 1
        g = A.certainty_guard(cons, self.ref_means, self.ref_sds, self.verdict, self.frontier)
        self.assertTrue(g["fired"])
        self.assertFalse(g["is_flip"])
        self.assertIn("verdict-hardening", g["reason"])

    def test_warranted_verdict_quiet(self):
        cons = {"n001": 3.0, "n002": 2.0, "c1": 3.5, "c2": 2.0}   # matches the reference
        g = A.certainty_guard(cons, self.ref_means, self.ref_sds, self.verdict, self.frontier)
        self.assertFalse(g["fired"], f"a warranted verdict must not fire (got {g['reason']})")


class TestCalibrationSpreadGuard(unittest.TestCase):
    """Identifiability guard: a per-rater affine fit is only well-posed when the
    anchor *truths* span the scale. All-settled-high anchors (covid) can't identify
    a slope, so calibration is DECLINED and the caller falls back to raw. The
    validated adversarial defense (spanning anchors, incl. a low truth) is untouched.
    """
    def _matrix(self, truths, targets):
        # 3 honest raters track truth; a 4-strong biased bloc rates everything 5.0.
        all_t = {**truths, **targets}
        m = {n: {} for n in all_t}
        for i in range(3):
            for n, t in all_t.items():
                m[n][f"hon{i}"] = max(0.0, min(5.0, t + (0.1 if i == 1 else -0.1 if i == 2 else 0.0)))
        for i in range(4):
            for n in all_t:
                m[n][f"bad{i}"] = 5.0
        return m

    def test_low_spread_anchors_decline_calibration(self):
        truths = {"n001": 4.1, "n002": 4.3, "n003": 4.5, "n004": 4.6}   # spread 0.5 < 2.0
        cal = A.calibrated_consensus(state(self._matrix(truths, {"n005": 2.0})), truths)
        self.assertFalse(cal["calibrated"])
        self.assertIsNone(cal["consensus"])
        self.assertLess(cal["anchor_spread"], A.MIN_ANCHOR_SPREAD)

    def test_spanning_anchors_engage_calibration(self):
        truths = {"n001": 1.4, "n002": 3.5, "n003": 4.0, "n004": 4.6}   # spread 3.2 >= 2.0
        cal = A.calibrated_consensus(state(self._matrix(truths, {"n005": 2.0})), truths)
        self.assertTrue(cal["calibrated"])
        self.assertIsNotNone(cal["consensus"])
        self.assertGreaterEqual(cal["anchor_spread"], A.MIN_ANCHOR_SPREAD)

    def test_declined_calibration_falls_back_to_raw_byte_identically(self):
        from reasonable import assess
        truths = {"n001": 4.1, "n002": 4.3, "n003": 4.5, "n004": 4.6}   # low spread
        m = self._matrix(truths, {"n005": 2.0})
        raw = assess.compute(compute_state(m))                     # no anchors
        anchored = assess.compute(compute_state(m), anchors=truths)  # guard should decline
        self.assertFalse(anchored["used_calibration"])
        self.assertEqual(raw["aggregate"], anchored["aggregate"],
                         "low-spread anchors must fall back byte-identically to the raw aggregate")

    def test_spanning_anchors_still_defend_against_biased_majority(self):
        # The validated benefit must survive the guard: spanning anchors engage
        # calibration and recover the target truth from a captured plain mean.
        from reasonable import assess
        truths = {"n001": 1.4, "n002": 3.5, "n003": 4.0, "n004": 4.6}
        m = self._matrix(truths, {"n005": 1.0})
        out = assess.compute(compute_state(m), anchors=truths)
        self.assertTrue(out["used_calibration"])
        agg = {t: mean for (t, d), (mean, _n) in out["aggregate"].items() if d == "A"}
        plain = sum(m["n005"].values()) / len(m["n005"])
        self.assertLess(abs(agg["n005"] - 1.0), abs(plain - 1.0),
                        "spanning-anchor calibration must still beat the biased-majority mean")


if __name__ == "__main__":
    unittest.main()
