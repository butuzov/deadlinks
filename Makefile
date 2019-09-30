PYTHON ?= python3
PACKAGE?= deadlinks
PYLINT ?= pylint
PYTEST ?= pytest
MYPY   ?= mypy


.PHONY:*

all: tests lints

# running pytest with --cov enabled
tests:
	$(PYTEST) --cov

# running pytest with --cov in 10 threads
tests-fast:
	$(PYTEST) --cov -n 10

pylint:
	$(PYLINT) $(PACKAGE)

# pylint with reporting on
pylint-details:
	$(PYLINT) $(PACKAGE) -r y

mypy:
	$(MYPY) $(PACKAGE)

# all linters
lints: pylint mypy
