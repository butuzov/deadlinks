# deadlinks

[![PyPI](https://img.shields.io/pypi/v/deadlinks)](https://pypi.org/project/deadlinks/)
[![Github (CI)](https://img.shields.io/github/actions/workflow/status/butuzov/deadlinks/main.yml?branch=master)](https://github.com/butuzov/deadlinks/actions/workflows/main.yaml)
[![codecov](https://codecov.io/gh/butuzov/deadlinks/branch/master/graph/badge.svg)](https://codecov.io/gh/butuzov/deadlinks)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/deadlinks)](https://pypi.org/project/deadlinks/)
[![PyPI - License](https://img.shields.io/badge/license-Apache%202-red)](https://pypi.org/project/deadlinks/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/deadlinks)](https://pypi.org/project/deadlinks/)

---
Health checks for your documentation links.


[![SWUbanner](https://raw.githubusercontent.com/vshymanskyy/StandWithUkraine/main/banner-personal-page.svg)]([https://vshymanskyy.github.io/StandWithUkraine](https://stand-with-ukraine.pp.ua/))

## Features

-   Concurrent and recursive checks
-   Respect robots.txt restrictions (content only)
-   External links checks
-   Checking links within base url path
-   Retries in the case of `502`, `503` and `504` http errors

## Installing

### Using package installer for Python

```bash
# using pip - package installer for Python
pip install deadlinks
```

### Mac

```bash
# we using custom tap to install deadlinks
brew install butuzov/deadlinks/deadlinks
```

### Using forked repo for development propose.

```bash
# activate virtual environment to keep your local site-packages clean.
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip

# in case if you developing within forked repository
cd /home/path/to/deadlinks
pip install -r requirements.txt
pip install -e .
```

## Usage

See more examples at [docs](https://deadlinks.readthedocs.io/en/stable/)

```bash
# Check links (including external) at http://gobyexample.com/ in 10 threads,
# but not ones that leading to domains play.golang.org or github.com
deadlinks gobyexample.com -n 10 -e -d play.golang.org -d github.com

# Limiting check only to links found within /docs path.
deadlinks http://localhost:1313/docs

# Running checks for all local links that belong to a domain.
deadlinks http://localhost:1313/docs/ -n 10 --full-site-check

# Checking local html files
deadlinks internal -n 10 --root=/var/html

# Help yourself
deadlinks --help
```

## Contributing

Here is a quick start guide to contributing to `deadlinks`

-   Fork `deadlinks` repository.
-   Create `feature` branch based on `develop`.
-   Install package using [development](#using-forked-repo-for-development-propose) instructions.
-   Implement your feature and test it with `make tests` and `make lints`.
-   Create `pull request` back to `development` branch.

All your contributions are welcome!
