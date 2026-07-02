# import relevant data model
from models.data_models import StockRecord
from datetime import date
from typing import Optional, List

# database imports
from core.database.connection import execute_write, fetch_all

# Stock operations
async def update_stock(item_id: str, quantity_change: int) -> bool:
    """Update stock quantity for an item."""
    try:
        return await execute_write(
            """
            INSERT INTO stock_records (item_id, quantity_change, timestamp)
            VALUES (?, ?, ?)
            """,
            (item_id, quantity_change, date.today())
        )
    except Exception as e:
        print(f"Error updating stock: {e}")
        return False

async def record_stock_in(item_id: str, quantity: int, received_date: date) -> bool:
    """Record stock received."""
    try:
        return await execute_write(
            """
            INSERT INTO stock_records (item_id, quantity_change, timestamp)
            VALUES (?, ?, ?)
            """,
            (item_id, quantity, received_date)
        )
    except Exception as e:
        print(f"Error recording stock in: {e}")
        return False

async def record_stock_out(item_id: str, quantity: int, used_date: date) -> bool:
    """Record stock used/dispensed."""
    try:
        await execute_write(
            conn,
            """
            INSERT INTO stock_records (item_id, quantity_change, timestamp)
            VALUES (?, ?, ?)
            """,
            (item_id, -quantity, used_date)
        )
        return True
    except Exception as e:
        print(f"Error recording stock out: {e}")
        return False
    finally:
        await close_database()

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

        records = await fetch_all(conn, query, params)
        return [StockRecord(**record) for record in records]
    except Exception as e:
        print(f"Error fetching stock history: {e}")
        return []
    finally:
        await close_database()