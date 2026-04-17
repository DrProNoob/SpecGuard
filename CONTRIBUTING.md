# Contributing to SpecGuard

Thanks for contributing.

## Philosophy

SpecGuard is in an early foundation stage. Priorities are:

- clarity over cleverness,
- deterministic behavior,
- small reviewable pull requests,
- tight alignment with the active milestone.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Common commands

```bash
PYTHONPATH=src pytest
PYTHONPATH=src python -m specguard.cli validate-config --config specguard.json
PYTHONPATH=src python -m specguard.cli scan-specs --repo .
```

## Pull request expectations

- Keep PRs focused on one small objective.
- Include tests for behavior changes.
- Update docs when interfaces/commands change.
- Explicitly list assumptions and tradeoffs.

## Scope guardrails (v0)

Contributions are encouraged for:

- CLI usability improvements,
- config/rule validation enhancements,
- local scanning/diff logic,
- test quality and docs.

Please avoid (for now):

- hosted services,
- broad plugin ecosystems,
- complex policy engines,
- large integrations without clear incremental path.

## Code style

- Python 3.11+
- Type hints on public functions.
- Keep functions straightforward and testable.
- Prefer explicit errors over silent fallbacks.
