# AGENTS.md

## Project purpose

SpecGuard is a Git-native OSS CLI for spec-driven development guardrails.
Current milestone is **v0 foundation**: minimal CLI + config validation + simple spec file discovery.

## Current milestone boundaries

Do:

- Keep behavior deterministic and easy to reason about.
- Prefer local, file-based checks over remote integrations.
- Add tests alongside functionality.
- Document assumptions and tradeoffs.

Do not:

- Add cloud services, hosted infra, or paid features.
- Add heavy ML/AI systems.
- Build full GitHub bots yet.
- Expand scope beyond PR-time spec drift groundwork.

## Coding conventions

- Language: Python 3.11+.
- Keep modules small and composable.
- Prefer explicit types for public functions.
- Avoid unnecessary abstractions and framework complexity.
- Keep CLI output readable and deterministic.
- Use TODOs only for concrete, near-term follow-ups.

## Repo workflow for agents/contributors

1. Read `README.md` and `docs/architecture/v0.md` before large changes.
2. Make incremental changes in small commits.
3. Update tests/docs in the same change when behavior changes.
4. If a request conflicts with milestone scope, call that out explicitly.

## Commands

Setup:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

Run checks:

```bash
PYTHONPATH=src pytest
PYTHONPATH=src python -m specguard.cli validate-config --config specguard.json
PYTHONPATH=src python -m specguard.cli scan-specs --repo .
```

## Scope control rules

- Prefer extending existing modules instead of introducing new subsystems.
- Favor one clear path over multiple partially-implemented options.
- Avoid speculative architecture for future milestones.
- Keep changes easy for future Codex tasks to build on.
