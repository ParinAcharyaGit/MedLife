"""
Database connection management for MedLife.

Uses the Python standard library `sqlite3` — no external dependency needed.
sqlite3 is synchronous by nature, so blocking calls are run in a worker
thread via `asyncio.to_thread`. This keeps the async function signatures
from PROJECT_STRUCTURE.md (add_drug_item, get_stock_history, etc.) usable
with `await`, without actually needing an async database driver.

Usage:
    from core.database.connection import initialize_database, close_database, get_connection

    await initialize_database()
    conn = get_connection()
    conn.execute(...)
    await close_database()
"""

import asyncio
import sqlite3
from pathlib import Path
from typing import Optional

from core.database.schemas import SCHEMA_STATEMENTS, INDEX_STATEMENTS

# connection.py lives at <project_root>/core/database/connection.py,
# so two parents up is the project root.
DEFAULT_DB_PATH = Path(__file__).resolve().parents[2] / "medlife.db"

# Module-level connection, created by initialize_database() and
# torn down by close_database(). check_same_thread=False because
# asyncio.to_thread() may run calls from a different thread than
# the one that opened the connection.
_connection: Optional[sqlite3.Connection] = None


def _init_sync(db_path: Path) -> bool:
    """Blocking half of initialize_database(), run in a worker thread."""
    global _connection
    try:
        _connection = sqlite3.connect(str(db_path), check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _connection.execute("PRAGMA foreign_keys = ON;")
        _connection.execute("PRAGMA journal_mode = WAL;")

        for statement in SCHEMA_STATEMENTS:
            _connection.execute(statement)
        for statement in INDEX_STATEMENTS:
            _connection.execute(statement)

        _connection.commit()
        return True
    except sqlite3.Error as exc:
        print(f"Failed to initialize database: {exc}")
        return False


async def initialize_database(db_path: Path = DEFAULT_DB_PATH) -> bool:
    """Initialize the database connection and tables."""
    return await asyncio.to_thread(_init_sync, db_path)


def _close_sync() -> None:
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None


async def close_database() -> None:
    """Close the database connection."""
    await asyncio.to_thread(_close_sync)


def get_connection() -> sqlite3.Connection:
    """
    Return the live module-level connection.

    Raises RuntimeError if initialize_database() hasn't been called yet,
    so callers fail fast instead of hitting a confusing AttributeError.
    Callers running on the event loop should wrap blocking calls in
    asyncio.to_thread(...), e.g.:

        conn = get_connection()
        row = await asyncio.to_thread(
            lambda: conn.execute("SELECT * FROM drug_items WHERE id = ?", (item_id,)).fetchone()
        )
    """
    if _connection is None:
        raise RuntimeError("Database not initialized. Call initialize_database() first.")
    return _connection


def _execute_write_sync(query: str, params: tuple) -> bool:
    conn = get_connection()
    try:
        conn.execute(query, params)
        conn.commit()
        return True
    except sqlite3.Error as exc:
        print(f"Database write failed: {exc}")
        return False


async def execute_write(query: str, params: tuple = ()) -> bool:
    """Convenience helper for simple INSERT/UPDATE/DELETE calls that just need a bool result."""
    return await asyncio.to_thread(_execute_write_sync, query, params)


def _fetch_all_sync(query: str, params: tuple) -> list:
    conn = get_connection()
    cursor = conn.execute(query, params)
    return cursor.fetchall()


async def fetch_all(query: str, params: tuple = ()) -> list:
    """Convenience helper for SELECT calls returning multiple rows (list of sqlite3.Row)."""
    return await asyncio.to_thread(_fetch_all_sync, query, params)


def _fetch_one_sync(query: str, params: tuple) -> Optional[sqlite3.Row]:
    conn = get_connection()
    cursor = conn.execute(query, params)
    return cursor.fetchone()


async def fetch_one(query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
    """Convenience helper for SELECT calls returning a single row (or None)."""
    return await asyncio.to_thread(_fetch_one_sync, query, params)
