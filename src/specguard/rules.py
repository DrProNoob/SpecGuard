from __future__ import annotations

import fnmatch
from typing import Any

from specguard.classify import ClassifiedChange

BEHAVIOR_RULE_ID = "behavior-code-requires-spec-and-tests"


def _matching_waivers(config: dict[str, Any], rule_id: str) -> list[dict[str, Any]]:
    waivers = config.get("waivers", [])
    if not isinstance(waivers, list):
        return []
    return [item for item in waivers if isinstance(item, dict) and item.get("rule_id") == rule_id]


def _is_waived_for_code_paths(config: dict[str, Any], code_paths: list[str], rule_id: str) -> tuple[bool, str | None]:
    waivers = _matching_waivers(config, rule_id)
    if not waivers:
        return False, None

    for waiver in waivers:
        patterns = waiver.get("path_patterns")
        if not isinstance(patterns, list) or not patterns:
            continue

        if all(any(fnmatch.fnmatch(path, pattern) for pattern in patterns) for path in code_paths):
            reason = waiver.get("reason")
            if isinstance(reason, str) and reason.strip():
                return True, reason
            return True, "Waived by config path_patterns"

    return False, None


def evaluate_behavior_change_rule(
    classified_changes: list[ClassifiedChange], config: dict[str, Any]
) -> dict[str, Any]:
    code_paths = [c.change.path.as_posix() for c in classified_changes if c.is_code]
    spec_paths = [c.change.path.as_posix() for c in classified_changes if c.is_spec_docs]
    test_paths = [c.change.path.as_posix() for c in classified_changes if c.is_test]

    if not code_paths:
        return {
            "id": BEHAVIOR_RULE_ID,
            "status": "not_applicable",
            "reason": "No behavior-affecting code changes detected by v0 heuristics.",
            "details": {"code_paths": [], "spec_paths": spec_paths, "test_paths": test_paths},
        }

    waived, waiver_reason = _is_waived_for_code_paths(config, code_paths, BEHAVIOR_RULE_ID)
    if waived:
        return {
            "id": BEHAVIOR_RULE_ID,
            "status": "waived",
            "reason": waiver_reason,
            "details": {"code_paths": code_paths, "spec_paths": spec_paths, "test_paths": test_paths},
        }

    if spec_paths and test_paths:
        return {
            "id": BEHAVIOR_RULE_ID,
            "status": "pass",
            "reason": "Code changes include spec/ticket evidence and test evidence.",
            "details": {"code_paths": code_paths, "spec_paths": spec_paths, "test_paths": test_paths},
        }

    missing: list[str] = []
    if not spec_paths:
        missing.append("spec/ticket evidence")
    if not test_paths:
        missing.append("test evidence")

    return {
        "id": BEHAVIOR_RULE_ID,
        "status": "fail",
        "reason": f"Behavior-affecting code changes missing: {', '.join(missing)}.",
        "details": {"code_paths": code_paths, "spec_paths": spec_paths, "test_paths": test_paths},
    }
