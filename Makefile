.PHONY: freeze
freeze:
	pip freeze > requirements.txt

.PHONY: install
install:
	pip install -U pip
	pip install -U -r requirements.txt

.PHONY: format
format:
	ruff format .

.PHONY: lint
lint:
	ruff check .

.PHONY: typecheck
typecheck:
	mypy .
