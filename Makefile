ESC			:=	\033
RESET			:=	$(ESC)[0m

GREEN			:=	$(ESC)[0;32m
YELLOW			:=	$(ESC)[0;33m
RED			:=	$(ESC)[0;31m
BLUE			:=	$(ESC)[0;34m

BOLD			:=	$(ESC)[1m

UV				?=	uv
PYTHON			?=	python
APP				?=	test.py
LINT_TARGETS	?=	src test.py

.PHONY: install run lint clean

install:
	@printf "$(BLUE)$(BOLD)[install]$(RESET) Installing dependencies\n"
	@$(UV) sync --active

run:
	@printf "$(GREEN)$(BOLD)[run]$(RESET) Starting application\n"
	@$(UV) run $(PYTHON) $(APP)

lint:
	@printf "$(YELLOW)$(BOLD)[lint]$(RESET) Running mypy and flake8\n"
	@$(UV) run mypy $(LINT_TARGETS)
	@$(UV) run flake8 $(LINT_TARGETS)

clean:
	@printf "$(RED)$(BOLD)[clean]$(RESET) Removing Python caches\n"
	@find . -type d \( -name '__pycache__' -o -name '.mypy_cache' -o -name '.pytest_cache' -o -name '.ruff_cache' \) -prune -exec rm -rf {} +
	@find . -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
