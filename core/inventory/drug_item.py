from dataclasses import dataclass
from datetime import date
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

@dataclass
class DrugItem:
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

# CRUD operations
async def add_drug_item(item: DrugItem) -> bool:
    """Add a new drug item to inventory."""
    ...

async def update_drug_item(item_id: str, updates: Dict[str, Any]) -> bool:
    """Update an existing drug item."""
    ...

async def delete_drug_item(item_id: str) -> bool:
    """Delete a drug item from inventory."""
    ...

async def get_drug_item(item_id: str) -> Optional[DrugItem]:
    """Retrieve a drug item by ID."""
    ...

async def list_drug_items(
    expiry_date_before: Optional[date] = None,
    low_stock_threshold: Optional[int] = None,
    shelf_location: Optional[str] = None
) -> List[DrugItem]:
    """List drug items with optional filters."""
    ...