#!/bin/sh
set -eu

ESCAPED_PASSWORD=$(printf '%s' "$REDIS_PASSWORD" | sed 's/[\/&]/\\&/g')

sed "s/__REDIS_PASSWORD__/${ESCAPED_PASSWORD}/g" \
  /templates/haproxy.cfg.template > /tmp/haproxy.cfg

printf '\n' >> /tmp/haproxy.cfg

exec haproxy -W -db -f /tmp/haproxy.cfg