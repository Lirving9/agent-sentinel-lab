# Rule Catalog

The analyzer ships with local heuristic rules. It does not call an LLM or upload task text.

| Category | What it catches |
| --- | --- |
| `prompt_injection` | Attempts to override instructions or reveal hidden prompts. |
| `secret_exfiltration` | Requests credentials, tokens, API keys, or local secret files. |
| `network_exfiltration` | Requests uploading or posting collected data to an external URL. |
| `tool_misuse` | Requests destructive or elevated shell operations. |
