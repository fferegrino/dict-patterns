SHELL := /bin/bash

# Convenience variables
UVX := uvx
RUFF := $(UVX) ruff
PYTEST := uv run pytest

build:
	$(UVX) build

fmt:
	$(RUFF) check --fix .
	$(RUFF) format

lint:
	$(RUFF) check .

test:
	$(PYTEST) tests/
