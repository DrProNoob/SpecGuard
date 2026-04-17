from __future__ import annotations

import argparse
import json
from pathlib import Path

from specguard.config import ConfigError, load_config, validate_config
from specguard.pr_check import run_pr_check
from specguard.scanner import find_spec_files


def cmd_validate_config(config_path: Path) -> int:
    try:
        raw = load_config(config_path)
    except ConfigError as exc:
        print(f"Config error: {exc}")
        return 1

    errors = validate_config(raw)
    if errors:
        print("Invalid config:")
        for item in errors:
            print(f"- {item}")
        return 1

    print(f"Config OK: {config_path}")
    return 0


def cmd_scan_specs(repo: Path) -> int:
    files = find_spec_files(repo)
    if not files:
        print("No candidate spec files found.")
        return 0

    print(f"Found {len(files)} candidate spec file(s):")
    for path in files:
        print(f"- {path.as_posix()}")
    return 0


def _render_check_pr_text(report: dict[str, object]) -> None:
    summary = report["summary"]
    rules = report["rules"]
    changed_files = report["changed_files"]

    print("SpecGuard check-pr summary")
    print(f"- base: {report['base']}")
    print(f"- head: {report['head']}")
    print(f"- changed files: {summary['total_changed_files']}")
    print(
        "- classified changes: "
        f"spec/docs={summary['spec_docs_changes']}, "
        f"code={summary['code_changes']}, "
        f"tests={summary['test_changes']}, "
        f"api_contract={summary['api_contract_changes']}"
    )
    print("\nRule results:")
    for rule in rules:
        print(f"- [{rule['status']}] {rule['id']}: {rule['reason']}")

    print("\nChanged files:")
    if not changed_files:
        print("- (none)")
    for item in changed_files:
        labels = ",".join(item["classifications"]) or "unclassified"
        print(f"- {item['status']} {item['path']} ({labels})")


def cmd_check_pr(config_path: Path, base: Path, head: Path, output_format: str) -> int:
    try:
        config = load_config(config_path)
    except ConfigError as exc:
        print(f"Config error: {exc}")
        return 1

    config_errors = validate_config(config)
    if config_errors:
        print("Invalid config:")
        for item in config_errors:
            print(f"- {item}")
        return 1

    if not base.exists() or not base.is_dir():
        print(f"Base path must be an existing directory: {base}")
        return 1

    if not head.exists() or not head.is_dir():
        print(f"Head path must be an existing directory: {head}")
        return 1

    report = run_pr_check(base=base, head=head, config=config)

    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        _render_check_pr_text(report)

    has_failures = any(rule.get("status") == "fail" for rule in report["rules"])
    return 1 if has_failures else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="specguard", description="SpecGuard CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-config", help="Validate SpecGuard config file")
    validate.add_argument("--config", type=Path, required=True, help="Path to SpecGuard JSON config")

    scan = subparsers.add_parser("scan-specs", help="Scan repo for candidate spec files")
    scan.add_argument("--repo", type=Path, default=Path("."), help="Repository root")

    check_pr = subparsers.add_parser("check-pr", help="Run PR-oriented checks between two repo snapshots")
    check_pr.add_argument("--config", type=Path, required=True, help="Path to SpecGuard JSON config")
    check_pr.add_argument("--base", type=Path, required=True, help="Path to base snapshot directory")
    check_pr.add_argument("--head", type=Path, required=True, help="Path to head snapshot directory")
    check_pr.add_argument(
        "--format",
        dest="output_format",
        choices=["text", "json"],
        default="text",
        help="Output format",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate-config":
        return cmd_validate_config(args.config)
    if args.command == "scan-specs":
        return cmd_scan_specs(args.repo)
    if args.command == "check-pr":
        return cmd_check_pr(args.config, args.base, args.head, args.output_format)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
