# Case study

## Problem

On-call triage needs to distinguish a measured breach from a gap in collection. This agent reconstructs evidence for one service and incident window.

## Design

The local language model selects one evidence probe per turn. The loop validates the returned action, executes the corresponding read-only function and sends the resulting observation back to the model. A deterministic domain policy consumes the validated evidence to produce the decision and source IDs. Missing required evidence yields review. The JSON report includes the trace and per-probe SHA-256 digests.

## Outcome

The sample reports 36 errors from 900 requests, rollout deploy-v4, and payments latency above the configured threshold. The policy proposes a page for human review.

The captured local-model report records the selected probe order and all validated outputs. The offline evaluation checks alternate inputs and the behavior when the loop cannot collect enough evidence. [Captured report](../examples/live-report.json)
