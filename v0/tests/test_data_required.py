"""`--data` is now required on every verb, read or write (BUILD-SPEC.md
## Amendments, v0.1) -- omitting it must be a clear argparse error
(SystemExit, code 2, with a specific message), not a silent fallback to
some default graph directory. See Feature Discussions Entry 16 (the
operational finding that agents forgetting `--data` wrote into the wrong
shared graph)."""
from __future__ import annotations

import contextlib
import io
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import graph  # noqa: E402


class DataRequiredTest(unittest.TestCase):
    def _run_expect_system_exit(self, argv):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as cm:
                graph.main(argv)
        return cm.exception, stderr.getvalue()

    def test_read_verb_without_data_errors(self):
        exc, err = self._run_expect_system_exit(["stats"])
        self.assertEqual(exc.code, 2)
        self.assertIn("--data is required", err)

    def test_another_read_verb_without_data_errors(self):
        exc, err = self._run_expect_system_exit(["search", "anything"])
        self.assertEqual(exc.code, 2)
        self.assertIn("--data is required", err)

    def test_write_verb_without_data_errors(self):
        exc, err = self._run_expect_system_exit(
            ["create-node", "--agent", "agent-01", "--text", "x"]
        )
        self.assertEqual(exc.code, 2)
        self.assertIn("--data is required", err)

    def test_another_write_verb_without_data_errors(self):
        exc, err = self._run_expect_system_exit(
            ["flag-friction", "--agent", "agent-01", "--text", "x"]
        )
        self.assertEqual(exc.code, 2)
        self.assertIn("--data is required", err)


if __name__ == "__main__":
    unittest.main()
