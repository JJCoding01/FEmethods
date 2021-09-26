PACKAGE_NAME=femethods

.PHONY: install docs lint-html tests
.PHONY: build

docs:
	cd docs && make html

install:
	python setup.py install

format:
	black $(PACKAGE_NAME)
	isort $(PACKAGE_NAME)

format-tests:
	black tests
	isort tests

format-all:
	black $(PACKAGE_NAME)
	isort $(PACKAGE_NAME)
	black tests
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
	pytest tests/integration

tests-int-cov:
	pytest --cov-report html --cov=$(PACKAGE_NAME) tests/integration

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
