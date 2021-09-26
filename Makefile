PACKAGE_NAME=femethods

.PHONY: install docs lint-html tests
.PHONY: build

docs:
	cd docs && make html

install:
	python setup.py install

format:
	black $(PACKAGE_NAME) --line-length=79
	isort $(PACKAGE_NAME)

format-tests:
	black tests --line-length=79
	isort tests

format-all:
	black $(PACKAGE_NAME) --line-length=79
	isort $(PACKAGE_NAME)
	black tests --line-length=79
	isort tests

lint:
	pylint $(PACKAGE_NAME)

lint-tests:
	pylint tests

tests:
	pytest tests

tests-cov:
	pytest --cov-report html --cov=$(PACKAGE_NAME) tests

tests-unit:
	pytest tests/$(PACKAGE_NAME)

tests-unit-cov:
	pytest --cov-report html --cov=$(PACKAGE_NAME) tests/$(PACKAGE_NAME)

tests-int:
	pytest "tests/functional tests"

tests-int-cov:
	pytest --cov-report html --cov=$(PACKAGE_NAME) "tests/functional tests"

tests-core:
	pytest tests/$(PACKAGE_NAME)/core

tests-core-cov:
	pytest --cov-report html --cov=$(PACKAGE_NAME) tests/$(PACKAGE_NAME)/core

tests-ci:
	pytest --cov-report html --cov=$(PACKAGE_NAME) tests/$(PACKAGE_NAME) -v

build:
	python setup.py sdist
	python setup.py bdist_wheel

upload:
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*
