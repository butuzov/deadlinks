PYTHON ?= python3
PACKAGE?= deadlinks
PYLINT ?= pylint
MYPY   ?= mypy


.PHONY:*

all:
	pytest . -s

travis-tests:
	pytest . --cov=$(PACKAGE)

tests:
	pytest . --cov=$(PACKAGE) -n 10

coverage:
	pytest . --cov=$(PACKAGE)

tests-fast:
	pytest --cov -n 10

pylint:
	pylint $(PACKAGE)

pylint-details:
	pylint $(PACKAGE) -r y

mypy:
	mypy $(PACKAGE)

lints: pylint mypy
