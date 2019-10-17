# `WIP` docker implementation


## `make`

```bash
# Upgrade Package Version
make update VERSION=0.0.1
# Build and Push
make build
make push
```

## Using

It's ok to use docker image for remote domain checks, but its fails to use host network on mac and windows to check local domains.

```bash
docker run -it butuzov/deadlinks:0.0.1 https://opsdroid.readthedocs.io/en/latest/ -n 10

# Usage on Mac
docker run -it --network=host  butuzov/deadlinks:0.0.1 http://127.0.0.1:8000  -n 10
```



