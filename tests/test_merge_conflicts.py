from __future__ import annotations

from pathlib import Path

LEFT_MARKER = "<" * 7
MID_MARKER = "=" * 7
RIGHT_MARKER = ">" * 7
SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache"}
SKIP_EXTENSIONS = {".pyc", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".ico"}


def _iter_repo_files(repo_root: Path):
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in SKIP_EXTENSIONS:
            continue
        yield path


def _contains_conflict_marker(line: str) -> bool:
    stripped = line.lstrip()
    return (
        stripped.startswith(f"{LEFT_MARKER} ")
        or stripped == MID_MARKER
        or stripped.startswith(f"{RIGHT_MARKER} ")
    )


def test_repository_has_no_unresolved_merge_conflict_markers() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    markers_found: list[str] = []

    for file_path in _iter_repo_files(repo_root):
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for line_number, line in enumerate(content.splitlines(), start=1):
            if _contains_conflict_marker(line):
                relative = file_path.relative_to(repo_root)
                markers_found.append(f"{relative}:{line_number}: {line}")

    assert not markers_found, "Unresolved merge conflict markers found:\n" + "\n".join(markers_found)
