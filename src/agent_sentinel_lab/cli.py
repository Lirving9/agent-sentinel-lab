from __future__ import annotations

import argparse
import json
import sys

from agent_sentinel_lab.analyzer import analyze_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-sentinel",
        description="Score AI agent task text for prompt-injection and tool-risk heuristics.",
    )
    parser.add_argument("text", nargs="+", help="Task text to analyze.")
    return parser


def run(argv: list[str] | None = None) -> tuple[int, str, str]:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = int(exc.code) if isinstance(exc.code, int) else 2
        return code, "", parser.format_usage()

    report = analyze_text(" ".join(args.text))
    return 0, json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n", ""


def main(argv: list[str] | None = None) -> int:
    exit_code, stdout, stderr = run(argv)
    if stdout:
        sys.stdout.write(stdout)
    if stderr:
        sys.stderr.write(stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
