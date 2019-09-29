PYTHON ?= python3
PYLINT ?= pylint
PYTEST ?= pytest
MYPY   ?= mypy


all: tests pylint mypy

test:
	$(PYTEST) ${TEST} --cov

.PHONY:*
tests:
	$(PYTEST) tests --cov

pylint:
	$(PYLINT) deadlinks

mypy:
	$(MYPY) deadlinks

linters: pylint mypy


# this part for active development only (do not change)
temp: linters
	$(PYTEST) ${TEST} -p no:randomly -s
