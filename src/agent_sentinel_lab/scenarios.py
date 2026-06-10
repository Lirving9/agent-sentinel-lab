from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import re
from typing import Iterable

from agent_sentinel_lab.analyzer import analyze_text


_HEADING_RE = re.compile(r"^#\s+Scenario\s+([0-9]+):\s*(.+?)\s*$", re.MULTILINE)
_TASK_RE = re.compile(r"```text\s*\n(.*?)\n```", re.DOTALL)
_LEVEL_RE = re.compile(r"^- Expected level:\s*`([^`]+)`\s*$", re.MULTILINE)
_CATEGORY_RE = re.compile(r"^- Expected category:\s*`([^`]+)`\s*$", re.MULTILINE)
_NOTE_RE = re.compile(r"^- Review note:\s*(.+?)\s*$", re.MULTILINE)


@dataclass(frozen=True)
class ScenarioCase:
    identifier: str
    title: str
    text: str
    expected_level: str
    expected_category: str
    review_note: str
    source: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(frozen=True)
class ScenarioEvaluation:
    total: int
    passed: int
    failed: int
    failures: list[dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def parse_scenario_card(markdown: str, source: str = "") -> ScenarioCase:
    heading = _require_match(_HEADING_RE, markdown, "scenario heading", source)
    task = _require_match(_TASK_RE, markdown, "text code block", source)
    level = _require_match(_LEVEL_RE, markdown, "expected level", source)
    category = _require_match(_CATEGORY_RE, markdown, "expected category", source)
    note = _require_match(_NOTE_RE, markdown, "review note", source)

    return ScenarioCase(
        identifier=heading.group(1),
        title=heading.group(2).strip(),
        text=task.group(1).strip(),
        expected_level=level.group(1).strip(),
        expected_category=category.group(1).strip(),
        review_note=note.group(1).strip(),
        source=source,
    )


def load_scenarios(directory: str | Path) -> list[ScenarioCase]:
    scenario_dir = Path(directory)
    paths = sorted(scenario_dir.glob("scenario-*.md"))
    return [
        parse_scenario_card(path.read_text(encoding="utf-8"), source=str(path))
        for path in paths
        if path.is_file()
    ]


def evaluate_scenarios(scenarios: Iterable[ScenarioCase]) -> ScenarioEvaluation:
    cases = list(scenarios)
    failures: list[dict[str, object]] = []

    for scenario in cases:
        report = analyze_text(scenario.text)
        category_ok = _category_matches(scenario.expected_category, report.categories)
        level_ok = report.level == scenario.expected_level
        if category_ok and level_ok:
            continue

        failures.append(
            {
                "identifier": scenario.identifier,
                "source": scenario.source,
                "expected_level": scenario.expected_level,
                "actual_level": report.level,
                "expected_category": scenario.expected_category,
                "actual_categories": report.categories,
                "score": report.score,
            }
        )

    return ScenarioEvaluation(
        total=len(cases),
        passed=len(cases) - len(failures),
        failed=len(failures),
        failures=failures,
    )


def _category_matches(expected: str, actual: list[str]) -> bool:
    if expected == "benign_agent_task":
        return actual == []
    return expected in actual


def _require_match(pattern: re.Pattern[str], text: str, field: str, source: str) -> re.Match[str]:
    match = pattern.search(text)
    if match is None:
        location = f" in {source}" if source else ""
        raise ValueError(f"missing {field}{location}")
    return match
