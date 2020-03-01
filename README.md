# deadlinks

[![PyPI](https://img.shields.io/pypi/v/deadlinks)](https://pypi.org/project/deadlinks/)
[![Travis (.org)](https://img.shields.io/travis/butuzov/deadlinks/develop)](https://travis-ci.org/butuzov/deadlinks)
[![codecov](https://codecov.io/gh/butuzov/deadlinks/branch/develop/graph/badge.svg)](https://codecov.io/gh/butuzov/deadlinks)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/cff8901ed5974425a61dff833f8f81b8)](https://codacy.com/manual/butuzov/deadlinks)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/deadlinks)](https://pypi.org/project/deadlinks/)
[![PyPI - License](https://img.shields.io/badge/license-Apache%202-red)](https://pypi.org/project/deadlinks/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/deadlinks)](https://pypi.org/project/deadlinks/)

---
Health checks for your documentation links.

![](https://butuzov.github.io/deadlinks/deadlinks.gif)

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

# if you using Python 3.5 on the mac, install new version of pip
curl https://bootstrap.pypa.io/get-pip.py | python3.5
# if you using other version, just upgrade pip
pip install --upgrade pip

# in case if you developing within forked repository
cd /home/user/deadlinks-fork
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
