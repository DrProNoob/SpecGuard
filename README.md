# SpecGuard

SpecGuard is a **Git-native guardrail for spec-driven development**.

It helps engineering teams keep pull requests aligned with the specifications that define intended behavior: issues, acceptance criteria, ADRs/RFCs, API contracts, and test expectations.

## Why this exists

Teams often merge behavior changes that are not clearly tied back to specs, tickets, or contracts. This leads to:

- **Spec drift**: code evolves while docs/specs lag behind.
- **Contract drift**: API changes sneak in without explicit review.
- **Missing coverage**: behavior changes land without corresponding tests.
- **Risky automation**: AI-generated PRs may look plausible but miss required process links.

SpecGuard aims to catch these issues at PR time using transparent, deterministic checks.

## v0 scope (this repository foundation)

This first version intentionally stays small:

- A Python CLI scaffold (`specguard`) with one practical PR check slice.
- Config loading + validation for a sample SpecGuard config file.
- Basic repository scan for spec-like files (`specs/`, `docs/rfcs`, `docs/adrs`, OpenAPI filenames).
- A tiny test suite to validate rule behavior and CLI output.
- Contributor/agent docs designed for iterative OSS development.

### What v0 does today

- `specguard validate-config --config specguard.json`
  - Loads JSON config.
  - Verifies minimal required keys/types.
  - Prints success/failure.
- `specguard scan-specs --repo .`
  - Scans a repository for candidate spec files.
  - Prints discovered files in deterministic order.
- `specguard check-pr --config specguard.json --base ./snapshots/base --head ./snapshots/head [--format text|json]`
  - Compares two repo snapshots.
  - Detects changed files.
  - Classifies changes into spec/docs, code, test, and API contract categories.
  - Evaluates the v0 rule: behavior-affecting code changes require spec/ticket evidence + test evidence, or an explicit waiver.

## Heuristics used in `check-pr` (v0)

- **Code changes**: files under `src/`, `app/`, `backend/`, `frontend/`, `api/` or common source extensions.
- **Test changes**: files under `tests/` or filenames containing `test`/`spec`.
- **Spec/docs evidence**: changed files under `docs/specs`, `docs/rfcs`, or `docs/adrs`.
- **API contract changes**: changed files with `openapi`/`swagger`/`schema` markers and `.yaml/.yml/.json` extensions.
- **Waiver**: config-based rule waiver with `rule_id` + `path_patterns` globs.

These are intentionally simple and deterministic; no semantic/ML inference.

## What SpecGuard does **not** do yet

- No PR comment bot.
- No direct GitHub API checks.
- No semantic diffing of specs vs implementation.
- No test impact or coverage analysis.
- No AI/LLM safety classifiers.
- No cloud services or hosted backend.

## Implementation stack choice

SpecGuard v0 uses **Python (3.11+)** with:

- **argparse** for a dependency-light CLI.
- **json** (stdlib) for config parsing.
- **pytest** for tests.

Why this stack:

- Fast iteration for a solo founder/small OSS team.
- Low barrier for contributors.
- Minimal dependency overhead.
- Easy path to future GitHub/OpenAPI integrations.

## Quick start

### Prerequisites

- Python 3.11+

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### Run CLI

```bash
specguard validate-config --config specguard.json
specguard scan-specs --repo .
specguard check-pr --config specguard.json --base ./snapshots/base --head ./snapshots/head
specguard check-pr --config specguard.json --base ./snapshots/base --head ./snapshots/head --format json
```

Or without install:

```bash
PYTHONPATH=src python -m specguard.cli validate-config --config specguard.json
PYTHONPATH=src python -m specguard.cli scan-specs --repo .
PYTHONPATH=src python -m specguard.cli check-pr --config specguard.json --base ./snapshots/base --head ./snapshots/head
```

### Run tests

```bash
PYTHONPATH=src pytest
```

## Example config

See `specguard.json` for a minimal starter config including a waiver example.

## How future integrations might work

Planned direction (incremental):

1. **Local PR-mode simulation (current base)**
   - Given base/head refs, detect touched files and required linked specs.
2. **GitHub-native integration**
   - GitHub Action wrapper invoking `specguard` in CI.
   - Optional PR annotations/check-run output.
3. **Spec type adapters**
   - GitHub Issues, Markdown templates, ADR/RFC conventions, OpenAPI parser hooks.
4. **Rule engine expansion**
   - Configurable guardrails for “changed code requires changed spec/test evidence”.

## Roadmap ideas

- Rule: enforce PR description references at least one tracked spec/ticket.
- Rule: when `openapi/` changes, require linked contract-change note.
- Rule: changed behavior files require nearby test changes or explicit waiver.
- SARIF/check-style output format.
- Optional plugin system for org-specific rules.

## Contributing

Please read:

- `CONTRIBUTING.md`
- `AGENTS.md`
- `docs/architecture/v0.md`

The project emphasizes small, reviewable changes and clear milestone boundaries.
