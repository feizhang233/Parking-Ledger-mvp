from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "parking_ledger.db"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_connection() as conn:
        conn.executescript(sql)
        _run_migrations(conn)


def _run_migrations(conn: sqlite3.Connection) -> None:
    project_columns = {row["name"] for row in conn.execute("PRAGMA table_info(projects)")}
    if "region" not in project_columns:
        conn.execute("ALTER TABLE projects ADD COLUMN region TEXT NOT NULL DEFAULT '外地'")
    if "template_id" not in project_columns:
        conn.execute("ALTER TABLE projects ADD COLUMN template_id INTEGER")
    conn.execute(
        """
        UPDATE projects
        SET region = CASE
            WHEN name LIKE '%北京%' THEN '北京'
            ELSE COALESCE(region, '外地')
        END
        WHERE region IS NULL OR region = ''
        """
    )
    conn.commit()


def fetch_all(query: str, params: Iterable[Any] = ()) -> list[sqlite3.Row]:
    with get_connection() as conn:
        cursor = conn.execute(query, tuple(params))
        return cursor.fetchall()


def fetch_one(query: str, params: Iterable[Any] = ()) -> sqlite3.Row | None:
    with get_connection() as conn:
        cursor = conn.execute(query, tuple(params))
        return cursor.fetchone()


def execute(query: str, params: Iterable[Any] = ()) -> int:
    with get_connection() as conn:
        cursor = conn.execute(query, tuple(params))
        conn.commit()
        return cursor.lastrowid


def execute_many(query: str, params: list[tuple[Any, ...]]) -> None:
    with get_connection() as conn:
        conn.executemany(query, params)
        conn.commit()
