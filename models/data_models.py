"""
Data models for the MedLife drug shelf-life tracker.

These dataclasses mirror the schema defined in schemas.py. They are the
in-memory representation used by the rest of the application; conversion
to/from sqlite3.Row happens in connection.py / the service modules.
"""

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


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


@dataclass
class StockRecord:
    id: str
    item_id: str
    quantity_change: int  # Positive for in, negative for out
    timestamp: date
    reason: Optional[str] = None


@dataclass
class Reminder:
    id: str
    item_id: str
    reminder_date: date
    type: str  # 'batch', 'expiry', or 'custom'
    message: str
    is_sent: bool = False
    sent_at: Optional[date] = None


@dataclass
class ExpiryHeatmapPoint:
    date: str  # YYYY-MM-DD format
    expiring_count: int
    expired_count: int
    total_value_at_risk: float


@dataclass
class User:
    id: str
    username: str
    password_hash: str
    role: str  # 'admin', 'pharmacist', or 'viewer'


# --- Additional features referenced in PROJECT_STRUCTURE.md ---

@dataclass
class TransferRequest:
    id: str
    item_id: str
    from_location: str
    to_location: str
    quantity: int
    requested_at: date
    status: str = "pending"  # 'pending', 'approved', 'rejected', 'completed'


@dataclass
class ConsumptionRecord:
    id: str
    item_id: str
    quantity_used: int
    recorded_at: date


@dataclass
class Forecast:
    id: str
    item_id: str
    generated_at: date
    predicted_stockout_date: Optional[date] = None
    average_daily_consumption: float = 0.0
