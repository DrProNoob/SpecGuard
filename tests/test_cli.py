from __future__ import annotations

import json
from pathlib import Path

from specguard.cli import main


def test_validate_config_success(tmp_path: Path, capsys) -> None:
    config = tmp_path / "specguard.json"
    config.write_text(
        json.dumps({"version": 1, "rules": [{"id": "rule-one", "enabled": True}]}),
        encoding="utf-8",
    )

    exit_code = main(["validate-config", "--config", str(config)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "Config OK" in out


def test_scan_specs_finds_expected_files(tmp_path: Path, capsys) -> None:
    (tmp_path / "docs" / "rfcs").mkdir(parents=True)
    (tmp_path / "openapi").mkdir(parents=True)
    (tmp_path / "docs" / "rfcs" / "0001-feature.md").write_text("# RFC", encoding="utf-8")
    (tmp_path / "openapi" / "service.yaml").write_text("openapi: 3.1.0", encoding="utf-8")

    exit_code = main(["scan-specs", "--repo", str(tmp_path)])
    out = capsys.readouterr().out

    assert exit_code == 0
    assert "docs/rfcs/0001-feature.md" in out
    assert "openapi/service.yaml" in out


def test_check_pr_json_output_and_pass(tmp_path: Path, capsys) -> None:
    base = tmp_path / "base"
    head = tmp_path / "head"
    (base / "src").mkdir(parents=True)
    (head / "src").mkdir(parents=True)
    (head / "docs" / "rfcs").mkdir(parents=True)
    (head / "tests").mkdir(parents=True)

    (base / "src" / "service.py").write_text("print('old')\n", encoding="utf-8")

    (head / "src" / "service.py").write_text("print('new')\n", encoding="utf-8")
    (head / "docs" / "rfcs" / "001-change.md").write_text("# RFC\n", encoding="utf-8")
    (head / "tests" / "test_service.py").write_text("def test_x(): pass\n", encoding="utf-8")

    config = tmp_path / "specguard.json"
    config.write_text(
        json.dumps(
            {
                "version": 1,
                "rules": [
                    {
                        "id": "behavior-code-requires-spec-and-tests",
                        "enabled": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    exit_code = main(
        [
            "check-pr",
            "--config",
            str(config),
            "--base",
            str(base),
            "--head",
            str(head),
            "--format",
            "json",
        ]
    )

    out = capsys.readouterr().out
    payload = json.loads(out)

    assert exit_code == 0
    assert payload["summary"]["code_changes"] >= 1
    assert payload["summary"]["spec_docs_changes"] >= 1
    assert payload["summary"]["test_changes"] >= 1
    assert payload["rules"][0]["status"] == "pass"
