from __future__ import annotations

from dataclasses import asdict, dataclass
import re


@dataclass(frozen=True)
class Rule:
    rule_id: str
    category: str
    severity: int
    pattern: re.Pattern[str]
    message: str


@dataclass(frozen=True)
class Finding:
    rule_id: str
    category: str
    severity: int
    message: str
    match: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RiskReport:
    text: str
    score: int
    level: str
    categories: list[str]
    findings: list[Finding]

    def to_dict(self) -> dict[str, object]:
        return {
            "text": self.text,
            "score": self.score,
            "level": self.level,
            "categories": self.categories,
            "findings": [finding.to_dict() for finding in self.findings],
        }


RULES = [
    Rule(
        "prompt.ignore_previous",
        "prompt_injection",
        45,
        re.compile(r"\b(ignore|disregard)\s+(all\s+)?(previous|prior)\s+instructions\b", re.I),
        "Attempts to override earlier instructions.",
    ),
    Rule(
        "prompt.override_safety",
        "prompt_injection",
        40,
        re.compile(r"\b(override|bypass|disable)\s+(all\s+)?(safety|policy|guardrail)s?\b", re.I),
        "Attempts to bypass safety or policy controls.",
    ),
    Rule(
        "prompt.hidden_instructions",
        "prompt_injection",
        35,
        re.compile(r"\b(system prompt|hidden instructions?|developer message|internal policy)\b", re.I),
        "Requests hidden or privileged instructions.",
    ),
    Rule(
        "secret.token_file",
        "secret_exfiltration",
        60,
        re.compile(r"(\.config/gh/hosts\.yml|\.git-credentials|GITHUB_TOKEN|API[_-]?KEY|env secrets?)", re.I),
        "Targets credentials, tokens, or local secret storage.",
    ),
    Rule(
        "secret.disclose",
        "secret_exfiltration",
        40,
        re.compile(r"\b(reveal|print|dump|disclose|send)\b.*\b(token|secret|password|credential)s?\b", re.I),
        "Requests disclosure of credentials or secrets.",
    ),
    Rule(
        "network.post_external",
        "network_exfiltration",
        40,
        re.compile(r"\b(post|upload|send|curl)\b.*https?://", re.I),
        "Requests sending data to an external URL.",
    ),
    Rule(
        "tool.destructive_shell",
        "tool_misuse",
        30,
        re.compile(r"\b(rm\s+-rf|chmod\s+777|sudo\s+|delete\s+all)\b", re.I),
        "Suggests destructive or elevated shell operations.",
    ),
]


def analyze_text(text: str) -> RiskReport:
    normalized = text.strip()
    if not normalized:
        raise ValueError("text must not be empty")

    findings = _find_matches(normalized)
    score = min(sum(finding.severity for finding in findings), 100)
    categories = sorted({finding.category for finding in findings})

    return RiskReport(
        text=normalized,
        score=score,
        level=_level_for_score(score),
        categories=categories,
        findings=findings,
    )


def _find_matches(text: str) -> list[Finding]:
    findings: list[Finding] = []
    for rule in RULES:
        match = rule.pattern.search(text)
        if match is None:
            continue
        findings.append(
            Finding(
                rule_id=rule.rule_id,
                category=rule.category,
                severity=rule.severity,
                message=rule.message,
                match=match.group(0),
            )
        )
    return findings


def _level_for_score(score: int) -> str:
    if score >= 90:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"
