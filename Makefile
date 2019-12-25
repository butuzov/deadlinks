PYTHON ?= python3
PACKAGE?= deadlinks
PYLINT ?= pylint
PYTEST ?= $(PYTHON) -m pytest
MYPY   ?= mypy
BUILD  = build
DIST   = dist
BRANCH = $(shell git rev-parse --abbrev-ref HEAD)
COMMIT = $(shell git rev-list --abbrev-commit -1 HEAD)
TAGGED = $(shell git describe)

.PHONY: help

help:
	@cat $(MAKEFILE_LIST) | \
		grep -E '^# ~~~ .*? [~]+$$|^[a-zA-Z0-9_-]+:.*?## .*$$' | \
		awk '{if ( $$1=="#" ) {\
			match($$0, /^# ~~~ (.+?) [~]+$$/, a);\
			{print "\n", a[1], "\n"}\
		} else { \
			match($$0, /^([a-zA-Z-]+):.*?## (.*)$$/, a); \
			{printf "  - \033[32m%-20s\033[0m %s\n",   a[1], a[2]} \
		};}'

# ~~~ Install ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

install-dev: clean requirements ## Install Development version
	DEADLINKS_BRANCH=$(BRANCH) \
	DEADLINKS_COMMIT=$(COMMIT) \
	DEADLINKS_TAGGED=$(TAGGED) \
	$(PYTHON) setup.py develop -q 2>&1 1> /dev/null

requirements: ## Install requirements.txt
	@ $(PYTHON) -m pip install -q -r requirements.txt

# ~~~ Tests and Continues Integration ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# all: clean install-dev ## Running All Checks
# 	@echo "===> Running Standard Lints";



.PHONY: tests
tests: ## Run PyTest for CI/Localy
	@if [ ! -z "${TRAVIS_BUILD_NUMBER}" ]; then\
	 	pytest . -m "not e2e" -vrax --cov=$(PACKAGE);\
	else\
	 	pytest . -m "not e2e" -n12  --cov=$(PACKAGE);\
	fi

all: ## All Tests (w/o integration tests)
	$(PYTEST) . --randomly-dont-reorganize -n12 \
		--maxfail=10 -s -vrax --cov=$(PACKAGE);

e2e: ## Integration tests (brew, docker)
	$(PYTEST) . -m "e2e" -n12  --cov=$(PACKAGE);


full-e2e: ## Integration tests (brew, docker) Skipp interfaces creation

	@ $(MAKE) brew-uninstall
	@ $(MAKE) brew-dev
	@ $(MAKE) brew-install
	@ $(MAKE) brew-audit

	@ $(MAKE) docker-build

	@ $(MAKE) e2e

	@ $(MAKE) brew-web-stop


coverage: ## Run PyTest with coverage report
	$(PYTHON) -m pytest . -m "not e2e" --cov=$(PACKAGE)

linter-pylint: ## Run Linter: pylint
	$(PYTHON) -m pylint $(PACKAGE) --rcfile=.github/configs/pylintrc

linter-pylint-full: ## Run Linter: pylint (with details report)
	$(PYTHON) -m pylint $(PACKAGE) -r y --rcfile=.github/configs/pylintrc

linter-mypy: ## Run Linter: mypy
	$(PYTHON) -m mypy $(PACKAGE) --config .github/configs/mypy.ini

linters: linter-pylint linter-mypy ### Run All Linters

codacy: bandit prospector docker remark ## Codacy: run all codacy linters (bandit, remark, docker, prospector)

# https://bandit.readthedocs.io/en/latest/plugins/index.html
bandit: ## Codacy Linter: Bandit (python)
	codacy-analysis-cli analyse --tool bandit

remark: ## Codacy Linter: Remark (markdown)
	codacy-analysis-cli analyse --tool remark-int

# https://prospector.readthedocs.io/en/master/
prospector: ## Codacy Linter: Prospector (python)
	codacy-analysis-cli analyse --tool prospector

# https://github.com/hadolint/hadolint
linter-docker: ## Codacy Linter: hadolint (Dockerfile)
	hadolint --config .github/configs/hadolint.yaml Dockerfile

# Codacy Code Analysis
# https://github.com/codacy/codacy-analysis-cli#install
# https://support.codacy.com/hc/en-us/articles/115002130625-Codacy-Configuration-File
codacity-config: ## Codacity: check codacity config
	codacy-analysis-cli validate-configuration --directory `pwd`

# ~~~ Documentation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

docs: gen-docs ## Documentation Pipeline (build->browse->check->serve)
	$(MAKE) browse
	$(MAKE) docs-ci
	$(MAKE) docs-serve

browse:  ## Open documentation server in browser
	open http://localhost:5678

docs-serve: ghp #- Run documentation server
	ghp -root=build/html -port=5678 &

docs-serve-stop: #- Stop documentation server
	@ps -a | grep '[g]hp -root=build/html -port=5678' --color=never \
		| awk '{print $$1}' | xargs -L1 kill -9


gen-docs: ## Generate Documentation
	@if [ -z ${VIRTUAL_ENV} ]; then\
		@ $(PYTHON) -m venv .venv;\
		@ source .venv/bin/activate; \
	fi
	@ $(PYTHON) -m pip install Sphinx sphinx-rtd-theme -q;
	@ $(PYTHON) -m pip install recommonmark sphinx-markdown-tables -q;
	sphinx-build docs build/html -qW --keep-going;

docs-ci: ## Run deadlinks checks for own docs
	deadlinks internal --root=build/html --no-progress --no-colors --fiff

# ~~~ Brew ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

brew-env:
	@ $(PYTHON) -m venv .brew;
	@ source .brew/bin/activate;
	@ $(PYTHON) -m pip install --upgrade pip requests Jinja2 -q;\

brew-web-start: ghp
	@ghp -port=8878  2>&1 1>/dev/null &

brew-web-stop:
	@ps -a | grep '[g]hp port=8878' --color=never \
		| awk '{print $$1}' | xargs -L1 kill -9

brew: brew-env build ## Create Formula: Create (Production)
	@ VIRTUAL_ENV=""
	@ source .brew/bin/activate;
	@ $(PYTHON) make_brew_formula.py

brew-dev: brew-web-start brew-env build-dev ## Create Formula: Create (Development)
	@ VIRTUAL_ENV=""
	@ source .brew/bin/activate;
	@ $(PYTHON) make_brew_formula.py --dev

brew-install: ## Formula: Install
	brew install --include-test deadlinks.rb

brew-uninstall: ## Formula: UnInstall
	@brew list -1 | grep deadlinks --color=never | xargs -I {} sh -c 'brew uninstall {}' 2>&1 1>/dev/null

brew-cleanup: ## Cleanup
	@ VIRTUAL_ENV=""
	@ source .brew/bin/activate;
	@ $(PYTHON) -m pip uninstall requests chardet Jinja2 MarkupSafe urllib3 certifi idna -y -q

brew-audit: ## Formula: Audit
	brew audit --new-formula deadlinks.rb;
	brew audit --strict deadlinks.rb;

brew-dev-pipeline: ## Dev Pipeline (Create/Install/Test/Uninstall)
	$(MAKE) brew-dev
	$(MAKE) brew-uninstall
	$(MAKE) brew-install
	$(MAKE) brew-audit
	$(MAKE) brew-web-stop
	$(MAKE) brew-uninstall

brew-pytest-start: brew-dev brew-uninstall brew-install ## (pytest) Install Pipeline

brew-pytest-final: brew-uninstall brew-web-stop ## (pytest) Finalizer

brew-update-prepare: brew ## Prepare brew for deploying new version.p
	@git clone https://github.com/butuzov/homebrew-deadlinks
	@cp deadlinks.rb homebrew-deadlinks/Formula/deadlinks.rb

# ~~~ Deployments ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

build: pre-deploy clean ## Build disto (source & wheel) - Production
	@ $(PYTHON) setup.py sdist bdist_wheel 1>&2 2> /dev/null

build-dev: pre-deploy clean ## Build disto (source & wheel) - Development
	@ \
	DEADLINKS_BRANCH=$(BRANCH) \
	DEADLINKS_COMMIT=$(COMMIT) \
	DEADLINKS_TAGGED=$(TAGGED) \
	$(PYTHON) setup.py sdist bdist_wheel 1>&2 2>/dev/null

clean: ## Cleanup Build artifacts
	@echo "Cleanup Temporary Files"
	@rm -rf ${DIST}
	@rm -rf ${BUILD}
	@rm -f deadlinks/__develop__.py

pre-deploy: ## Install deploy packages
	@ $(PYTHON) -m pip install --upgrade wheel twine -q


deploy-test: pre-deploy ## PyPi Deploy (test.pypi.org)
	twine upload -u ${PYPI_TEST_USER} --repository-url https://test.pypi.org/legacy/ dist/*;\

deploy-prod: pre-deploy build ## PyPi Deploy (pypi.org)
	twine upload -u ${PYPI_PROD_USER} --repository-url https://upload.pypi.org/legacy/ dist/*;\


# ~~~ Docker ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

docker-clean: ## Clean untagged images
	@docker ps -q -f "status=exited" | xargs -L1 docker rm
	@docker images -q -f "dangling=true" | xargs -L1 docker rmi
	@docker images | grep [b]utuzov/deadlinks | awk '{print $3}' |  xargs -L1 docker rmi

docker-build: clean ## Build Image
	@docker build . -t butuzov/deadlinks:local

docker-local-version:
	@docker run --rm -it --network=host  butuzov/deadlinks:local --version

# enable `--pull=alway` once it will be available https://github.com/docker/cli/pull/1498
# status - 19.03 not avaialbe.


# --- Helpers --- Do Not Show --------------------------------------------------

ghp:
	go get github.com/butuzov/ghp
