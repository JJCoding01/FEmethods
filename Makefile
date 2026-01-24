PACKAGE_NAME=femethods

.PHONY: install docs lint-html tests
.PHONY: build

build:
	python setup.py sdist
	python setup.py bdist_wheel

docs:
	cd docs && make html

format:
	isort $(PACKAGE_NAME)
	black $(PACKAGE_NAME)

format-tests:
	isort tests
	black tests

format-all:
	isort $(PACKAGE_NAME)
	black $(PACKAGE_NAME)
	isort tests
	black tests

pyproject:
	validate-pyproject pyproject.toml
	pyproject-fmt pyproject.toml

install:
	python setup.py install

lint:
	pylint $(PACKAGE_NAME) --disable=fixme

lint-tests:
	pylint tests

lint-all:
	pylint $(PACKAGE_NAME)
	pylint tests

lint-ci:
	flake8 $(PACKAGE_NAME) --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 $(PACKAGE_NAME) --count --max-complexity=10 --max-line-length=127 --statistics

	flake8 tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 tests --count --max-complexity=10 --max-line-length=127 --statistics

tests:
	pytest tests

tests-cov:
	pytest --cov-report html --cov=$(PACKAGE_NAME) tests

tests-unit:
	pytest tests/unit

tests-unit-cov:
	pytest --cov-report html --cov=$(PACKAGE_NAME) tests/unit

tests-int:
	pytest tests/integration

tests-int-cov:
	pytest --cov-report html --cov=$(PACKAGE_NAME) tests/integration

tests-core:
	pytest tests/$(PACKAGE_NAME)/core

tests-core-cov:
	pytest --cov-report html --cov=$(PACKAGE_NAME) tests/$(PACKAGE_NAME)/core

tests-ci-cov:
	coverage run -m --source=actions pytest tests
	coverage report --fail-under=100

upload:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
