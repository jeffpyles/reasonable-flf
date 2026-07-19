"""End-to-end smoke test of the actual `graph.py` CLI (argparse wiring,
--json output, exit codes) via subprocess -- not just the importable
functions. Keeps most detailed coverage in test_fold.py / test_validate.py;
this file just proves the CLI surface matches BUILD-SPEC.md §2."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

V0_DIR = Path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
GRAPH_PY = V0_DIR / "graph.py"


def run(data_dir, *args):
    cmd = [sys.executable, str(GRAPH_PY), *args, "--data", str(data_dir), "--json"]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=str(V0_DIR))


class CliSmokeTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def test_create_node_agree_get_node_stats_rebuild(self):
        r = run(self.tmp, "create-node", "--agent", "agent-01", "--text", "eggs are a claim placeholder")
        self.assertEqual(r.returncode, 0, r.stderr)
        n1 = json.loads(r.stdout)["id"]
        self.assertTrue(n1.startswith("n"))

        r = run(self.tmp, "create-node", "--agent", "agent-02", "--text", "another placeholder claim")
        n2 = json.loads(r.stdout)["id"]

        r = run(self.tmp, "draw-ground", "--agent", "agent-01", "--from", n1, "--to", n2)
        self.assertEqual(r.returncode, 0, r.stderr)
        eid = json.loads(r.stdout)["id"]

        r = run(self.tmp, "agree", "--agent", "agent-02", "--target", eid)
        self.assertEqual(r.returncode, 0, r.stderr)

        # self-agree must be rejected with nonzero exit
        r = run(self.tmp, "agree", "--agent", "agent-01", "--target", eid)
        self.assertEqual(r.returncode, 1)
        self.assertFalse(json.loads(r.stdout)["ok"])

        r = run(self.tmp, "get-node", n1)
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["node"]["id"], n1)
        self.assertEqual(len(rec["dependents"]), 1)

        r = run(self.tmp, "stats")
        self.assertEqual(r.returncode, 0, r.stderr)
        st = json.loads(r.stdout)
        self.assertEqual(st["counts"]["nodes"], 2)
        self.assertEqual(st["health"]["self_agree_rejected"], 1)

        r = run(self.tmp, "rebuild")
        self.assertEqual(r.returncode, 0, r.stderr)

        graph = json.loads((self.tmp / "graph.json").read_text())
        self.assertEqual(len(graph["nodes"]), 2)
        self.assertEqual(graph["ground_edges"][0]["strength"], 2)

    def test_grammar_evidence_ought_hume_and_flag_type(self):
        # evidence requires a source
        r = run(self.tmp, "create-node", "--agent", "a1", "--text", "a study finding", "--kind", "evidence")
        self.assertEqual(r.returncode, 1)
        self.assertFalse(json.loads(r.stdout)["ok"])
        r = run(self.tmp, "create-node", "--agent", "a1", "--text", "a study finding",
                "--kind", "evidence", "--source", "http://x")
        self.assertEqual(r.returncode, 0, r.stderr)
        ev_id = json.loads(r.stdout)["id"]

        # ought needs no source
        r = run(self.tmp, "create-node", "--agent", "a1", "--text", "you should avoid eggs", "--kind", "ought")
        self.assertEqual(r.returncode, 0, r.stderr)
        ought_id = json.loads(r.stdout)["id"]

        r = run(self.tmp, "create-node", "--agent", "a2", "--text", "eggs raise CVD risk")
        is_id = json.loads(r.stdout)["id"]

        # Hume: an Ought may not ground an is-node
        r = run(self.tmp, "draw-ground", "--agent", "a2", "--from", ought_id, "--to", is_id)
        self.assertEqual(r.returncode, 1)
        self.assertFalse(json.loads(r.stdout)["ok"])

        # evidence still shows up in list-studies grouped by source
        r = run(self.tmp, "list-studies")
        self.assertEqual(r.returncode, 0, r.stderr)
        studies = json.loads(r.stdout)["studies"]
        self.assertEqual(studies[0]["source"], "http://x")
        self.assertIn(ev_id, studies[0]["nodes"])

        # flag-type: records the flag, adds no node, leaves structure intact
        r = run(self.tmp, "flag-type", "--agent", "a2", "--node", is_id, "--as", "ought")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout)["ok"])
        r = run(self.tmp, "stats")
        self.assertEqual(json.loads(r.stdout)["counts"]["nodes"], 3)

    def test_supersede_demote_restore(self):
        r = run(self.tmp, "create-node", "--agent", "a1", "--text", "a claim to demote later")
        nid = json.loads(r.stdout)["id"]
        r = run(self.tmp, "supersede", "--agent", "a2", "--target", nid, "--reason", "superseded")
        self.assertEqual(r.returncode, 0, r.stderr)
        graph = json.loads((self.tmp / "graph.json").read_text())
        self.assertEqual(graph["nodes"][0]["demoted"]["reason"], "superseded")
        # restore removes the marker
        r = run(self.tmp, "supersede", "--agent", "a2", "--target", nid, "--restore")
        self.assertEqual(r.returncode, 0, r.stderr)
        graph = json.loads((self.tmp / "graph.json").read_text())
        self.assertNotIn("demoted", graph["nodes"][0])
        # restoring again (not demoted) is rejected
        r = run(self.tmp, "supersede", "--agent", "a2", "--target", nid, "--restore")
        self.assertEqual(r.returncode, 1)

    def test_lint_and_ghosts_verbs(self):
        # two grounds into one node + an orphan -> lint should parse and flag the orphan
        ids = []
        for i in range(3):
            r = run(self.tmp, "create-node", "--agent", "a1", "--text", f"claim {i} placeholder text")
            ids.append(json.loads(r.stdout)["id"])
        run(self.tmp, "draw-ground", "--agent", "a1", "--from", ids[1], "--to", ids[0])
        r = run(self.tmp, "lint", "--hub-threshold", "1")  # run() appends --data/--json
        self.assertEqual(r.returncode, 0, r.stderr)
        rep = json.loads(r.stdout)
        self.assertTrue(rep["ok"])
        self.assertIn(ids[2], rep["orphan_nodes"])           # ids[2] has no edges
        self.assertEqual(rep["summary"]["hub_nodes"], 1)     # ids[0] has in-degree 1 >= threshold

        r = run(self.tmp, "ghosts")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout)["ok"])

    def test_ghost_eligible_exported_to_graph_json(self):
        # A standalone node rated low+settled is ghost_eligible; the fold now
        # exports that AUTO signal as a conditional per-target flag (UI request),
        # and it must match the `ghosts` read verb exactly.
        low = json.loads(run(self.tmp, "create-node", "--agent", "author",
                             "--text", "a refuted standalone claim placeholder").stdout)["id"]
        high = json.loads(run(self.tmp, "create-node", "--agent", "author",
                              "--text", "a well-supported standalone claim placeholder").stdout)["id"]
        for r in ("r1", "r2", "r3"):
            run(self.tmp, "rate", "--agent", r, "--target", low, "--dim", "A", "--value", "0.8")
            run(self.tmp, "rate", "--agent", r, "--target", high, "--dim", "A", "--value", "4.2")
        run(self.tmp, "rebuild")
        graph = json.loads((self.tmp / "graph.json").read_text())
        byid = {n["id"]: n for n in graph["nodes"]}
        self.assertTrue(byid[low].get("ghost_eligible"))               # flag present + True
        self.assertNotIn("ghost_eligible", byid[high])                 # conditional: omitted when not
        verb = set((json.loads(run(self.tmp, "ghosts").stdout).get("ghost_eligible") or {}).keys())
        flagged = {n["id"] for n in graph["nodes"] if n.get("ghost_eligible")}
        self.assertEqual(flagged, verb)                                # graph.json == read verb

    def test_evidence_source_named_in_graph_json(self):
        # FLF: Evidence nodes name their source. A free-text source shows as-is;
        # a source matching the graph's harness/sources.json resolves to title+url.
        (self.tmp / "harness").mkdir()
        (self.tmp / "harness" / "sources.json").write_text(json.dumps(
            {"sources": [{"id": "s01", "title": "A Real Study (2024)", "url": "https://example.org/x"}]}))
        free = json.loads(run(self.tmp, "create-node", "--agent", "a1", "--kind", "evidence",
                              "--source", "some-freetext-ref", "--text", "an evidence claim placeholder").stdout)["id"]
        resolved = json.loads(run(self.tmp, "create-node", "--agent", "a1", "--kind", "evidence",
                                  "--source", "s01", "--text", "another evidence claim placeholder").stdout)["id"]
        run(self.tmp, "rebuild")
        byid = {n["id"]: n for n in json.loads((self.tmp / "graph.json").read_text())["nodes"]}
        self.assertEqual(byid[free]["source"], {"ref": "some-freetext-ref", "title": "some-freetext-ref", "url": None})
        self.assertEqual(byid[resolved]["source"],
                         {"ref": "s01", "title": "A Real Study (2024)", "url": "https://example.org/x"})

    def test_layer_exported_as_support_depth(self):
        # Per-node `layer` = Kahn longest-path support-depth (a ground supports
        # its dependent, so layer[to] = max(layer[from]) + 1); a source is 0.
        a = json.loads(run(self.tmp, "create-node", "--agent", "x", "--text", "ground claim placeholder").stdout)["id"]
        b = json.loads(run(self.tmp, "create-node", "--agent", "x", "--text", "middle claim placeholder").stdout)["id"]
        c = json.loads(run(self.tmp, "create-node", "--agent", "x", "--text", "top claim placeholder").stdout)["id"]
        run(self.tmp, "draw-ground", "--agent", "x", "--from", a, "--to", b)   # a supports b
        run(self.tmp, "draw-ground", "--agent", "x", "--from", b, "--to", c)   # b supports c
        run(self.tmp, "rebuild")
        byid = {n["id"]: n for n in json.loads((self.tmp / "graph.json").read_text())["nodes"]}
        self.assertEqual(byid[a]["layer"], 0)   # source
        self.assertEqual(byid[b]["layer"], 1)
        self.assertEqual(byid[c]["layer"], 2)   # deepest dependent

    def test_neighborhood_resolves_title_text_not_just_id(self):
        r = run(self.tmp, "create-node", "--agent", "agent-01", "--text", "eggs claim",
                "--title", "Eggs Title")
        n1 = json.loads(r.stdout)["id"]
        r = run(self.tmp, "neighborhood", "--node", n1, "--depth", "1")
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads(r.stdout)
        self.assertEqual(rec["nodes"][0]["primary_title_text"], "Eggs Title")

    def test_search_finds_substring(self):
        run(self.tmp, "create-node", "--agent", "agent-01", "--text", "a very unique zzyzx phrase")
        r = run(self.tmp, "search", "zzyzx")
        self.assertEqual(r.returncode, 0, r.stderr)
        hits = json.loads(r.stdout)["hits"]
        self.assertEqual(len(hits), 1)

    def test_external_anchor_requires_source(self):
        r = run(self.tmp, "create-node", "--agent", "agent-01", "--text", "cited",
                "--kind", "external_anchor")
        self.assertEqual(r.returncode, 1)

    def test_help_documents_every_verb(self):
        r = subprocess.run([sys.executable, str(GRAPH_PY), "--help"], capture_output=True, text=True,
                            cwd=str(V0_DIR))
        self.assertEqual(r.returncode, 0)
        for verb in ("create-node", "draw-ground", "add-antithesis", "agree", "propose-title",
                     "propose-phrasing", "flag-friction", "get-node", "neighborhood", "search",
                     "list-sets", "list-studies", "stats", "rebuild"):
            self.assertIn(verb, r.stdout)


class SeedDemoTest(unittest.TestCase):
    def test_seed_demo_produces_valid_graph(self):
        tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        r = subprocess.run(
            [sys.executable, str(V0_DIR / "seed_demo.py"), "--data", str(tmp)],
            capture_output=True, text=True, cwd=str(V0_DIR),
        )
        self.assertEqual(r.returncode, 0, r.stderr)
        graph = json.loads((tmp / "graph.json").read_text())
        self.assertGreaterEqual(len(graph["nodes"]), 8)
        self.assertLessEqual(len(graph["nodes"]), 12)
        self.assertGreaterEqual(len(graph["ground_edges"]), 1)
        self.assertGreaterEqual(len(graph["conjunction_groups"]), 1)
        self.assertGreaterEqual(len(graph["antithesis_sets"]), 1)
        self.assertGreaterEqual(len(graph["frictions"]), 1)


if __name__ == "__main__":
    unittest.main()
