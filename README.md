# deadlinks


[![PyPI](https://img.shields.io/pypi/v/deadlinks)](https://pypi.org/project/deadlinks/)
[![Travis (.org)](https://img.shields.io/travis/butuzov/deadlinks/master)](https://travis-ci.org/butuzov/deadlinks)
[![codecov](https://codecov.io/gh/butuzov/deadlinks/branch/master/graph/badge.svg)](https://codecov.io/gh/butuzov/deadlinks)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/cff8901ed5974425a61dff833f8f81b8)](https://codacy.com/manual/butuzov/deadlinks)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/deadlinks)
![PyPI - License](https://img.shields.io/pypi/l/deadlinks?color=%23ecac1b)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/deadlinks)](https://pypi.org/project/deadlinks/)
---

**deadlinks** is a simple cli tool to check your documentation/website for deadlinks.

## Features

-   Concurrent and recursive checks
-   External links checks
-   Checking links within base url path
-   Retries in the case of `502`, `503` and `504` http errors

## Installing

```bash
# using pip - package installer for Python
pip install deadlinks
```

## Usage

See more examples at [docs](docs/examples.md)

```bash
# run 10 instances of crawler against https://gobyexample.com.ua
# with the additional check for the external links (except ones that
# match play.golang.org)
deadlinks https://gobyexample.com.ua -n 10 -e -d play.golang.org

# get more help with
deadlinks --help
```

## Contributing

Your contributions are welcome!

-   Fork `deadlinks` repository
-   Switch to develop and create new branch using tip of
-   Do your changes in new branach
-   Create `pull request` back to `development` branch

## Alternatives

These are a lot of alternative ways to check your website for dead links errors, you can check a [open software](https://github.com/topics/link-checker) or check other options:

| Platform           | Title                      | Link                                                                |
|--------------------|----------------------------|---------------------------------------------------------------------|
| `mac`, `ui`        | Integrity                  | <https://peacockmedia.software/mac/integrity/free.html>             |
| `win`, `ui`        | Xenu's Link Sleuth         | <http://home.snafu.de/tilman/xenulink.html>                         |
| `web`              | Online Broken Link Checker | <https://www.brokenlinkcheck.com/>                                  |
| `web`              | Free Broken Link Tool      | <https://www.deadlinkchecker.com/website-dead-link-checker.asp>     |
| `win`, `ui`        | InterroBot                 | <https://interro.bot/>                                              |
| `go`, `cli`        | muffet                     | <https://github.com/raviqqe/muffet>                                 |
| `cli`, `ui`, `web` | linkchecker                | <https://wummel.github.io/linkchecker>                              |
