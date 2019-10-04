#!/usr/bin/env bash

set -eo pipefail

if [ -n "${ON_ALPINE}" ]; then
    apk add --no-cache --virtual .build-deps gcc musl-dev linux-headers make
fi
pip install --no-cache-dir .[ujson,docs,tests] -U wheel