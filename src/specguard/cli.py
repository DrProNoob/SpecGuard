from __future__ import annotations

import argparse
from pathlib import Path

from specguard.config import ConfigError, load_config, validate_config
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="specguard", description="SpecGuard CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate-config", help="Validate SpecGuard config file")
    validate.add_argument("--config", type=Path, required=True, help="Path to SpecGuard JSON config")

    scan = subparsers.add_parser("scan-specs", help="Scan repo for candidate spec files")
    scan.add_argument("--repo", type=Path, default=Path("."), help="Repository root")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "validate-config":
        return cmd_validate_config(args.config)
    if args.command == "scan-specs":
        return cmd_scan_specs(args.repo)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
