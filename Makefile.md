# Makefile Help

Installs:
  * install               Installs development version.

Tests and Continues Integration:
  * all                   Run (almost) all checks.
  * tests                 pytest (travis and local versions)
  * pylint                pylint static checks
  * coverage              pylint static checks with coverage output
  * pylint-details        pylint static checks in report mode
  * mypy                  mypy static checks
  * lints                 Pipeline: pylint -> mypy
  * codacity-config       Codacity Config validation
  * codacity              Codacity Checks (slow)

Documentation:
  * docs                  Pipeline: gen-docs -> browse -> documentation
  * gen-docs              Runs Sphinx and Generate Documentation
  * documentation         Starts Web Server from Docs Directory
  * browse                Open URL of the Documentation Server

Deployments:
  * build                 Build package
  * clean                 Clean
  * pre-deploy            Install `wheel` and `twine`
  * deploy-test           Deploy to test PyPi server
  * deploy-prod           Deploy to production PyPi server
  * brew                  Create Brew formula and run brew tests
  * brew-update-prepare   Prepare Formula repository

Docker:
  * docker-build-local    Build Local Docker image
  * docker-check-local    Check deadlinks version in "local" image
  * docker-check-dev      Check deadlinks version in "dev" image
  * docker-check-latest   Check deadlinks version in "latest" image
