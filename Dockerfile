# initial builder
FROM docker.io/python:3.7-slim-stretch as BUILD

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


FROM gcr.io/distroless/python3:latest
LABEL maintainer "Oleg Butuzov <butuzov@made.ua>"

ENV PYTHONPATH=/usr/local/lib/python3.7/site-packages

COPY --from=BUILD ${PYTHONPATH} ${PYTHONPATH}
# COPY --from=BUILD /usr/local/lib/libpython3.7m.so.1.0 /usr/lib/x86_64-linux-gnu/
COPY --from=BUILD /usr/local/bin/deadlinks /usr/local/bin/

WORKDIR /github/workspace

ENTRYPOINT [ "deadlinks" ]
