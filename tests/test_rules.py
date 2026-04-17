from __future__ import annotations

from pathlib import Path

from specguard.changes import FileChange
from specguard.classify import classify_changes
from specguard.rules import BEHAVIOR_RULE_ID, evaluate_behavior_change_rule


def test_behavior_rule_fails_without_evidence() -> None:
    changes = [FileChange(path=Path("src/service.py"), status="modified")]
    classified = classify_changes(changes)

    result = evaluate_behavior_change_rule(classified, {"version": 1, "rules": []})

    assert result["id"] == BEHAVIOR_RULE_ID
    assert result["status"] == "fail"
    assert "spec/ticket evidence" in result["reason"]
    assert "test evidence" in result["reason"]


def test_behavior_rule_passes_with_spec_and_test_evidence() -> None:
    changes = [
        FileChange(path=Path("src/service.py"), status="modified"),
        FileChange(path=Path("docs/rfcs/001-api.md"), status="modified"),
        FileChange(path=Path("tests/test_service.py"), status="modified"),
    ]
    classified = classify_changes(changes)

    result = evaluate_behavior_change_rule(classified, {"version": 1, "rules": []})

    assert result["status"] == "pass"


def test_behavior_rule_can_be_waived_by_path_pattern() -> None:
    changes = [FileChange(path=Path("src/legacy/old_module.py"), status="modified")]
    classified = classify_changes(changes)

    config = {
        "version": 1,
        "rules": [],
        "waivers": [
            {
                "rule_id": BEHAVIOR_RULE_ID,
                "path_patterns": ["src/legacy/*"],
                "reason": "Temporary migration waiver",
            }
        ],
    }

    result = evaluate_behavior_change_rule(classified, config)

    assert result["status"] == "waived"
    assert result["reason"] == "Temporary migration waiver"
