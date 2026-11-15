# Troubleshooting

| What you see | What to check |
| --- | --- |
| `model_error` | Verify that Ollama is on loopback and the configured port and model match the server. |
| `budget_exhausted` | Check for rejected actions in the trace. Use the scripted demo to isolate policy or fixture failures. |
| Exit 2 | Verify the JSON fixture shape, expected field types and input size. |
| Unexpected decision | Compare the cited evidence with the example before adjusting policy. |

For a page candidate, open the cited timeline and check the deployment version against the affected requests. Compare dependency signals across regions before deciding the next step.
