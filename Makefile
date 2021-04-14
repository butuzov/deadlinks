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
PROCS  = $(shell nproc)

export PATH   := $(PWD)/bin:$(PATH)
export SHELL  := bash

# --- Deadlinks: restarted ---------------------------------------------------------------

help: dep-gawk
	@ echo "=============================================================================="
	@ echo " Makefile: github.com/butuzov/deadlinks - links checker                       "
	@ echo "=============================================================================="
	@ cat $(MAKEFILE_LIST) | \
		grep -E '^# ~~~ .*? [~]+$$|^[a-zA-Z0-9_-]+:.*?## .*$$' | \
		gawk '{if ( $$1=="#" ) { \
			match($$0, /^# ~~~ (.+?) [~]+$$/, a);\
			{print "\n", a[1], ""}\
		} else { \
			match($$0, /^([a-zA-Z/_-]+):.*?## (.*)$$/, a); \
			{printf "  - \033[32m%-20s\033[0m %s\n",   a[1], a[2]} \
 		}}'
	@echo ""



ghp:
	@go get -u github.com/butuzov/ghp

# ~~~ Install ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

deps: venv ## install requiements
	$(PYTHON) -m pip install -q -r requirements.txt


dev-env: deps clean ## Install Development Version
	pip uninstall deadlinks -y
	pip install -e .


# ~~~ Tests and Continues Integration ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~




#   make tests -> run tests + click integration
#   make all -> runs all tests
#   make docker-tests -> runs docket tests
#   make brew-tests -> runs installs bre and runs brew tests
#   make integration -> runs click/docker/brew

.PHONY: tests
tests: venv ## Run package tests (w/o integration tests)
	@if [ ! -z "${GITHUB_ACTIONS}" ]; then\
		$(PYTEST) . -m "not (docker or brew)" -vrax --cov=$(PACKAGE);\
	else\
		$(PYTEST) . -m "not (docker or brew)" -n$(PROCS)  --cov=$(PACKAGE);\
	fi

all: ## All Tests (with integration tests)
	$(PYTEST) . --randomly-dont-reorganize -n$(PROCS) \
		--maxfail=10 -s -vrax --cov=$(PACKAGE);


coverage: tests ## Coverage Report (same as `make tests`)

integration: ## Integration Tests
	$(PYTEST) . -m "docker or brew or click" -n$(PROCS)  --cov=$(PACKAGE);

# ~~~ Linting ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pylint: ## Linter: pylint
	$(PYTHON) -m pylint $(PACKAGE)

pylint-full: ## Linter: pylint (with details report)
	$(PYTHON) -m pylint $(PACKAGE) -r y

mypy: ## Linter: mypy
	$(PYTHON) -m mypy $(PACKAGE) --config .github/configs/mypy.ini

linters: pylint mypy ### All Important Linters (pylint/mypy)


codacy-install: ## Brew Install Codacy Linters (Docker required)
	brew install codacy-analysis-cli

codacy-uninstall: ## Brew Install Codacy Linters (Docker required)
	@docker images | grep [c]odacy | awk '{print $3}' |  xargs -L1 docker rmi
	brew uninstall codacy-analysis-cli

# https://bandit.readthedocs.io/en/latest/plugins/index.html
bandit: ## Codacy Linter: Bandit (python)
	codacy-analysis-cli analyse --tool bandit

remark: ## Codacy Linter: Remark (markdown)
	codacy-analysis-cli analyse --tool remark-int

# https://prospector.readthedocs.io/en/master/
prospector: ## Codacy Linter: Prospector (python)
	codacy-analysis-cli analyse --tool prospector


# Codacy Code Analysis
# https://github.com/codacy/codacy-analysis-cli#install
# https://support.codacy.com/hc/en-us/articles/115002130625
codacity-config: ## Codacy: Check .codacy.yml
	codacy-analysis-cli validate-configuration --directory `pwd`

codacy: bandit prospector docker remark ## Codacy: Linters (All)

hadolint-install: ## Docker: Install hadolint  (Dockerfile)
	@brew install hadolint

# https://github.com/hadolint/hadolint
hadolint-check: ## Docker: Run hadolint (Dockerfile)
	hadolint --config .github/configs/hadolint.yaml Dockerfile


# ~~~ Documentation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
.PHONY: docs
docs: ## Documentation Build Pipeline
	$(MAKE) docs-build
	$(MAKE) docs-browse
	$(MAKE) docs-ci

docs-browse: ghp
	ghp -root=build/html -port=5678 &
	open http://localhost:5678

docs-build: venv ## Generate Documentation

	@$(PYTHON) -m pip install Sphinx sphinx-rtd-theme -q;
	@$(PYTHON) -m pip install recommonmark sphinx-markdown-tables -q;
	sphinx-build docs build/html -qW --keep-going;

docs-ci: venv ## Documentation CI
	deadlinks internal --root=build/html --no-progress  --fiff

docs-stop: ## Documentation WebServer: Stop
	@ps -a | grep '[g]hp -root=build/html -port=5678' --color=never \
		| awk '{print $$1}' | xargs -L1 kill -9

# ~~~ Brew (Package Manager for macoS) ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

brew-env:
	@ $(PYTHON) -m venv .brew;
	@ source .brew/bin/activate;
	@ $(PYTHON) -m pip install --upgrade pip requests Jinja2 -q;\


brew-prod: brew-env ## Create & Install Formula (Production)
	@brew uninstall deadlinks -f
	@echo "Creating formula (prod)..."
	@ $(PYTHON) make_brew_formula.py
	$(MAKE) brew-audit
	@echo "Formula ready to be published"

brew-dev: build-prod  ## Create & Install Formula (Development)
	@brew uninstall deadlinks -f
	@echo "Creating formula (dev)..."
	$(MAKE) brew-web-start
	@ $(PYTHON) make_brew_formula.py --dev
	@ $(MAKE) brew-audit
	@ $(MAKE) brew-install
	$(MAKE) brew-web-stop

brew-install: ## Local Formula Installation
	@if [ -f "deadlinks.rb" ]; then\
		sleep 5;\
		brew install --include-test deadlinks.rb;\
	else\
		echo ">>>>>> deadlinks.rb not found";\
		exit 1;\
	fi

brew-audit: ## Formula: Audit
	@if [ -f "deadlinks.rb" ]; then\
		brew audit --new-formula deadlinks.rb;\
		brew audit --strict deadlinks.rb;\
	else\
		echo ">>>>>> deadlinks.rb not found";\
		exit 1;\
	fi

brew-web-start: ghp # Start Server (Serves dev pacakge)
	@ghp -port=8878  2>&1 1>/dev/null &

brew-web-stop:      # Stop Server (Serves dev pacakge)
	@ps -a | grep '[g]hp -port=8878' --color=never \
		| awk '{print $$1}' | xargs -L1 kill -9

brew-tests: venv brew-dev clean dev-env
	$(PYTEST) . -m "brew" -n$(PROCS)  --cov=$(PACKAGE);

# ~~~ Deployments ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

build-prod: venv clean ## Build disto (source & wheel) - Production
	@ $(PYTHON) setup.py sdist bdist_wheel > /dev/null 2>&1

build-dev: venv clean ## Build disto (source & wheel) - Development
	@ \
	DEADLINKS_BRANCH=$(BRANCH) \
	DEADLINKS_COMMIT=$(COMMIT) \
	DEADLINKS_TAGGED=$(TAGGED) \
	$(PYTHON) setup.py sdist bdist_wheel > /dev/null 2>&1

clean: ## Cleanup Build artifacts
	@echo "Cleanup Temporary Files"
	@rm -rf ${DIST}
	@rm -rf ${BUILD}
	@rm -f deadlinks/__develop__.py

deploy:
	@ $(PYTHON) -m pip install --upgrade wheel twine -q

deploy-test: deploy build-dev ## PyPi Deploy (test.pypi.org)
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*;\

deploy-prod: deploy build-prod ## PyPi Deploy (pypi.org)
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*;\

pre-depeloy-check: venv clean deps ## Install Development Version
	$(PYTHON) -m pip uninstall deadlinks -y
	DEADLINKS_BRANCH=$(BRANCH) \
	DEADLINKS_COMMIT=$(COMMIT) \
	DEADLINKS_TAGGED=$(TAGGED) \
	$(PYTHON) setup.py develop -q 2>&1 1> /dev/null

# ~~~ Docker ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

docker-clean: ## Clean untagged images
	@docker ps -q -f "status=exited" | xargs -L1 docker rm
	@docker images -q -f "dangling=true" | xargs -L1 docker rmi
	@docker images | grep [b]utuzov/deadlinks | awk '{print $3}' |  xargs -L1 docker rmi

docker-build: clean ## Build Image
	@docker build . -t deadlinks:local --no-cache

docker-tests: venv ## Docker Integration Testing
	$(PYTEST) . -m "docker" -n$(PROCS);

docker: ## Quick test
	@docker run --rm -it --network=host  deadlinks:local --version



# Helper Mehtods ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


dep-gawk:
	@ if [ -z "$(shell command -v gawk)" ]; then  \
		if [ -x /usr/local/bin/brew ]; then $(MAKE) _brew_gawk_install; exit 0; fi; \
		if [ -x /usr/bin/apt-get ]; then $(MAKE) _ubuntu_gawk_install; exit 0; fi; \
		if [ -x /usr/bin/yum ]; then  $(MAKE) _centos_gawk_install; exit 0; fi; \
		if [ -x /sbin/apk ]; then  $(MAKE) _alpine_gawk_install; exit 0; fi; \
		echo  "GNU Awk Required.";\
		exit 1; \
	fi

_brew_gawk_install:
	@ echo "Instaling gawk using brew... "
	@ brew install gawk --quiet
	@ echo "done"

_ubuntu_gawk_install:
	@ echo "Instaling gawk using apt-get... "
	@ apt-get -q install gawk -y
	@ echo "done"

_alpine_gawk_install:
	@ echo "Instaling gawk using yum... "
	@ apk add --update --no-cache gawk
	@ echo "done"

_centos_gawk_install:
	@ echo "Instaling gawk using yum... "
	@ yum install -q -y gawk;
	@ echo "done"


venv:
	@ if [[ ! -z "${GITHUB_ENV}" ]]; then \
		echo ">>>>> This is CI. Cplease Continue!";\
		exit 0;\
	elif [[   -z "${VIRTUAL_ENV}" ]]; then\
		echo ">>>>> You need to run this test in virtual environment. Abort!";\
		exit 1;\
	else \
		echo ">>>>> Oh Hi Mark";\
	fi
