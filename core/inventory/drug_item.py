from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

# import dataclasses from models/data_models.py
from models.data_models import DrugItem

# database imports
from core.database.connection import execute_write, fetch_one, fetch_all

# CRUD operations ##########################################
async def add_drug_item(item: DrugItem) -> bool:
    """Add a new drug item to inventory."""
    # try catch except pattern to handle errors gracefully
    try:
        # update db using the drug item model
        return await execute_write(
            """
            INSERT INTO drug_items (id, name, date_of_purchase, date_of_manufacture, expiry_date, batch_number, serial_number, shelf_location, company_sourced_from, quantity, price)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (item.id, item.name, item.date_of_purchase, item.date_of_manufacture, item.expiry_date, item.batch_number, item.serial_number, item.shelf_location, item.company_sourced_from, item.quantity, item.price)
        )
    except Exception as e:
        print(f"Error adding drug item: {e}")
        return False

async def update_drug_item(item_id: str, updates: Dict[str, Any]) -> bool:
    """Update an existing drug item."""
    # The updates dictionary is populated by the calling function
    try:
        # Builds the SET clause dynamically based on the updates dictionary
        # f"{key}=?" turns each key into an SQL fragment using updates.keys(which are the column names)
        # and then separate them with commas
        set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
        params = list(updates.values()) + [item_id]

        return await execute_write(
            f"""
            UPDATE drug_items
            SET {set_clause}
            WHERE id = ?
            """,
            tuple(params)
        )
    except Exception as e:
        print(f"Error updating drug item: {e}")
        return False

async def delete_drug_item(item_id: str) -> bool:
    """Delete a drug item from inventory."""
    try:
        return await execute_write(
            """
            DELETE FROM drug_items
            WHERE id = ?
            """,
            (item_id,)
        )
    except Exception as e:
        print(f"Error deleting drug item: {e}")
        return False

async def get_drug_item(item_id: str) -> Optional[DrugItem]:
    """Retrieve a drug item by ID."""   
    try:
        row = await fetch_one(
            """
            SELECT * FROM drug_items
            WHERE id = ?
            """,
            (item_id,)
        )
        if row:
            return DrugItem(**row)
        return None
    except Exception as e:
        print(f"Error retrieving drug item: {e}")
        return None

async def list_drug_items(
    expiry_date_before: Optional[date] = None,
    low_stock_threshold: Optional[int] = None,
    shelf_location: Optional[str] = None
) -> List[DrugItem]:
    """List drug items with optional filters."""
    try:
        # using WHERE 1=1 instead of SELECT * FROM drug_items, so as to easily add conditions(filters) without worrying about the WHERE clause
        query = "SELECT * FROM drug_items WHERE 1=1"
        params = []

        if expiry_date_before: # if searching by expiry date, same for the other if functions below
            query += " AND expiry_date < ?"
            params.append(expiry_date_before)
        
        if low_stock_threshold is not None: # if searching by low stock threshold
            query += " AND quantity < ?"
            params.append(low_stock_threshold)

        if shelf_location: # if searching by shelf location
            query += " AND shelf_location = ?"
            params.append(shelf_location)

        rows = await fetch_all(query, tuple(params)) # query is the SQL string with placeholders, params are the actual values
        return [DrugItem(**row) for row in rows]
    except Exception as e:  
        print(f"Error listing drug items: {e}")
        return []