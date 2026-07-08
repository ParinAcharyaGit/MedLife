# import relevant data model
import uuid
from models.data_models import StockRecord
from datetime import date
from typing import Optional, List

# database imports
from core.database.connection import execute_write, fetch_all

# Stock operations
async def update_stock(item_id: str, quantity_change: int) -> bool:
    """Update stock quantity for an item (legacy convenience wrapper)."""
    if quantity_change >= 0:
        return await record_stock_in(item_id, quantity_change, date.today())
    return await record_stock_out(item_id, abs(quantity_change), date.today())


async def _adjust_quantity(item_id: str, delta: int) -> bool:
    """Atomically adjust drug_items.quantity by `delta` (clamped at 0)."""
    try:
        return await execute_write(
            """
            UPDATE drug_items
            SET quantity = MAX(0, quantity + ?)
            WHERE id = ?
            """,
            (delta, item_id),
        )
    except Exception as e:
        print(f"Error adjusting quantity: {e}")
        return False


async def record_stock_in(item_id: str, quantity: int, received_date: date) -> bool:
    """Record stock received — inserts a stock_records row AND increments the item's quantity."""
    if quantity <= 0:
        return False
    try:
        inserted = await execute_write(
            """
            INSERT INTO stock_records (id, item_id, quantity_change, timestamp, reason)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), item_id, quantity, received_date, "stock_in"),
        )
        if not inserted:
            return False
        return await _adjust_quantity(item_id, quantity)
    except Exception as e:
        print(f"Error recording stock in: {e}")
        return False


async def record_stock_out(item_id: str, quantity: int, used_date: date) -> bool:
    """Record stock used/dispensed — inserts a stock_records row AND decrements the item's quantity."""
    if quantity <= 0:
        return False
    try:
        inserted = await execute_write(
            """
            INSERT INTO stock_records (id, item_id, quantity_change, timestamp, reason)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), item_id, -quantity, used_date, "stock_out"),
        )
        if not inserted:
            return False
        return await _adjust_quantity(item_id, -quantity)
    except Exception as e:
        print(f"Error recording stock out: {e}")
        return False


async def get_stock_history(
    item_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[StockRecord]:
    """Get stock movement history for an item."""
    try:
        query = """
            SELECT * FROM stock_records
            WHERE item_id = ?
        """
        params = [item_id]
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)

        records = await fetch_all(query, tuple(params))
        return [StockRecord(**record) for record in records]
    except Exception as e:
        print(f"Error fetching stock history: {e}")
        return []
