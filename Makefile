PYTHON ?= python3
PACKAGE?= deadlinks
PYLINT ?= pylint
MYPY   ?= mypy
BUILD  = build
DIST   = dist

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

clean:
	rm -rf ${DIST}
	rm -rf ${BUILD}

build: clean
	python3 setup.py sdist bdist_wheel

deploy-test: build
	@if [ ! -z ${DEADLINKS_VERSION} ]; then\
		twine upload -u ${PYPI_TEST_USER} --repository-url https://test.pypi.org/legacy/ dist/*;\
	fi

deploy-prod: build
	twine upload -u ${PYPI_PROD_USER} --repository-url https://pypi.org/legacy/ dist/*;
