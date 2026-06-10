from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from agent_sentinel_lab.analyzer import RiskReport, analyze_text, list_rules
from agent_sentinel_lab.scenarios import evaluate_scenarios, load_scenarios


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-sentinel",
        description="Score AI agent task text for prompt-injection and tool-risk heuristics.",
    )
    parser.add_argument("text", nargs="*", help="Task text to analyze.")
    parser.add_argument("--input-file", type=Path, help="Read task text from a UTF-8 text file.")
    parser.add_argument("--stdin", action="store_true", help="Read task text from standard input.")
    parser.add_argument("--format", choices=["json", "text"], default="json", help="Output format.")
    parser.add_argument(
        "--threshold",
        type=int,
        help="Exit with status 1 when the report score is greater than or equal to this value.",
    )
    parser.add_argument("--list-rules", action="store_true", help="List built-in heuristic rules.")
    parser.add_argument("--evaluate-scenarios", type=Path, help="Evaluate scenario markdown cards in a directory.")
    return parser


def run(argv: list[str] | None = None, stdin_text: str | None = None) -> tuple[int, str, str]:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = int(exc.code) if isinstance(exc.code, int) else 2
        return code, "", parser.format_usage()

    if args.list_rules:
        payload = {"rules": list_rules()}
        return 0, _render_json(payload), ""

    if args.evaluate_scenarios is not None:
        try:
            result = evaluate_scenarios(load_scenarios(args.evaluate_scenarios))
        except OSError as exc:
            return 2, "", f"{exc}\n"
        except ValueError as exc:
            return 2, "", f"{exc}\n"
        return (1 if result.failed else 0), _render_json(result.to_dict()), ""

    try:
        text = _read_task_text(args, parser, stdin_text)
        report = analyze_text(text)
    except OSError as exc:
        return 2, "", f"{exc}\n"
    except ValueError as exc:
        return 2, "", f"{exc}\n"

    exit_code = 1 if args.threshold is not None and report.score >= args.threshold else 0
    if args.format == "text":
        return exit_code, _render_text(report), ""
    return exit_code, _render_json(report.to_dict()), ""


def main(argv: list[str] | None = None) -> int:
    exit_code, stdout, stderr = run(argv)
    if stdout:
        sys.stdout.write(stdout)
    if stderr:
        sys.stderr.write(stderr)
    return exit_code


def _read_task_text(
    args: argparse.Namespace,
    parser: argparse.ArgumentParser,
    stdin_text: str | None,
) -> str:
    sources = [bool(args.text), args.input_file is not None, args.stdin]
    if sum(sources) != 1:
        raise ValueError(parser.format_usage().strip())
    if args.input_file is not None:
        return args.input_file.read_text(encoding="utf-8")
    if args.stdin:
        return stdin_text if stdin_text is not None else sys.stdin.read()
    return " ".join(args.text)


def _render_json(payload: dict[str, object]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def _render_text(report: RiskReport) -> str:
    lines = [
        f"Level: {report.level}",
        f"Score: {report.score}",
        f"Categories: {', '.join(report.categories) if report.categories else 'none'}",
    ]
    if not report.findings:
        lines.append("Findings: none")
    else:
        lines.append("Findings:")
        for finding in report.findings:
            lines.append(f"- {finding.rule_id}: {finding.message} ({finding.match})")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
