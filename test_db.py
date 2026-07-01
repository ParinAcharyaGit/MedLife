"""
Smoke test for the MedLife database layer (core/database/connection.py + schemas.py).

Run from the project root with:
    python3 test_db.py

Uses a throwaway .db file (test_medlife.db) so it never touches your real
medlife.db. Deletes it automatically when done, pass or fail.
"""

import asyncio
import os
import sqlite3
from pathlib import Path

from core.database.connection import (
    initialize_database,
    close_database,
    execute_write,
    fetch_one,
    fetch_all,
)

TEST_DB_PATH = Path(__file__).resolve().parent / "test_medlife.db"

passed = 0
failed = 0


def check(label: str, condition: bool):
    global passed, failed
    if condition:
        print(f"  [PASS] {label}")
        passed += 1
    else:
        print(f"  [FAIL] {label}")
        failed += 1


async def test_initialize():
    print("\n== initialize_database ==")
    ok = await initialize_database(db_path=TEST_DB_PATH)
    check("returns True", ok is True)
    check("db file created on disk", TEST_DB_PATH.exists())


async def test_tables_exist():
    print("\n== all tables created ==")
    expected_tables = {
        "drug_items", "stock_records", "reminders", "users",
        "transfer_requests", "consumption_records", "forecasts",
    }
    rows = await fetch_all("SELECT name FROM sqlite_master WHERE type='table'")
    actual_tables = {row["name"] for row in rows}
    for table in expected_tables:
        check(f"table '{table}' exists", table in actual_tables)


async def test_drug_items():
    print("\n== drug_items CRUD ==")
    ok = await execute_write(
        """INSERT INTO drug_items
           (id, name, date_of_purchase, date_of_manufacture, expiry_date, batch_number, quantity, price)
           VALUES (?,?,?,?,?,?,?,?)""",
        ("item-1", "Paracetamol", "2026-01-01", "2025-12-01", "2027-01-01", "B001", 100, 5.5),
    )
    check("insert succeeds", ok is True)

    row = await fetch_one("SELECT * FROM drug_items WHERE id = ?", ("item-1",))
    check("row retrievable", row is not None)
    check("name matches", row["name"] == "Paracetamol")
    check("quantity matches", row["quantity"] == 100)

    ok = await execute_write("UPDATE drug_items SET quantity = ? WHERE id = ?", (80, "item-1"))
    check("update succeeds", ok is True)
    row = await fetch_one("SELECT quantity FROM drug_items WHERE id = ?", ("item-1",))
    check("quantity updated", row["quantity"] == 80)

    # A second item for the low_stock / expiry filter checks
    await execute_write(
        """INSERT INTO drug_items
           (id, name, date_of_purchase, date_of_manufacture, expiry_date, batch_number, quantity, price)
           VALUES (?,?,?,?,?,?,?,?)""",
        ("item-2", "Amoxicillin", "2026-02-01", "2026-01-01", "2026-08-01", "B002", 5, 12.0),
    )
    rows = await fetch_all("SELECT * FROM drug_items WHERE expiry_date < ?", ("2027-01-01",))
    check("expiry filter finds item-2", any(r["id"] == "item-2" for r in rows))

    rows = await fetch_all("SELECT * FROM drug_items WHERE quantity < ?", (10,))
    check("low stock filter finds item-2", any(r["id"] == "item-2" for r in rows))


async def test_stock_records():
    print("\n== stock_records + foreign key ==")
    ok = await execute_write(
        "INSERT INTO stock_records (id, item_id, quantity_change, timestamp, reason) VALUES (?,?,?,?,?)",
        ("stock-1", "item-1", -20, "2026-03-01", "dispensed"),
    )
    check("insert linked to existing item succeeds", ok is True)

    rows = await fetch_all("SELECT * FROM stock_records WHERE item_id = ?", ("item-1",))
    check("history retrievable", len(rows) == 1)

    # Foreign key violation: item-999 doesn't exist
    ok = await execute_write(
        "INSERT INTO stock_records (id, item_id, quantity_change, timestamp) VALUES (?,?,?,?)",
        ("stock-bad", "item-999", 10, "2026-03-01"),
    )
    check("insert with invalid item_id is rejected (FK enforced)", ok is False)


async def test_reminders():
    print("\n== reminders ==")
    ok = await execute_write(
        "INSERT INTO reminders (id, item_id, reminder_date, type, message) VALUES (?,?,?,?,?)",
        ("rem-1", "item-2", "2026-07-01", "expiry", "Amoxicillin expiring soon"),
    )
    check("insert succeeds", ok is True)

    ok = await execute_write(
        "INSERT INTO reminders (id, item_id, reminder_date, type, message) VALUES (?,?,?,?,?)",
        ("rem-bad", "item-2", "2026-07-01", "not_a_real_type", "bad type"),
    )
    check("invalid type is rejected (CHECK constraint enforced)", ok is False)


async def test_users():
    print("\n== users ==")
    ok = await execute_write(
        "INSERT INTO users (id, username, password_hash, role) VALUES (?,?,?,?)",
        ("user-1", "adrian", "fake_hash_for_testing", "admin"),
    )
    check("insert succeeds", ok is True)

    ok = await execute_write(
        "INSERT INTO users (id, username, password_hash, role) VALUES (?,?,?,?)",
        ("user-2", "adrian", "another_hash", "viewer"),
    )
    check("duplicate username is rejected (UNIQUE constraint enforced)", ok is False)


async def test_cascade_delete():
    print("\n== ON DELETE CASCADE ==")
    rows_before = await fetch_all("SELECT * FROM stock_records WHERE item_id = ?", ("item-1",))
    check("stock record exists before delete", len(rows_before) == 1)

    await execute_write("DELETE FROM drug_items WHERE id = ?", ("item-1",))
    rows_after = await fetch_all("SELECT * FROM stock_records WHERE item_id = ?", ("item-1",))
    check("stock record cascade-deleted with parent item", len(rows_after) == 0)


async def test_close():
    print("\n== close_database ==")
    await close_database()
    try:
        # Any query after close should now fail with RuntimeError
        await fetch_all("SELECT 1")
        check("querying after close raises", False)
    except RuntimeError:
        check("querying after close raises", True)


async def main():
    if TEST_DB_PATH.exists():
        TEST_DB_PATH.unlink()

    try:
        await test_initialize()
        await test_tables_exist()
        await test_drug_items()
        await test_stock_records()
        await test_reminders()
        await test_users()
        await test_cascade_delete()
        await test_close()
    finally:
        for suffix in ("", "-wal", "-shm"):
            p = Path(str(TEST_DB_PATH) + suffix)
            if p.exists():
                p.unlink()

    print(f"\n{'='*40}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*40}")
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
