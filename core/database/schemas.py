"""
SQLite schema definitions for MedLife.

All tables use TEXT primary keys (expected to hold UUID strings generated
by the application layer) and store dates as ISO-8601 TEXT ('YYYY-MM-DD'),
which sorts and filters correctly in SQLite.
"""

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS drug_items (
        id                    TEXT PRIMARY KEY,
        name                  TEXT NOT NULL,
        date_of_purchase      TEXT NOT NULL,
        date_of_manufacture   TEXT NOT NULL,
        expiry_date           TEXT NOT NULL,
        batch_number          TEXT NOT NULL,
        serial_number         TEXT,
        shelf_location        TEXT,
        company_sourced_from  TEXT DEFAULT '',
        quantity              INTEGER NOT NULL DEFAULT 0,
        price                 REAL NOT NULL DEFAULT 0.0
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS stock_records (
        id               TEXT PRIMARY KEY,
        item_id          TEXT NOT NULL,
        quantity_change  INTEGER NOT NULL,
        timestamp        TEXT NOT NULL,
        reason           TEXT,
        FOREIGN KEY (item_id) REFERENCES drug_items (id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS reminders (
        id             TEXT PRIMARY KEY,
        item_id        TEXT NOT NULL,
        reminder_date  TEXT NOT NULL,
        type           TEXT NOT NULL CHECK (type IN ('batch', 'expiry', 'custom')),
        message        TEXT NOT NULL,
        is_sent        INTEGER NOT NULL DEFAULT 0,
        sent_at        TEXT,
        FOREIGN KEY (item_id) REFERENCES drug_items (id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS users (
        id             TEXT PRIMARY KEY,
        username       TEXT NOT NULL UNIQUE,
        password_hash  TEXT NOT NULL,
        role           TEXT NOT NULL CHECK (role IN ('admin', 'pharmacist', 'viewer'))
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS transfer_requests (
        id             TEXT PRIMARY KEY,
        item_id        TEXT NOT NULL,
        from_location  TEXT NOT NULL,
        to_location    TEXT NOT NULL,
        quantity       INTEGER NOT NULL,
        requested_at   TEXT NOT NULL,
        status         TEXT NOT NULL DEFAULT 'pending'
            CHECK (status IN ('pending', 'approved', 'rejected', 'completed')),
        FOREIGN KEY (item_id) REFERENCES drug_items (id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS consumption_records (
        id            TEXT PRIMARY KEY,
        item_id       TEXT NOT NULL,
        quantity_used INTEGER NOT NULL,
        recorded_at   TEXT NOT NULL,
        FOREIGN KEY (item_id) REFERENCES drug_items (id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS forecasts (
        id                          TEXT PRIMARY KEY,
        item_id                     TEXT NOT NULL,
        generated_at                TEXT NOT NULL,
        predicted_stockout_date     TEXT,
        average_daily_consumption   REAL NOT NULL DEFAULT 0.0,
        FOREIGN KEY (item_id) REFERENCES drug_items (id) ON DELETE CASCADE
    );
    """,
]

# Helpful indexes for the query patterns in PROJECT_STRUCTURE.md
# (expiry_date_before, low_stock_threshold, shelf_location filters; date-range history/heatmap lookups)
INDEX_STATEMENTS = [
    "CREATE INDEX IF NOT EXISTS idx_drug_items_expiry ON drug_items (expiry_date);",
    "CREATE INDEX IF NOT EXISTS idx_drug_items_shelf ON drug_items (shelf_location);",
    "CREATE INDEX IF NOT EXISTS idx_stock_records_item_ts ON stock_records (item_id, timestamp);",
    "CREATE INDEX IF NOT EXISTS idx_reminders_date ON reminders (reminder_date);",
    "CREATE INDEX IF NOT EXISTS idx_transfer_requests_item ON transfer_requests (item_id);",
    "CREATE INDEX IF NOT EXISTS idx_consumption_item_date ON consumption_records (item_id, recorded_at);",
]
