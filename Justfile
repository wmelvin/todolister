@default:
  @just --list

@build: checks test
  uv build

# Check formatting with ruff
@check:
  uv run ruff format --check

# Run check and lint
@checks: check lint

@clean:
  -rm dist/*

# Apply ruff format
@format:
  uv run ruff format

# Check code with ruff
@lint:
  uv run ruff check

@test: 
  uv run pytest

# @tox:
#   uv run tox
