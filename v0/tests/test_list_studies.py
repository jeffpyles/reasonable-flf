"""Tests for `list-studies` (BUILD-SPEC.md §2 read verbs; resolves friction
F2, "one source, multiple findings, no study-level identity"). Covers:
grouping multiple citing nodes under one source, resolving a pack citation,
and falling back to the raw source string when the pack has no matching
ref_id."""
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from reasonable import ops, queries


class ListStudiesTest(unittest.TestCase):
    def setUp(self):
        self.data = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.data, ignore_errors=True)

        # A throwaway sources pack, distinct from the real v0/sources/eggs
        # pack (which this task must not touch).
        self.sources_root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.sources_root, ignore_errors=True)
        pack_dir = self.sources_root / "testpack"
        pack_dir.mkdir()
        (pack_dir / "index.json").write_text(json.dumps([
            {
                "ref_id": "src-001",
                "citation": "Smith J, et al. \"A Test Study.\" Journal of Testing, 2020.",
                "url": "https://example.com/smith-2020",
                "claim_summary": "A study that yields more than one finding.",
                "status": "VERIFY_BEFORE_USE",
            },
        ]))

    def _create_anchor(self, agent: str, text: str, source: str) -> str:
        res = ops.cmd_create_node(self.data, agent, text, kind="external_anchor", source=source)
        self.assertTrue(res.ok, res.errors)
        return res.id

    def test_source_cited_by_multiple_nodes_groups_them(self):
        n1 = self._create_anchor("agent-01", "finding one drawn from the study", "src-001")
        n2 = self._create_anchor("agent-01", "a second, different finding from the same study", "src-001")

        graph = queries.load_graph(self.data)
        studies = queries.list_studies(graph, self.sources_root)

        rec = next(s for s in studies if s["source"] == "src-001")
        self.assertEqual(sorted(rec["nodes"]), sorted([n1, n2]))

    def test_source_with_pack_citation_shows_it(self):
        self._create_anchor("agent-01", "a finding citing the packed source", "src-001")

        graph = queries.load_graph(self.data)
        studies = queries.list_studies(graph, self.sources_root)

        rec = next(s for s in studies if s["source"] == "src-001")
        self.assertEqual(rec["citation"], "Smith J, et al. \"A Test Study.\" Journal of Testing, 2020.")

    def test_source_not_in_pack_still_lists_with_raw_string(self):
        n1 = self._create_anchor(
            "agent-01", "an unverified finding using a free-text source", "unpacked-source-xyz",
        )

        graph = queries.load_graph(self.data)
        studies = queries.list_studies(graph, self.sources_root)

        rec = next(s for s in studies if s["source"] == "unpacked-source-xyz")
        self.assertEqual(rec["citation"], "unpacked-source-xyz")
        self.assertEqual(rec["nodes"], [n1])

    def test_missing_sources_root_falls_back_to_raw_strings(self):
        n1 = self._create_anchor("agent-01", "a finding with no pack available at all", "src-001")

        graph = queries.load_graph(self.data)
        studies = queries.list_studies(graph, self.data / "no-such-sources-dir")

        rec = next(s for s in studies if s["source"] == "src-001")
        self.assertEqual(rec["citation"], "src-001")
        self.assertEqual(rec["nodes"], [n1])


if __name__ == "__main__":
    unittest.main()
