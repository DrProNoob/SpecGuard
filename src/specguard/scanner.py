from __future__ import annotations

from pathlib import Path

SPEC_FILE_SUFFIXES = {".md", ".markdown", ".yml", ".yaml", ".json"}
SPEC_DIR_MARKERS = {"spec", "specs", "rfc", "rfcs", "adr", "adrs"}
OPENAPI_MARKERS = ("openapi", "swagger")


def find_spec_files(repo_root: Path) -> list[Path]:
    discovered: list[Path] = []

    for file_path in repo_root.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in SPEC_FILE_SUFFIXES:
            continue

        rel = file_path.relative_to(repo_root)
        rel_text = rel.as_posix().lower()

        parent_dirs = [part.lower() for part in rel.parts[:-1]]
        has_spec_dir = any(part in SPEC_DIR_MARKERS for part in parent_dirs)
        has_openapi_marker = any(marker in rel_text for marker in OPENAPI_MARKERS)

        if has_spec_dir or has_openapi_marker:
            discovered.append(rel)

    return sorted(discovered)
