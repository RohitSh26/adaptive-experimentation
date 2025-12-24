# Contributing

Thanks for your interest in contributing!

## Development setup (recommended)
This repo supports VS Code Dev Containers.

1. Open the repository in VS Code
2. Reopen in Container
3. Run:
   - `uv sync`
   - `uv run ruff check .`
   - `uv run pytest`

## Pull requests
- Keep PRs small and focused
- Add tests for new behavior
- Ensure `ruff` and `pytest` pass
- Prefer backward-compatible changes when possible

## Code style
- Python 3.10+
- `ruff` for linting/formatting
- `pytest` for tests

## Reporting issues
Please include:
- what you expected
- what happened
- minimal reproduction steps
- Python version and OS
