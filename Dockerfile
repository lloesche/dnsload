FROM python:3-alpine AS build-env
WORKDIR /usr/src/dnsload
COPY ./ ./
RUN pip install tox flake8
RUN tox

FROM python:3-alpine
WORKDIR /
RUN apk add --no-cache dumb-init
COPY --from=build-env /usr/src/dnsload /usr/src/dnsload
ENV PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN pip install /usr/src/dnsload \
    && rm -rf /usr/src/dnsload
ENTRYPOINT ["/usr/bin/dumb-init", "--",  "dnsload"]
