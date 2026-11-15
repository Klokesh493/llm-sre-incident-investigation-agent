import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock

from agent import evaluate, run
from domain import REQUIRED
from loop import Ollama, Replay, bounded_json

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples/main.json"


class AgentTest(unittest.TestCase):
    def test_evaluation_suite(self):
        result = evaluate(ROOT / "examples/eval.json")
        self.assertGreaterEqual(result["total"], 4)
        self.assertEqual(result["passed"], result["total"], result["cases"])

    def test_loop_rejects_unknown_and_duplicate_actions(self):
        first, *rest = sorted(REQUIRED)
        report = run(SAMPLE, Replay(["shell", first, first, *rest]), 7)
        self.assertEqual(report["stop"], "evidence_complete")
        self.assertEqual([x["event"] for x in report["trace"]].count("rejected_action"), 2)
        self.assertEqual(set(report["evidence"]), REQUIRED)

    def test_missing_evidence_is_review(self):
        report = run(SAMPLE, Replay([]))
        self.assertEqual((report["decision"], report["stop"]), ("review", "model_error"))
        self.assertEqual(set(report["missing"]), REQUIRED)

    def test_ollama_contract_forbids_arbitrary_tool_arguments(self):
        model = Ollama("test-model")
        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock()
        response.read.return_value = json.dumps({"message": {"content": '{"action":"probe"}'}}).encode()
        model.client = Mock()
        model.client.open.return_value = response
        self.assertEqual(model.choose("task", {"probe": "read local evidence"}, {}, 2), "probe")
        request = model.client.open.call_args.args[0]
        options = json.loads(request.data)
        self.assertEqual(request.full_url, "http://127.0.0.1:11434/api/chat")
        self.assertEqual(options["format"]["properties"]["action"]["enum"], ["probe"])
        self.assertFalse(options["format"]["additionalProperties"])

    def test_input_size_and_non_finite_constants(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            for value in (" " * 131_073, '{"samples":[NaN]}', '{"case":1,"case":2}'):
                path.write_text(value, encoding="utf-8")
                with self.assertRaises(ValueError):
                    bounded_json(path)

    def test_cli_required_decision_exposes_policy_failure(self):
        expected = json.loads((ROOT / "examples/eval.json").read_text())[0]["expected"]
        command = [sys.executable, "-B", "agent.py", "run", "examples/main.json",
                   "--replay", "examples/actions.json", "--require-decision"]
        for required, code in [(expected, 0), ("unexpected_decision", 1)]:
            with self.subTest(required=required):
                result = subprocess.run(command + [required], cwd=ROOT, capture_output=True, text=True, check=False)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(json.loads(result.stdout)["decision"], expected)
