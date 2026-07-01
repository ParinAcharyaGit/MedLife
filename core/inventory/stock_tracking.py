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