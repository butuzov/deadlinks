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
	 	pytest . --cov=$(PACKAGE) -n12 --randomly-dont-reorganize --verbose -ra --ff -x;\
	fi

coverage:
	pytest . --cov=$(PACKAGE)

pylint:
	pylint $(PACKAGE)

pylint-details:
	pylint $(PACKAGE) -r y

mypy:
	mypy $(PACKAGE)

# @ codacy remark linter
remark:
	@docker run -it -v "${PWD}:/src" codacy/codacy-remark-lint:latest;
	@docker rm `docker ps -q --filter status=exited --filter ancestor=codacy/codacy-remark-lint:latest` 1> /dev/null

lints: pylint mypy

# @ build procedures
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
