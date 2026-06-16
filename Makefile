PACKAGE_NAME = femethods
PACKAGE_PATH = src/$(PACKAGE_NAME)

.PHONY: install docs lint-html tests


install:
	uv sync --extra docs

# ============= BUILD AND UPLOAD COMMANDS =============
.PHONY: build
build:
	uv build

upload:
	uv run twine upload --repository-url https://upload.pypi.org/legacy/ dist/*


# ============= DOCS =============
docs:
	cd docs && uv run make html


# ============= FORMATTING AND LINTING =============
format:
	uv run isort $(PACKAGE_PATH)
	uv run black $(PACKAGE_PATH)

format-tests:
	uv run isort tests
	uv run black tests

format-all:
	uv run isort $(PACKAGE_PATH)
	uv run black $(PACKAGE_PATH)
	uv run isort tests
	uv run black tests


# ============= VALIDATION =============
pyproject:
	uv run validate-pyproject pyproject.toml
	uv run pyproject-fmt pyproject.toml


# ============= LINTING =============
lint:
	uv run pylint $(PACKAGE_PATH) --disable=fixme

lint-tests:
	uv run pylint tests

lint-all:
	uv run pylint $(PACKAGE_PATH)
	uv run pylint tests

lint-ci:
	uv run flake8 $(PACKAGE_PATH) --count --select=E9,F63,F7,F82 --show-source --statistics
	uv run flake8 $(PACKAGE_PATH) --count --max-complexity=10 --max-line-length=127 --statistics

	uv run flake8 tests --count --select=E9,F63,F7,F82 --show-source --statistics
	uv run flake8 tests --count --max-complexity=10 --max-line-length=127 --statistics


# ============= RUNNING TESTS =============
tests:
	uv run pytest tests

tests-cov:
	uv run pytest --cov-report html --cov=$(PACKAGE_NAME) tests

tests-unit:
	uv run pytest tests/unit

tests-unit-cov:
	uv run pytest --cov-report html --cov=$(PACKAGE_NAME) tests/unit

tests-int:
	uv run pytest tests/integration

tests-int-cov:
	uv run pytest --cov-report html --cov=$(PACKAGE_NAME) tests/integration

tests-core:
	uv run pytest tests/$(PACKAGE_NAME)/core

tests-core-cov:
	uv run pytest --cov-report html --cov=$(PACKAGE_NAME) tests/$(PACKAGE_NAME)/core

tests-ci-cov:
	uv run coverage run -m pytest tests
	uv run coverage report --fail-under=100
