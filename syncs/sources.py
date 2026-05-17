"""Source connectors — read dbt model outputs from SQL databases."""
from __future__ import annotations

import csv
import sqlite3
from pathlib import Path
from typing import Any


def read_source(config: dict) -> list[dict[str, Any]]:
    """Read records from configured source."""
    source_type = config["type"]
    if source_type == "sqlite":
        return _read_sqlite(config)
    elif source_type == "csv":
        return _read_csv(config)
    elif source_type == "postgres":
        return _read_postgres(config)
    else:
        raise ValueError(f"Unsupported source type: {source_type}")


def _read_sqlite(config: dict) -> list[dict]:
    conn = sqlite3.connect(config["path"])
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(config["query"])
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows


def _read_csv(config: dict) -> list[dict]:
    path = Path(config["path"])
    with open(path) as f:
        return list(csv.DictReader(f))


def _read_postgres(config: dict) -> list[dict]:
    """Read from PostgreSQL (requires psycopg2)."""
    try:
        import psycopg2
        import psycopg2.extras
    except ImportError:
        raise ImportError("Install psycopg2: pip install psycopg2-binary")

    conn = psycopg2.connect(
        host=config.get("host", "localhost"),
        port=config.get("port", 5432),
        dbname=config["database"],
        user=config.get("user", ""),
        password=config.get("password", ""),
    )
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(config["query"])
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return rows
