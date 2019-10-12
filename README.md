# deadlinks

[![Travis (.org)](https://img.shields.io/travis/butuzov/deadlinks/features-beter_indexation)](https://travis-ci.org/butuzov/deadlinks)
[![codecov](https://codecov.io/gh/butuzov/deadlinks/branch/develop/graph/badge.svg)](https://codecov.io/gh/butuzov/deadlinks)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/cff8901ed5974425a61dff833f8f81b8)](https://codacy.com/manual/butuzov/deadlinks)

---

**deadlinks** is a simple cli tool to check your documentation/website for deadlinks.

## Features

-   Concurrent and recursive checks
-   External links checks
-   Checking links within base url path
-   Retries in the case of `502`, `503` and `504` http errors

## Installing (development)

### From Source (Python 3.5)

While developing on mac with Python 3.5 I have found that simple install from source doesn't work, as expected.

```bash
# installation into virtual environment
python3.5 -m venv .venv
source .venv/bin/activate

# update pip
curl https://bootstrap.pypa.io/get-pip.py | python3.5
# we expect to get pip version above 19.2.3
pip --version

# clone repo
git clone https://github.com/butuzov/deadlinks.git
cd deadlinks
git checkout develop
pip install -r requirments.txt
python setup.py install
```

### From Source (Python 3.6, 3.7)

```bash
# installation into virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install git+https://github.com/butuzov/deadlinks.git@develop
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

Here is a quick start guide to contributing to `deadlinks`

-   Fork `deadlinks` repository.
-   Create `feature` branch based on `develop`.
-   Implement your feature and test it with `make tests` and `make lints`.
-   Create `pull request` back to `development` branch.

All your contributions are welcome!

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
