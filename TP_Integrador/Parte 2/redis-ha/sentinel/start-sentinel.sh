#!/bin/sh
set -eu

if [ ! -f /data/sentinel.conf ]; then
  MASTER_IP=""

  while [ -z "$MASTER_IP" ]; do
    MASTER_IP="$(getent hosts redis-0 | awk 'NR == 1 { print $1 }')"

    if [ -z "$MASTER_IP" ]; then
      sleep 1
    fi
  done

  ESCAPED_PASSWORD=$(printf '%s' "$REDIS_PASSWORD" | sed 's/[\/&]/\\&/g')

  sed \
    -e "s/__REDIS_MASTER_IP__/${MASTER_IP}/g" \
    -e "s/__REDIS_PASSWORD__/${ESCAPED_PASSWORD}/g" \
    /templates/sentinel.conf.template > /data/sentinel.conf
fi

exec redis-server /data/sentinel.conf --sentinel