"""
Local API server for MedLife.

Exposes the database layer (core/database/connection.py) over HTTP so a
local frontend (React dev server, etc.) can read/write drug inventory
without needing direct DB access.

Run with:
    uvicorn api_server:app --reload --port 8000

Then visit http://localhost:8000/docs for interactive API docs
(FastAPI generates this automatically from the code below).
"""

from contextlib import asynccontextmanager
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.database.connection import (
    initialize_database,
    close_database,
    execute_write,
    fetch_one,
    fetch_all,
)


# --- Startup/shutdown wiring -------------------------------------------------
# FastAPI's lifespan hook replaces manually calling initialize_database()/
# close_database() yourself — it runs once when the server starts and once
# when it shuts down (Ctrl+C).

@asynccontextmanager
async def lifespan(app: FastAPI):
    await initialize_database()
    yield
    await close_database()


app = FastAPI(title="MedLife API", lifespan=lifespan)

# CORS: allows a frontend running on a different port (e.g. a React dev
# server on localhost:3000 or localhost:5173) to call this API. Without
# this, the browser blocks the requests even though the server is running.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your actual frontend's URL once you know it
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Request/response shapes --------------------------------------------------
# Pydantic models define what JSON shape the frontend sends/receives.
# These mirror DrugItem from models/data_models.py but use FastAPI's
# validation instead of a plain dataclass.

class DrugItemIn(BaseModel):
    id: str
    name: str
    date_of_purchase: date
    date_of_manufacture: date
    expiry_date: date
    batch_number: str
    serial_number: Optional[str] = None
    shelf_location: Optional[str] = None
    company_sourced_from: str = ""
    quantity: int = 0
    price: float = 0.0


class DrugItemUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None
    shelf_location: Optional[str] = None


def _row_to_dict(row) -> dict:
    """Convert a sqlite3.Row into a plain JSON-serializable dict."""
    return dict(row) if row is not None else None


# --- Routes --------------------------------------------------------------

@app.get("/")
async def root():
    return {"status": "MedLife API is running"}


@app.get("/drug-items")
async def list_drug_items(
    expiry_before: Optional[date] = None,
    low_stock_threshold: Optional[int] = None,
    shelf_location: Optional[str] = None,
):
    """List drug items, with optional filters as query params, e.g.
    GET /drug-items?low_stock_threshold=10
    """
    conditions = []
    params = []

    if expiry_before is not None:
        conditions.append("expiry_date < ?")
        params.append(expiry_before.isoformat())
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
    return [_row_to_dict(row) for row in rows]


@app.get("/drug-items/{item_id}")
async def get_drug_item(item_id: str):
    row = await fetch_one("SELECT * FROM drug_items WHERE id = ?", (item_id,))
    if row is None:
        raise HTTPException(status_code=404, detail=f"Drug item '{item_id}' not found")
    return _row_to_dict(row)


@app.post("/drug-items", status_code=201)
async def create_drug_item(item: DrugItemIn):
    existing = await fetch_one("SELECT id FROM drug_items WHERE id = ?", (item.id,))
    if existing is not None:
        raise HTTPException(status_code=409, detail=f"Drug item '{item.id}' already exists")

    ok = await execute_write(
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
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to create drug item")

    row = await fetch_one("SELECT * FROM drug_items WHERE id = ?", (item.id,))
    return _row_to_dict(row)


@app.patch("/drug-items/{item_id}")
async def update_drug_item(item_id: str, updates: DrugItemUpdate):
    existing = await fetch_one("SELECT id FROM drug_items WHERE id = ?", (item_id,))
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Drug item '{item_id}' not found")

    fields_to_update = updates.model_dump(exclude_unset=True)
    if not fields_to_update:
        raise HTTPException(status_code=400, detail="No fields provided to update")

    set_clause = ", ".join(f"{field} = ?" for field in fields_to_update)
    params = tuple(fields_to_update.values()) + (item_id,)

    ok = await execute_write(f"UPDATE drug_items SET {set_clause} WHERE id = ?", params)
    if not ok:
        raise HTTPException(status_code=500, detail="Failed to update drug item")

    row = await fetch_one("SELECT * FROM drug_items WHERE id = ?", (item_id,))
    return _row_to_dict(row)


@app.delete("/drug-items/{item_id}", status_code=204)
async def delete_drug_item(item_id: str):
    existing = await fetch_one("SELECT id FROM drug_items WHERE id = ?", (item_id,))
    if existing is None:
        raise HTTPException(status_code=404, detail=f"Drug item '{item_id}' not found")

    await execute_write("DELETE FROM drug_items WHERE id = ?", (item_id,))
    return None
