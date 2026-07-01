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