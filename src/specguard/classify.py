from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from specguard.changes import FileChange

CODE_DIR_PREFIXES = ("src/", "app/", "backend/", "frontend/", "api/")
CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".cs",
    ".rb",
    ".php",
}


@dataclass(frozen=True)
class ClassifiedChange:
    change: FileChange
    is_spec_docs: bool
    is_code: bool
    is_test: bool
    is_api_contract: bool

    def labels(self) -> list[str]:
        labels: list[str] = []
        if self.is_spec_docs:
            labels.append("spec_docs")
        if self.is_code:
            labels.append("code")
        if self.is_test:
            labels.append("test")
        if self.is_api_contract:
            labels.append("api_contract")
        return labels


def _is_spec_docs(path_text: str) -> bool:
    markers = (
        "docs/spec",
        "docs/specs",
        "docs/rfc",
        "docs/rfcs",
        "docs/adr",
        "docs/adrs",
    )
    return any(marker in path_text for marker in markers)


def _is_test(path_text: str) -> bool:
    filename = path_text.rsplit("/", 1)[-1]
    if path_text.startswith("tests/"):
        return True
    return "test" in filename or "spec" in filename


def _is_code(path: Path, path_text: str, is_test: bool) -> bool:
    if is_test:
        return False
    if any(path_text.startswith(prefix) for prefix in CODE_DIR_PREFIXES):
        return True
    return path.suffix.lower() in CODE_EXTENSIONS


def _is_api_contract(path: Path, path_text: str) -> bool:
    contract_markers = ("openapi", "swagger", "schema")
    contract_exts = {".yaml", ".yml", ".json"}
    return any(marker in path_text for marker in contract_markers) and path.suffix.lower() in contract_exts


def classify_change(change: FileChange) -> ClassifiedChange:
    path_text = change.path.as_posix().lower()
    path = change.path
    is_test = _is_test(path_text)
    return ClassifiedChange(
        change=change,
        is_spec_docs=_is_spec_docs(path_text),
        is_code=_is_code(path, path_text, is_test),
        is_test=is_test,
        is_api_contract=_is_api_contract(path, path_text),
    )


def classify_changes(changes: list[FileChange]) -> list[ClassifiedChange]:
    return [classify_change(change) for change in changes]
