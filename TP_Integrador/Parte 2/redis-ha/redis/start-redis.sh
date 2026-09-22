#!/bin/sh
set -eu

MASTER_HOST=""
MASTER_PORT="6379"
SELF_IP="$(hostname -i | awk '{print $1}')"

for SENTINEL in sentinel-0 sentinel-1 sentinel-2; do
  MASTER_INFO="$(redis-cli -h "$SENTINEL" -p 26379 --raw SENTINEL get-master-addr-by-name mymaster 2>/dev/null || true)"
  FOUND_HOST="$(printf '%s\n' "$MASTER_INFO" | sed -n '1p')"
  FOUND_PORT="$(printf '%s\n' "$MASTER_INFO" | sed -n '2p')"

  if [ -n "$FOUND_HOST" ]; then
    MASTER_HOST="$FOUND_HOST"
    MASTER_PORT="${FOUND_PORT:-6379}"
    break
  fi
done

if [ -z "$MASTER_HOST" ]; then
  if [ "$REDIS_NODE_NAME" = "redis-0" ]; then
    MASTER_HOST="$REDIS_NODE_NAME"
  else
    MASTER_HOST="redis-0"
  fi
fi

set -- redis-server \
  --bind 0.0.0.0 \
  --protected-mode no \
  --appendonly yes \
  --appendfsync everysec \
  --dir /data \
  --requirepass "$REDIS_PASSWORD" \
  --masterauth "$REDIS_PASSWORD" \
  --min-replicas-to-write 1 \
  --min-replicas-max-lag 10

if [ "$MASTER_HOST" != "$REDIS_NODE_NAME" ] && [ "$MASTER_HOST" != "$SELF_IP" ]; then
  set -- "$@" --replicaof "$MASTER_HOST" "$MASTER_PORT"
fi

exec "$@"