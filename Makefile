# Configuration

UV            ?= uv
PYTHON        ?= python
APP           ?= -m src
LINT_TARGETS  ?= .

.PHONY: install run debug lint lint-strict clean


# Install

install:
	@printf '\033[0;34m[install]\033[0m Installing dependencies\n'
	@$(UV) sync --active


# Run

run:
	@printf '\033[0;32m[run]\033[0m Starting application\n'
	@$(UV) run $(PYTHON) $(APP)


# Debug

debug:
	@printf '\033[0;35m[debug]\033[0m Starting application in debug mode\n'
	@$(UV) run $(PYTHON) -m pdb $(APP)


# Lint

lint:
	@printf '\033[0;33m[lint]\033[0m Running mypy\n'
	@$(UV) run mypy $(LINT_TARGETS) --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@printf '\033[0;33m[lint]\033[0m Running flake8\n'
	@$(UV) run flake8 $(LINT_TARGETS)


# Lint Strict

lint-strict:
	@printf '\033[0;33m[lint-strict]\033[0m Running mypy strictly\n'
	@$(UV) run mypy $(LINT_TARGETS) --strict
	@printf '\033[0;33m[lint-strict]\033[0m Running flake8\n'
	@$(UV) run flake8 $(LINT_TARGETS)


# Clean

clean:
	@printf '\033[0;31m[clean]\033[0m Removing Python caches\n'
	@find . -type d \( \
		-name '__pycache__' \
		-o -name '.mypy_cache' \
		-o -name '.pytest_cache' \
		-o -name '.ruff_cache' \
	\) -prune -exec rm -rf {} +
	@find . -type f \( \
		-name '*.pyc' \
		-o -name '*.pyo' \
	\) -delete