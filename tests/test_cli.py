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
