import argparse
import json
import os
import random
import time
from datetime import datetime
from typing import Any

import requests

try:
    import redis
except ImportError:
    redis = None


DEFAULT_USERS = ["Ana", "Bruno", "Carla", "Diego", "Eva", "Facu"]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def write_log(log_file: str, event: str, data: dict[str, Any]) -> None:
    record = {"ts": now_iso(), "event": event, **data}
    with open(log_file, "a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def build_transaction(users: list[str], min_amount: int, max_amount: int) -> dict[str, Any]:
    origen, destino = random.sample(users, 2)
    return {
        "origen": origen,
        "destino": destino,
        "monto": random.randint(min_amount, max_amount),
    }


def send_transaction(coordinator_url: str, transaction: dict[str, Any], timeout: float) -> dict[str, Any]:
    started = time.time()
    response = requests.post(
        f"{coordinator_url.rstrip('/')}/transaccion",
        json=transaction,
        timeout=timeout,
    )
    elapsed = time.time() - started
    return {
        "status_code": response.status_code,
        "response_text": response.text,
        "elapsed_seconds": round(elapsed, 4),
    }


def connect_redis(host: str, port: int, password: str | None, db: int):
    if redis is None:
        raise RuntimeError("Falta instalar la dependencia 'redis'. Ejecuta: pip install redis")

    client = redis.Redis(host=host, port=port, password=password, db=db, decode_responses=True)
    client.ping()
    return client


def get_prefix(redis_client) -> str | None:
    value = redis_client.get("prefix_key")
    return value if value is not None else None


def get_blocks(redis_client, list_key: str) -> list[dict[str, Any]]:
    raw_blocks = redis_client.lrange(list_key, 0, -1)
    blocks = []
    for raw in raw_blocks:
        try:
            blocks.append(json.loads(raw))
        except json.JSONDecodeError:
            blocks.append({"raw": raw, "parse_error": True})
    return blocks


def summarize_block(block: dict[str, Any]) -> dict[str, Any]:
    transactions = block.get("transaccion", [])
    return {
        "id": block.get("id"),
        "numero": block.get("numero"),
        "hash": block.get("hash"),
        "prefix": block.get("prefix"),
        "previous_block": block.get("previous_block"),
        "blockchain_content": block.get("blockchain_content"),
        "timestamp": block.get("timestamp"),
        "tiempo_proceso": block.get("tiempo_proceso"),
        "transaction_count": len(transactions) if isinstance(transactions, list) else None,
        "transactions": transactions,
    }


def observe_redis(redis_client, list_key: str, seen_block_ids: set[str], last_prefix: str | None, log_file: str) -> str | None:
    current_prefix = get_prefix(redis_client)
    if current_prefix != last_prefix:
        write_log(
            log_file,
            "difficulty_changed",
            {
                "previous_prefix": last_prefix,
                "current_prefix": current_prefix,
                "previous_difficulty": len(last_prefix or ""),
                "current_difficulty": len(current_prefix or ""),
            },
        )
        last_prefix = current_prefix

    for block in reversed(get_blocks(redis_client, list_key)):
        block_id = str(block.get("id", ""))
        if not block_id or block_id in seen_block_ids:
            continue

        seen_block_ids.add(block_id)
        write_log(log_file, "block_created", summarize_block(block))

    return last_prefix


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Genera transacciones aleatorias y registra entradas, salidas, bloques y dificultad."
    )
    parser.add_argument("--coordinator-url", default=os.getenv("COORDINATOR_URL", "http://localhost:5000"))
    parser.add_argument("--redis-host", default=os.getenv("REDIS_HOST", "localhost"))
    parser.add_argument("--redis-port", type=int, default=int(os.getenv("REDIS_PORT", "6379")))
    parser.add_argument("--redis-password", default=os.getenv("REDIS_PASSWORD"))
    parser.add_argument("--redis-db", type=int, default=int(os.getenv("REDIS_DB", "0")))
    parser.add_argument("--redis-list-key", default=os.getenv("REDIS_LIST_KEY", "blockchain"))
    parser.add_argument("--log-file", default=os.getenv("LOAD_TEST_LOG", "load_test_observer.txt"))
    parser.add_argument("--users", default=",".join(DEFAULT_USERS))
    parser.add_argument("--min-amount", type=int, default=1)
    parser.add_argument("--max-amount", type=int, default=1000)
    parser.add_argument("--min-delay", type=float, default=1.0)
    parser.add_argument("--max-delay", type=float, default=5.0)
    parser.add_argument("--duration", type=float, default=0, help="Segundos totales. 0 significa infinito.")
    parser.add_argument("--request-timeout", type=float, default=5.0)
    parser.add_argument("--observe-only", action="store_true", help="No envia transacciones; solo observa Redis.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    users = [user.strip() for user in args.users.split(",") if user.strip()]
    if len(users) < 2:
        raise ValueError("Se necesitan al menos dos usuarios para generar transferencias.")
    if args.min_delay > args.max_delay:
        raise ValueError("--min-delay no puede ser mayor que --max-delay.")

    redis_client = connect_redis(args.redis_host, args.redis_port, args.redis_password, args.redis_db)
    seen_block_ids: set[str] = set()
    last_prefix: str | None = None
    started = time.time()

    write_log(
        args.log_file,
        "script_started",
        {
            "coordinator_url": args.coordinator_url,
            "redis_host": args.redis_host,
            "redis_port": args.redis_port,
            "redis_list_key": args.redis_list_key,
            "min_delay": args.min_delay,
            "max_delay": args.max_delay,
            "duration": args.duration,
            "observe_only": args.observe_only,
        },
    )

    try:
        while True:
            last_prefix = observe_redis(redis_client, args.redis_list_key, seen_block_ids, last_prefix, args.log_file)

            if not args.observe_only:
                transaction = build_transaction(users, args.min_amount, args.max_amount)
                write_log(args.log_file, "transaction_generated", {"transaction": transaction})

                try:
                    result = send_transaction(args.coordinator_url, transaction, args.request_timeout)
                    write_log(
                        args.log_file,
                        "transaction_response",
                        {"transaction": transaction, **result},
                    )
                except requests.RequestException as exc:
                    write_log(
                        args.log_file,
                        "transaction_error",
                        {"transaction": transaction, "error": str(exc)},
                    )

            last_prefix = observe_redis(redis_client, args.redis_list_key, seen_block_ids, last_prefix, args.log_file)

            if args.duration > 0 and time.time() - started >= args.duration:
                break

            time.sleep(random.uniform(args.min_delay, args.max_delay))

    except KeyboardInterrupt:
        write_log(args.log_file, "script_interrupted", {})
    finally:
        last_prefix = observe_redis(redis_client, args.redis_list_key, seen_block_ids, last_prefix, args.log_file)
        write_log(args.log_file, "script_finished", {"known_blocks": len(seen_block_ids)})


if __name__ == "__main__":
    main()
