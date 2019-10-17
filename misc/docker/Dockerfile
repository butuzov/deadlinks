FROM python:3.8.0-alpine3.10

LABEL maintainer "Oleg Butuzov <butuzov@made.ua>"

WORKDIR /app

RUN python3 -m pip --no-cache-dir install \
    deadlinks==0.0.1

ENTRYPOINT ["deadlinks"]
