PYTHON ?= python3
PACKAGE?= deadlinks
PYLINT ?= pylint
MYPY   ?= mypy
BUILD  = build
DIST   = dist
BRANCH = $(shell git rev-parse --abbrev-ref HEAD)
COMMIT = $(shell git rev-list --abbrev-commit -1 HEAD)

.PHONY: help

help:
	@cat Makefile.md

# ~~~ Tests and Continues Integration ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

lints: pylint mypy

all: tests lints

# Codacity Code Analysis
# https://github.com/codacy/codacy-analysis-cli#install
# https://support.codacy.com/hc/en-us/articles/115002130625-Codacy-Configuration-File
codacity-config:
	codacy-analysis-cli validate-configuration --directory `pwd`

codacity:
	codacy-analysis-cli analyse

# ~~~ Documentation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

browse:
	open http://localhost:5678

documentation:
	ghp -root=build/dirhtml -port=5678

gen-docs:
	sphinx-build -M dirhtml docs build -c docs

docs: gen-docs browse  documentation

# ~~~ Deployments ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

clean:
	rm -rf ${DIST}
	rm -rf ${BUILD}

pre-deploy:
	python3 -m pip install --upgrade wheel twine -q

build: pre-deploy clean
	python3 setup.py sdist bdist_wheel

deploy-test: pre-deploy
	@if [ ! -z ${DEADLINKS_VERSION} ]; then\
		twine upload -u ${PYPI_TEST_USER} --repository-url https://test.pypi.org/legacy/ dist/*;\
	else \
		echo "You need to provide DEADLINKS_VERSION to run this command";\
	fi

deploy-prod: pre-deploy build
	twine upload -u ${PYPI_PROD_USER} --repository-url https://upload.pypi.org/legacy/ dist/*;\


# ~~~ Docker  ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

docker-build-local: clean
	docker tag butuzov/deadlinks:local butuzov/deadlinks:prev
	docker build . -t butuzov/deadlinks:local
	docker rmi butuzov/deadlinks:prev

docker-check-local: docker-build-local
	docker run --rm -it --network=host  butuzov/deadlinks:local --version

docker-check-dev:
	docker run --rm -it --network=host  butuzov/deadlinks:dev --version

docker-check-latest:
	docker run --rm -it --network=host  butuzov/deadlinks:latest --version
