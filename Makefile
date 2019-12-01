PYTHON ?= python3
PACKAGE?= deadlinks
PYLINT ?= pylint
MYPY   ?= mypy
BUILD  = build
DIST   = dist
BRANCH = $(shell git rev-parse --abbrev-ref HEAD)
COMMIT = $(shell git rev-list --abbrev-commit -1 HEAD)
TAGGED = $(shell git describe)

.PHONY: help

help:
	@cat Makefile.md

# ~~~ Install ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

requirements:
	@python3 -m pip install -q -r requirements.txt

install: clean requirements
	DEADLINKS_BRANCH=$(BRANCH) \
	DEADLINKS_COMMIT=$(COMMIT) \
	DEADLINKS_TAGGED=$(TAGGED) \
	python3 setup.py develop


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

all: clean install
	@echo "Running All Checks"
	@echo "Running mypy static analizer"
	@make mypy
	@echo "Running pylint static analizer"
	@make pylint-details
	@make docker-build-local

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
	ghp -root=build/sphinx/html -port=5678

gen-docs:
	python3 setup.py build_sphinx -c docs

docs: gen-docs browse  documentation

# ~~~ Brew ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

brew:
	@python3 -m pip install --upgrade requests Jinja2 -q
	@python3 setup.py brew_formula_create
	@python3 -m pip uninstall requests chardet Jinja2 MarkupSafe urllib3 certifi idna -y -q
	@brew reinstall deadlinks.rb
	@brew audit --new-formula deadlinks.rb
	@brew audit --strict deadlinks.rb
	@brew test --verbose --debug deadlinks.rb
	@brew uninstall deadlinks


brew-update-prepare: brew
	@git clone https://github.com/butuzov/homebrew-deadlinks
	@cp deadlinks.rb homebrew-deadlinks/Formula/deadlinks.rb

# ~~~ Deployments ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

clean:
	@echo "Cleanup Temporary Files"
	@rm -rf ${DIST}
	@rm -rf ${BUILD}
	@rm -f deadlinks/__develop__.py

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

# enable `--pull=alway` once it will be available https://github.com/docker/cli/pull/1498
# status - 19.03 not avaialbe.
docker-check-dev:
	docker run --rm -it --network=host  butuzov/deadlinks:dev --version

docker-check-latest:
	docker run --rm -it --network=host  butuzov/deadlinks:latest --version
