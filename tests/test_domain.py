import json
from pathlib import Path
import unittest

from agent import run
from loop import Replay

ROOT = Path(__file__).resolve().parents[1] / "examples"


class IncidentTest(unittest.TestCase):
    def test_breach_keeps_change_and_dependency_evidence(self):
        report = run(ROOT / "main.json", Replay(["timeline", "slo", "coverage", "dependencies"]))
        self.assertEqual(report["decision"], "page_candidate")
        self.assertEqual(report["evidence"]["slo"]["data"]["errors"], 36)
        self.assertEqual(report["evidence"]["timeline"]["data"]["changes"][0]["id"], "deploy-v4")
        self.assertEqual(report["evidence"]["dependencies"]["data"]["degraded"], ["payments"])
        self.assertNotIn("coverage", report["citations"])

    def test_evidence_is_reproducible_independent_of_probe_order(self):
        actions = json.loads((ROOT / "actions.json").read_text())
        first = run(ROOT / "main.json", Replay(actions))
        second = run(ROOT / "main.json", Replay(reversed(actions)))
        self.assertEqual(first["evidence"], second["evidence"])
        self.assertNotEqual(first["trace"], second["trace"])
