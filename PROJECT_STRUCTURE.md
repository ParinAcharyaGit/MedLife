# MedLife Project Structure
This document outlines the core features and their function signatures for the MedLife drug shelf-life tracker application.

## Core Features

### 1. Drug Inventory Management
Functions for managing drug inventory items.

```python
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
```

### 2. Stock Tracking Functions
Functions for tracking stock movements and updates.

```python
@dataclass
class StockRecord:
    id: str
    item_id: str
    quantity_change: int  # Positive for in, negative for out
    timestamp: date
    reason: Optional[str] = None

# Stock operations
async def update_stock(item_id: str, quantity_change: int) -> bool:
    """Update stock quantity for an item."""
    ...

async def record_stock_in(item_id: str, quantity: int, received_date: date) -> bool:
    """Record stock received."""
    ...

async def record_stock_out(item_id: str, quantity: int, used_date: date) -> bool:
    """Record stock used/dispensed."""
    ...

async def get_stock_history(
    item_id: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[StockRecord]:
    """Get stock movement history for an item."""
    ...
```

### 3. Reminder System
Functions for handling reminders based on batch/expiry dates.

```python
@dataclass
class Reminder:
    id: str
    item_id: str
    reminder_date: date
    type: str  # 'batch', 'expiry', or 'custom'
    message: str
    is_sent: bool = False
    sent_at: Optional[date] = None

# Reminder functions
async def set_reminder(
    item_id: str,
    reminder_date: date,
    reminder_type: str
) -> bool:
    """Set a reminder for batch or expiry date."""
    ...

async def get_upcoming_reminders(days_ahead: int = 30) -> List[Reminder]:
    """Get reminders for the next N days."""
    ...

async def auto_generate_expiry_reminders() -> int:
    """Automatically generate expiry reminders for all items. Returns count of reminders created."""
    ...
```

### 4. Expiry Heatmap and List
Functions for generating visual expiry data.

```python
@dataclass
class ExpiryHeatmapPoint:
    date: str  # YYYY-MM-DD format
    expiring_count: int
    expired_count: int
    total_value_at_risk: float

# Heatmap functions
async def get_expiry_heatmap_data(
    start_date: date,
    end_date: date
) -> List[ExpiryHeatmapPoint]:
    """Get expiry heatmap data for a date range."""
    ...

async def get_items_expiring_soon(days_threshold: int = 30) -> List[DrugItem]:
    """Get items expiring within the specified number of days."""
    ...

async def get_expired_items() -> List[DrugItem]:
    """Get all expired items."""
    ...
```

### 5. Database & Authentication
Basic data storage and user authentication functions.

```python
@dataclass
class User:
    id: str
    username: str
    password_hash: str
    role: str  # 'admin', 'pharmacist', or 'viewer'

# Database initialization
async def initialize_database() -> bool:
    """Initialize the database connection and tables."""
    ...

async def close_database() -> None:
    """Close the database connection."""
    ...

# User authentication
async def register_user(username: str, password: str, role: str) -> Optional[User]:
    """Register a new user."""
    ...

async def authenticate_user(username: str, password: str) -> Optional[User]:
    """Authenticate a user and return user object if successful."""
    ...

async def change_password(user_id: str, old_password: str, new_password: str) -> bool:
    """Change a user's password."""
    ...
```

## Supporting Types

The dataclasses defined above serve as the primary data structures:
- `DrugItem`: Represents a drug inventory item
- `StockRecord`: Tracks stock movements
- `Reminder`: Represents a reminder notification
- `ExpiryHeatmapPoint`: Data point for expiry heatmap visualization
- `User`: Represents a system user

Classes for additional features
- `TransferRequest`: Represents a drug transfer request
- `Forecast`: Represents a consumption forecast
- `ConsumptionRecord`: Tracks historical consumption

## Module Organization Suggestion

```
medlife/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── inventory/
│   │   ├── __init__.py
│   │   ├── drug_item.py
│   │   ├── stock_tracking.py
│   │   └── reminders.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── schemas.py
│   ├── auth/
│   │   ├── __init__.py
│   │   └── auth_service.py
│   ├── transfer/
│   │   ├── __init__.py
│   │   └── transfer_service.py
│   └── forecasting/
│       ├── __init__.py
│       └── forecast_service.py
├── models/
│   ├── __init__.py
│   └── data_models.py  # Contains all dataclass definitions
├── utils/
│   ├── __init__.py
│   ├── date_helpers.py
│   └── validation.py
├── main.py
├── requirements.txt
└── README.md
```