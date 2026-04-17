from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ConfigError(ValueError):
    """Raised when SpecGuard config is invalid."""


def load_config(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ConfigError(f"Config file not found: {path}")

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ConfigError("Top-level config must be a mapping/object.")

    return data


def _validate_waivers(waivers: Any, errors: list[str]) -> None:
    if waivers is None:
        return

    if not isinstance(waivers, list):
        errors.append("'waivers' must be a list when provided.")
        return

    for idx, waiver in enumerate(waivers):
        if not isinstance(waiver, dict):
            errors.append(f"waivers[{idx}] must be an object.")
            continue

        rule_id = waiver.get("rule_id")
        if not isinstance(rule_id, str) or not rule_id.strip():
            errors.append(f"waivers[{idx}].rule_id must be a non-empty string.")

        patterns = waiver.get("path_patterns")
        if not isinstance(patterns, list) or not patterns:
            errors.append(f"waivers[{idx}].path_patterns must be a non-empty list of glob patterns.")
        else:
            for pattern_idx, pattern in enumerate(patterns):
                if not isinstance(pattern, str) or not pattern.strip():
                    errors.append(
                        f"waivers[{idx}].path_patterns[{pattern_idx}] must be a non-empty string."
                    )

        reason = waiver.get("reason")
        if reason is not None and not isinstance(reason, str):
            errors.append(f"waivers[{idx}].reason must be a string when provided.")


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    version = config.get("version")
    if version != 1:
        errors.append("'version' is required and must be 1.")

    rules = config.get("rules")
    if not isinstance(rules, list):
        errors.append("'rules' is required and must be a list.")
    else:
        for idx, rule in enumerate(rules):
            if not isinstance(rule, dict):
                errors.append(f"rules[{idx}] must be an object.")
                continue

            rule_id = rule.get("id")
            if not isinstance(rule_id, str) or not rule_id.strip():
                errors.append(f"rules[{idx}].id must be a non-empty string.")

            enabled = rule.get("enabled")
            if enabled is not None and not isinstance(enabled, bool):
                errors.append(f"rules[{idx}].enabled must be a boolean when provided.")

    _validate_waivers(config.get("waivers"), errors)

    return errors
