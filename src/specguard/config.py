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


def validate_config(config: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    version = config.get("version")
    if version != 1:
        errors.append("'version' is required and must be 1.")

    rules = config.get("rules")
    if not isinstance(rules, list):
        errors.append("'rules' is required and must be a list.")
        return errors

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

    return errors
