from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class FileChange:
    path: Path
    status: str  # added | modified | removed


def _file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _list_files(root: Path) -> dict[Path, str]:
    files: dict[Path, str] = {}
    for item in root.rglob("*"):
        if item.is_file():
            rel = item.relative_to(root)
            files[rel] = _file_digest(item)
    return files


def compare_directories(base: Path, head: Path) -> list[FileChange]:
    base_files = _list_files(base)
    head_files = _list_files(head)

    base_paths = set(base_files.keys())
    head_paths = set(head_files.keys())
    all_paths = sorted(base_paths | head_paths)

    changes: list[FileChange] = []
    for rel in all_paths:
        if rel not in base_files:
            changes.append(FileChange(path=rel, status="added"))
            continue
        if rel not in head_files:
            changes.append(FileChange(path=rel, status="removed"))
            continue
        if base_files[rel] != head_files[rel]:
            changes.append(FileChange(path=rel, status="modified"))

    return changes
