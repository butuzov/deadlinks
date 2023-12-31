# initial builder
FROM docker.io/python:3.11-slim as BUILD

COPY  . /tmp
WORKDIR /tmp

RUN grep "# install" requirements.txt -A100 > docker.requirments.txt \
    && echo "docker.requirments.txt" >> .dockerignore \
    && echo ".git" >> .dockerignore \
    && python3 -m pip install --upgrade pip \
    && python3 -m pip install --no-cache-dir -r docker.requirments.txt  \
    && echo "docker.requirments.txt" >> .dockerignore \
    # deadlinks install
    && python3 -m pip install . \
    # cleanups
    && python3 -m pip uninstall pip wheel setuptools -y \
    && find / -type f -name "*.pyc" -exec rm -r {} \; \
    && sed -i 's/\/usr\/local/\/usr/g'  /usr/local/bin/deadlinks


FROM gcr.io/distroless/python3-debian12:debug
LABEL maintainer "Oleg Butuzov <butuzov@made.ua>"

ENV PYTHONPATH=/usr/local/lib/python3.11/site-packages

COPY --from=BUILD ${PYTHONPATH} ${PYTHONPATH}
COPY --from=BUILD /usr/local/bin/deadlinks /usr/local/bin/

WORKDIR /github/workspace

ENTRYPOINT [ "deadlinks" ]
