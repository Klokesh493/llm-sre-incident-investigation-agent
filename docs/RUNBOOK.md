# Operator runbook

1. Run `make verify` and `make demo` from the repository root.
2. Start local Ollama and run `make live MODEL=qwen2.5:0.5b`.
3. Read `decision`, `reason`, `stop`, and `missing`. Match `citations` to the corresponding evidence entries.
4. Compare any changed evidence or outcome with the [bundled report](../examples/live-report.json).

For a page candidate, open the cited timeline and check the deployment version against the affected requests. Compare dependency signals across regions before deciding the next step.

When the run returns review on a model or budget failure, inspect the last trace event and recover the missing evidence before acting.
