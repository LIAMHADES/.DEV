"""Small database compatibility layer for local SQLite and hosted PostgreSQL."""

from __future__ import annotations

import sqlite3
import os
import threading
from typing import Any, Iterable


_POOLS = {}
_POOLS_LOCK = threading.Lock()


def is_postgres_url(database: str) -> bool:
    return database.startswith(("postgres://", "postgresql://"))


class CompatibleConnection:
    """Expose the tiny execute/commit API used by the Flask app on both DBs."""

    def __init__(self, connection: Any, postgres: bool, release=None):
        self._connection = connection
        self.is_postgres = postgres
        self._release = release

    def execute(self, query: str, parameters: Iterable[Any] = ()):
        if self.is_postgres:
            query = query.replace("?", "%s")
        return self._connection.execute(query, tuple(parameters))

    def executemany(self, query: str, parameters):
        if self.is_postgres:
            query = query.replace("?", "%s")
        return self._connection.executemany(query, parameters)

    def commit(self):
        self._connection.commit()

    def rollback(self):
        self._connection.rollback()

    def close(self):
        if self._release:
            self._release(self._connection)
        else:
            self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.rollback()
        else:
            self.commit()
        self.close()
        return False


def open_connection(database: str) -> CompatibleConnection:
    if is_postgres_url(database):
        try:
            from psycopg_pool import ConnectionPool
        except ImportError as exc:
            raise RuntimeError(
                "PostgreSQL configured but psycopg_pool is not installed"
            ) from exc

        with _POOLS_LOCK:
            pool = _POOLS.get(database)
            if pool is None:
                min_size = max(1, int(os.environ.get("ONIX_DB_POOL_MIN", "1")))
                max_size = max(min_size, int(os.environ.get("ONIX_DB_POOL_MAX", "5")))
                pool = ConnectionPool(
                    conninfo=database,
                    min_size=min_size,
                    max_size=max_size,
                    kwargs={"connect_timeout": 10},
                    open=True,
                )
                _POOLS[database] = pool

        connection = pool.getconn()
        return CompatibleConnection(
            connection,
            postgres=True,
            release=pool.putconn,
        )

    connection = sqlite3.connect(database, timeout=10)
    connection.execute("PRAGMA foreign_keys = ON")
    return CompatibleConnection(connection, postgres=False)
