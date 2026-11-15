"""Run the local evidence agent or evaluate its incident fixtures."""
import argparse
import json
from pathlib import Path
import sys

from domain import BRIEF, REQUIRED, prepare
from loop import Ollama, Replay, bounded_json, investigate


def run(path, planner, budget=4):
    source = bounded_json(path)
    if not isinstance(source, dict):
        raise ValueError("case must be a JSON object")
    probes, decide = prepare(source)
    return investigate(probes, REQUIRED, budget, planner, BRIEF, decide)


def evaluate(path):
    suite = bounded_json(path)
    repo_path = Path(path).resolve().parent
    outcomes = []
    for case in suite:
        source = (repo_path / case["input"]).resolve()
        if not source.is_relative_to(repo_path):
            raise ValueError("evaluation inputs must remain beside the suite")
        report = run(source, Replay(case["actions"]), case.get("budget", 4))
        outcomes.append({
            "case": case["name"], "decision": report["decision"], "stop": report["stop"],
            "pass": (report["decision"] == case["expected"]
                     and report["stop"] == case.get("stop", "evidence_complete")
                     and report["citations"] == case["citations"]),
        })
    return {"passed": sum(row["pass"] for row in outcomes), "total": len(outcomes), "cases": outcomes}


def main():
    parser = argparse.ArgumentParser(description=BRIEF)
    commands = parser.add_subparsers(dest="command", required=True)
    inspect = commands.add_parser("run")
    inspect.add_argument("case", type=Path)
    mode = inspect.add_mutually_exclusive_group(required=True)
    mode.add_argument("--model")
    mode.add_argument("--replay", type=Path)
    inspect.add_argument("--port", type=int, choices=range(1, 65536), metavar="PORT", default=11434)
    inspect.add_argument("--budget", type=int, choices=range(1, 9), default=4)
    suite = commands.add_parser("evaluate")
    suite.add_argument("suite", type=Path, nargs="?", default=Path("examples/eval.json"))
    args = parser.parse_args()
    try:
        if args.command == "run":
            planner = Ollama(args.model, args.port) if args.model else Replay(bounded_json(args.replay))
            result = run(args.case, planner, args.budget)
            status = 1 if result["stop"] != "evidence_complete" else 0
        else:
            result = evaluate(args.suite)
            status = 0 if result["passed"] == result["total"] else 1
    except (OSError, ValueError, TypeError, KeyError, OverflowError) as exc:
        parser.exit(2, f"Input error: {exc}\n")
    json.dump(result, sys.stdout, indent=2, sort_keys=True, allow_nan=False)
    print()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
