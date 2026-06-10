from __future__ import annotations

import pytest

from agent_sentinel_lab.scenarios import evaluate_scenarios, load_scenarios, parse_scenario_card
from tools.generate_scenarios import TEMPLATES, render_card, write_cards


def test_render_card_outputs_parseable_scenario() -> None:
    card = render_card(91, template=TEMPLATES[0])

    scenario = parse_scenario_card(card, source="generated")

    assert scenario.identifier == "091"
    assert scenario.expected_category == "prompt_injection"
    assert scenario.expected_level == "high"


def test_write_cards_creates_rule_aligned_scenarios(tmp_path) -> None:
    written = write_cards(tmp_path, start=91, count=20)

    result = evaluate_scenarios(load_scenarios(tmp_path))

    assert len(written) == 20
    assert result.total == 20
    assert result.failures == []


def test_write_cards_refuses_to_overwrite_without_force(tmp_path) -> None:
    write_cards(tmp_path, start=91, count=1)

    with pytest.raises(FileExistsError, match="pass --force"):
        write_cards(tmp_path, start=91, count=1)


def test_write_cards_can_overwrite_with_force(tmp_path) -> None:
    first = write_cards(tmp_path, start=91, count=1)
    first[0].write_text("manual edit", encoding="utf-8")

    second = write_cards(tmp_path, start=91, count=1, force=True)

    assert second == first
    assert "manual edit" not in first[0].read_text(encoding="utf-8")
