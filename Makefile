PYTHON ?= python3
PACKAGE?= deadlinks
PYLINT ?= pylint
MYPY   ?= mypy


.PHONY:*

all: tests

tests:
	@if [ ! -z "${TRAVIS_BUILD_NUMBER}" ]; then\
	 	pytest . --verbose -ra -x;\
	else\
	 	pytest . --cov=$(PACKAGE) -n 4 --verbose -ra --ff -x;\
	fi

coverage:
	pytest . --cov=$(PACKAGE)

pylint:
	pylint $(PACKAGE)

pylint-details:
	pylint $(PACKAGE) -r y

mypy:
	mypy $(PACKAGE)

lints: pylint mypy
