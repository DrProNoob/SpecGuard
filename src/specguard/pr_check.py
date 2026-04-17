from __future__ import annotations

from pathlib import Path
from typing import Any

from specguard.changes import compare_directories
from specguard.classify import classify_changes
from specguard.rules import evaluate_behavior_change_rule


def run_pr_check(base: Path, head: Path, config: dict[str, Any]) -> dict[str, Any]:
    changes = compare_directories(base, head)
    classified = classify_changes(changes)

    summary = {
        "total_changed_files": len(classified),
        "spec_docs_changes": sum(1 for c in classified if c.is_spec_docs),
        "code_changes": sum(1 for c in classified if c.is_code),
        "test_changes": sum(1 for c in classified if c.is_test),
        "api_contract_changes": sum(1 for c in classified if c.is_api_contract),
    }

    rule_result = evaluate_behavior_change_rule(classified, config)

    return {
        "base": str(base),
        "head": str(head),
        "summary": summary,
        "changed_files": [
            {
                "path": c.change.path.as_posix(),
                "status": c.change.status,
                "classifications": c.labels(),
            }
            for c in classified
        ],
        "rules": [rule_result],
    }
