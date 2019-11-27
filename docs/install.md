# Installation

You can install and use `deadlinks` in various ways.

## Package installer for Python


``` bash
# Stable version
python3 -m pip install deadlinks

# Development version
python3 -m pip install git+https://github.com/butuzov/deadlinks.git
python3 -m pip install https://github.com/butuzov/deadlinks/archive/develop.zip
```

## Docker Images

You can use [our docker images](https://hub.docker.com/repository/docker/butuzov/deadlinks) in your routine work or automated in your ci pipeline. Check [all releases](https://hub.docker.com/repository/registry-1.docker.io/butuzov/deadlinks/tags?page=1) and pick one that suits you.

Available versions:
* `a.b.c`, a version release.
* `latest` HEAD of master branch (usually it same as latest version release.).
* `dev` HEAD of develop branch.

```bash
docker pull butuzov/deadlinks
```

## Mac

```bash
# we using custom tap to install deadlinks
brew install butuzov/deadlinks/deadlinks
```

