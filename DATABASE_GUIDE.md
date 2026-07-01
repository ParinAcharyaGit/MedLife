# MedLife — Database Layer Usage Guide

This explains how the SQLite database layer works, so anyone on the team can start writing the actual feature code (inventory, auth, transfers, forecasting) without having to reverse-engineer `connection.py`.

## 1. The two files that matter

```
core/database/
├── schemas.py      # defines every table (the DDL)
└── connection.py   # opens the DB, creates tables, and gives you helper functions to read/write
```

You will almost never touch `connection.py` directly once it's working — you `import` from it and call its functions from your own feature modules (`core/inventory/drug_item.py`, `core/auth/auth_service.py`, etc.).

## 2. Why everything is `async`, even though SQLite isn't

SQLite itself is synchronous — one query blocks until it's done. But every function signature in the project (`add_drug_item`, `get_stock_history`, ...) is declared `async def`. So `connection.py` runs the actual blocking SQLite calls in a background thread (`asyncio.to_thread`) and hands you back an `async` function to `await`. Practically, this means: **always use `await`** when calling anything from `connection.py`, and any feature function you write should also be `async def`.

## 3. Starting up and shutting down

Every entry point into the app (your test scripts, `main.py`, etc.) needs to call `initialize_database()` once before doing anything else, and `close_database()` when done:

```python
import asyncio
from core.database.connection import initialize_database, close_database

async def main():
    await initialize_database()
    # ... do stuff with the database ...
    await close_database()

asyncio.run(main())
```

`initialize_database()`:
- Opens (or creates, if it doesn't exist) `medlife.db` in the project root
- Turns on foreign key enforcement (off by default in SQLite — this is why bad `item_id` references get rejected)
- Runs every `CREATE TABLE IF NOT EXISTS` statement in `schemas.py`, so it's always safe to call — it won't wipe existing data or error if tables already exist

## 4. The four functions you'll actually use

| Function | Use for | Returns |
|---|---|---|
| `execute_write(query, params)` | INSERT / UPDATE / DELETE | `True` / `False` |
| `fetch_one(query, params)` | SELECT expecting exactly one row (or none) | a row, or `None` |
| `fetch_all(query, params)` | SELECT expecting multiple rows | a list of rows (empty list if none) |
| `get_connection()` | Advanced/rare — direct access to the raw `sqlite3.Connection` | `sqlite3.Connection` |

Rows come back as `sqlite3.Row` objects — access columns like a dict (`row["name"]`) or convert with `dict(row)`.

**Always use `?` placeholders, never string-format your SQL.** This isn't a style preference — it's what prevents SQL injection and it's also just how `sqlite3` expects parameters.

```python
# Good
await execute_write(
    "INSERT INTO drug_items (id, name, quantity) VALUES (?, ?, ?)",
    (item_id, name, quantity)
)

# Bad — never do this
await execute_write(f"INSERT INTO drug_items (id, name) VALUES ('{item_id}', '{name}')")
```

## 5. Worked example: writing `add_drug_item`

This is the pattern every function in `core/inventory/`, `core/auth/`, etc. should follow — call the schema function from `connection.py`, translate params in, translate the result out.

```python
# core/inventory/drug_item.py
from core.database.connection import execute_write, fetch_one, fetch_all
from models.data_models import DrugItem

async def add_drug_item(item: DrugItem) -> bool:
    """Add a new drug item to inventory."""
    return await execute_write(
        """INSERT INTO drug_items
           (id, name, date_of_purchase, date_of_manufacture, expiry_date,
            batch_number, serial_number, shelf_location, company_sourced_from,
            quantity, price)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            item.id, item.name,
            item.date_of_purchase.isoformat(), item.date_of_manufacture.isoformat(),
            item.expiry_date.isoformat(), item.batch_number, item.serial_number,
            item.shelf_location, item.company_sourced_from, item.quantity, item.price,
        ),
    )

async def get_drug_item(item_id: str) -> DrugItem | None:
    """Retrieve a drug item by ID."""
    row = await fetch_one("SELECT * FROM drug_items WHERE id = ?", (item_id,))
    if row is None:
        return None
    return DrugItem(
        id=row["id"], name=row["name"],
        date_of_purchase=date.fromisoformat(row["date_of_purchase"]),
        date_of_manufacture=date.fromisoformat(row["date_of_manufacture"]),
        expiry_date=date.fromisoformat(row["expiry_date"]),
        batch_number=row["batch_number"], serial_number=row["serial_number"],
        shelf_location=row["shelf_location"], company_sourced_from=row["company_sourced_from"],
        quantity=row["quantity"], price=row["price"],
    )
```

Note the two things happening at the boundary:
- **Going in:** Python `date` objects get converted to ISO strings (`item.date_of_purchase.isoformat()`) because SQLite has no native date type — everything is stored as `'YYYY-MM-DD'` text.
- **Coming out:** the reverse — `date.fromisoformat(row["date_of_purchase"])` turns the stored string back into a real `date` object before it's handed back to the caller.

Anyone writing a new function that touches dates needs to do this conversion — it won't happen automatically.

## 6. How filtering works (e.g. `list_drug_items`)

Build the `WHERE` clause dynamically based on which optional filters were passed, keeping every value parameterized:

```python
async def list_drug_items(
    expiry_date_before: date | None = None,
    low_stock_threshold: int | None = None,
    shelf_location: str | None = None,
) -> list[DrugItem]:
    conditions = []
    params = []

    if expiry_date_before is not None:
        conditions.append("expiry_date < ?")
        params.append(expiry_date_before.isoformat())
    if low_stock_threshold is not None:
        conditions.append("quantity < ?")
        params.append(low_stock_threshold)
    if shelf_location is not None:
        conditions.append("shelf_location = ?")
        params.append(shelf_location)

    query = "SELECT * FROM drug_items"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    rows = await fetch_all(query, tuple(params))
    return [_row_to_drug_item(row) for row in rows]  # see get_drug_item above for the conversion
```

## 7. The schema, at a glance

| Table | Links to | Enforced rules |
|---|---|---|
| `drug_items` | — | none, this is the root table |
| `stock_records` | `drug_items.id` | deleting a drug item cascades and deletes its stock records |
| `reminders` | `drug_items.id` | `type` must be `'batch'`, `'expiry'`, or `'custom'` |
| `users` | — | `username` must be unique; `role` must be `'admin'`, `'pharmacist'`, or `'viewer'` |
| `transfer_requests` | `drug_items.id` | `status` must be `'pending'`, `'approved'`, `'rejected'`, or `'completed'` |
| `consumption_records` | `drug_items.id` | cascades on delete |
| `forecasts` | `drug_items.id` | cascades on delete |

"Cascades on delete" means: if you delete a row from `drug_items`, every row in the linked tables that references it gets automatically deleted too — you don't need to manually clean those up yourself.

## 8. Testing your own functions

`test_db.py` in the project root is a working example of testing directly against the DB layer — copy its pattern (throwaway test DB file, `check()` assertions, cleanup in a `finally` block) when you write tests for your own feature module. Run the existing suite anytime with:

```bash
python3 test_db.py
```

If you break the schema or connection layer, this is the fastest way to find out before it shows up as a mystery bug three files away.

## 9. Common mistakes to avoid

- **Forgetting `await`.** Every one of these functions is a coroutine — calling `execute_write(...)` without `await` silently does nothing (you get back an un-awaited coroutine object, not a result).
- **String-formatting SQL instead of using `?` placeholders.** Besides being a security risk, it also breaks the moment a name has an apostrophe in it (`O'Brien`).
- **Forgetting date conversion.** Passing a raw `date` object into a query, or forgetting to convert a stored string back into a `date` on the way out, is the most common bug you'll hit here.
- **Calling any DB function before `initialize_database()`.** You'll get a clear `RuntimeError: Database not initialized`, not a silent failure — that error message means exactly what it says.
