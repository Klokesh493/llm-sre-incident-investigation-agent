# Architecture

```mermaid
flowchart LR
    Input["Request buckets, deploy history and dependency snapshots"] --> Session["Bounded agent loop"]
    Session --> Model["Ollama model selects one probe"]
    Model --> Allow["Validate probe against remaining allowlist"]
    Allow --> Probe["Calculate SLO evidence, build deploy timeline and compare dependency latency"]
    Probe --> Evidence["Hash evidence, record trace, update observations"]
    Evidence -->|More evidence needed| Session
    Evidence --> Output["Page candidate, observe or review"]
    Session -->|Budget or model failure| Review["Review with missing keys"]
```

The local language model selects one evidence probe per turn. The loop validates the returned action, executes the corresponding read-only function and sends the resulting observation back to the model. A deterministic domain policy consumes the validated evidence to produce the decision and source IDs. Missing required evidence yields review. The JSON report includes the trace and per-probe SHA-256 digests.

## Execution boundaries

The caller provides the JSON snapshot. The model selects an action from the probes that have not run yet. The default budget is four calls. Invalid and duplicate actions consume budget. Model timeouts and invalid responses stop the loop and retain evidence collected so far. Only the local Ollama endpoint receives the observations.

A rollout and degraded dependency provide leads for investigation. Their timing does not establish cause. A partial window, fewer than 100 requests, or missing dependency evidence requires review.
