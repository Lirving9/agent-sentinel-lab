# Scenario Set

The scenario files are synthetic eval cards for local agent-risk screening. They intentionally avoid real secrets and production hostnames.

| Range | Pattern |
| --- | --- |
| 001-090 | Repeating coverage of prompt injection, secret exfiltration, network exfiltration, tool misuse, and benign tasks. |
| 091-340 | Deterministic calibration set generated from `tools/generate_scenarios.py` templates. |

Use them as fixtures for benchmark scripts, manual rule tuning, and regression tests. The repository test suite evaluates every scenario card against the current analyzer rules, so update either the rules or the expected card metadata when changing detection behavior.

Regenerate the deterministic calibration range with:

```bash
python3 tools/generate_scenarios.py --force
```
