# initial builder
FROM docker.io/python:3.5-slim-stretch as build-env

LABEL maintainer "Oleg Butuzov <butuzov@made.ua>"
COPY  . /app
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    git gcc g++

RUN grep "# install" requirements.txt -A100 > docker.requirments.txt \
    && echo "docker.requirments.txt" >> .dockerignore \
    && echo ".git" >> .dockerignore \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install --no-cache-dir -r docker.requirments.txt  \
    && echo "docker.requirments.txt" >> .dockerignore

RUN DEADLINKS_COMMIT=$(git rev-list --abbrev-commit -1 HEAD) \
    DEADLINKS_BRANCH=$(git rev-parse --abbrev-ref HEAD) \
    DEADLINKS_TAGGED=$(git describe) \
    python3 setup.py install \
    && rm -rf dist \
    && rm -rf build

RUN python3 -m pip uninstall pip wheel -y
RUN ls -la


# Uncomment for debug container
FROM gcr.io/distroless/python3:latest
COPY --from=build-env /app /app

ENV PYTHONPATH=/usr/local/lib/python3.5/site-packages
COPY --from=build-env ${PYTHONPATH} ${PYTHONPATH}
COPY --from=build-env /usr/local/lib/libpython3.5m.so.1.0 /usr/lib/x86_64-linux-gnu/

WORKDIR /app

ENTRYPOINT [ "python", "-m", "deadlinks" ]


