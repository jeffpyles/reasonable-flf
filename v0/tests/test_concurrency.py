"""Concurrency safety for multi-agent writes (BUILD-SPEC.md ## Amendments;
Feature Discussions Entry 15's "concurrency-safe writes" limitation).

Drives the actual `graph.py` CLI via subprocess from multiple OS processes,
all writing into ONE shared data dir at the same time, and checks that the
file-lock-guarded critical section in reasonable/store.py's `locked()` (used
by every reasonable/ops.py `cmd_*`) actually serializes them: no lost event,
no duplicated seq, no interleaved/torn line in events.jsonl, and `rebuild`
stays byte-for-byte deterministic afterward.
"""
from __future__ import annotations

import json
import multiprocessing
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

V0_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
GRAPH_PY = V0_DIR / "graph.py"

NUM_WORKERS = 8
WRITES_PER_WORKER = 25
TOTAL_WRITES = NUM_WORKERS * WRITES_PER_WORKER


def _worker(args):
    """Run in a separate OS process: perform WRITES_PER_WORKER create-node
    calls against the shared data dir via subprocess (the CLI's real entry
    point), and hand back every invocation's (returncode, stdout, stderr)
    for the parent to assert on."""
    worker_id, data_dir = args
    results = []
    for i in range(WRITES_PER_WORKER):
        cmd = [
            sys.executable, str(GRAPH_PY), "create-node",
            "--agent", f"agent-w{worker_id}",
            "--text", f"concurrent claim from worker {worker_id} #{i}",
            "--data", str(data_dir), "--json",
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(V0_DIR))
        results.append((proc.returncode, proc.stdout, proc.stderr))
    return results


class ConcurrentWritesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_eight_workers_200_writes_serialize_cleanly(self):
        ctx = multiprocessing.get_context("fork" if hasattr(os, "fork") else "spawn")
        with ctx.Pool(processes=NUM_WORKERS) as pool:
            all_results = pool.map(_worker, [(w, self.tmp) for w in range(NUM_WORKERS)])

        # Every individual CLI invocation must have succeeded cleanly -- no
        # tracebacks, no lock timeouts, no rejected writes.
        flat = [r for worker_results in all_results for r in worker_results]
        self.assertEqual(len(flat), TOTAL_WRITES)
        node_ids = []
        for returncode, stdout, stderr in flat:
            self.assertEqual(returncode, 0, f"nonzero exit: stdout={stdout!r} stderr={stderr!r}")
            self.assertNotIn("Traceback", stderr, f"CLI raised an exception: {stderr}")
            payload = json.loads(stdout)
            self.assertTrue(payload["ok"], payload)
            node_ids.append(payload["id"])

        self.assertEqual(len(set(node_ids)), TOTAL_WRITES, "every created node id must be distinct")

        # Exactly 200 events, one well-formed JSON object per line -- no lost
        # writes and no interleaved/torn lines from racing appends.
        events_path = self.tmp / "events.jsonl"
        lines = events_path.read_text().splitlines()
        self.assertEqual(len(lines), TOTAL_WRITES)
        events = [json.loads(line) for line in lines]  # raises if any line is torn/corrupt

        seqs = [e["seq"] for e in events]
        self.assertEqual(
            sorted(seqs), list(range(1, TOTAL_WRITES + 1)),
            "seq values must be exactly 1..N, each used exactly once (no duplicate/skipped seq)",
        )
        self.assertEqual(
            seqs, sorted(seqs),
            "seq must be strictly increasing in on-disk (append) order",
        )

        # rebuild must stay deterministic/idempotent even after concurrent
        # writers touched the log (BUILD-SPEC.md §3).
        before = (self.tmp / "graph.json").read_text()
        r = subprocess.run(
            [sys.executable, str(GRAPH_PY), "rebuild", "--data", str(self.tmp), "--json"],
            capture_output=True, text=True, cwd=str(V0_DIR),
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        after = (self.tmp / "graph.json").read_text()
        self.assertEqual(before, after, "rebuild must be byte-for-byte deterministic")

        r2 = subprocess.run(
            [sys.executable, str(GRAPH_PY), "rebuild", "--data", str(self.tmp), "--json"],
            capture_output=True, text=True, cwd=str(V0_DIR),
        )
        self.assertEqual(r2.returncode, 0, r2.stderr)
        after2 = (self.tmp / "graph.json").read_text()
        self.assertEqual(after, after2, "repeated rebuild must reproduce identical bytes")

        graph = json.loads(after)
        self.assertEqual(graph["meta"]["event_count"], TOTAL_WRITES)
        self.assertEqual(len(graph["nodes"]), TOTAL_WRITES)


if __name__ == "__main__":
    unittest.main()
