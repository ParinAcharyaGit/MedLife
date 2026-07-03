# import relevant data model
import uuid
from models.data_models import Reminder
from datetime import date, timedelta
from typing import List

# database imports
from core.database.connection import execute_write, fetch_all

# Reminder functions
async def set_reminder(
    item_id: str,
    reminder_date: date,
    reminder_type: str,
    message: str,
) -> bool:
    """Set a reminder for batch or expiry date."""
    try:
        return await execute_write(
            """
            INSERT INTO reminders (id, item_id, reminder_date, type, message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (str(uuid.uuid4()), item_id, reminder_date, reminder_type, message)
        )
    except Exception as e:
        print(f"Error setting reminder: {e}")
        return False

async def get_upcoming_reminders(days_ahead: int = 30) -> List[Reminder]:
    """Get reminders for the next N days."""
    try:
        rows = await fetch_all(
            """
            SELECT * FROM reminders
            WHERE reminder_date <= ?
            """,
            (date.today() + timedelta(days=days_ahead),)
        )
        return [Reminder(**row) for row in rows]
    except Exception as e:
        print(f"Error fetching upcoming reminders: {e}")
        return []

async def auto_generate_expiry_reminders() -> int:
    """Automatically generate reminders for all items expiring within 30 days. Returns count of reminders created."""
    try:
        rows = await fetch_all(
            """
            SELECT * FROM drug_items
            WHERE expiry_date <= ?
            """,
            (date.today() + timedelta(days=30),)
        )
        count = 0
        for row in rows:
            item_id = row['id']
            expiry_date = row['expiry_date']
            existing_reminders = await fetch_all(
                """
                SELECT * FROM reminders
                WHERE item_id = ? AND reminder_date = ? AND type = 'expiry'
                """,
                (item_id, expiry_date)
            )
            if not existing_reminders:
                success = await set_reminder(
                    item_id,
                    expiry_date,
                    'expiry',
                    f'Expiry reminder for item {item_id} on {expiry_date}',
                )
                if success:
                    count += 1
        return count
    except Exception as e:
        print(f"Error auto-generating expiry reminders: {e}")
        return 0


async def get_enriched_upcoming_reminders(days_ahead: int = 30) -> List[dict]:
    """Get upcoming reminders joined with drug item info for frontend display."""
    try:
        rows = await fetch_all(
            """
            SELECT
                r.id,
                r.item_id,
                d.name as medicine_name,
                '' as details,
                d.batch_number as batch_number,
                r.reminder_date as expiry_date,
                r.type as reminder_type
            FROM reminders r
            JOIN drug_items d ON r.item_id = d.id
            WHERE r.reminder_date <= ?
            """,
            (date.today() + timedelta(days=days_ahead),)
        )
        result = []
        for r in rows:
            # Determine status based on reminder type
            status = r['reminder_type'].capitalize() if r['reminder_type'] else ''
            result.append({
                'id': r['id'],
                'item_id': r['item_id'],
                'medicine_name': r['medicine_name'] or '',
                'details': r['details'] or '',
                'batch_number': r['batch_number'] or '',
                'status': status,
                'expiry_date': r['expiry_date']  # YYYY-MM-DD string
            })
        return result
    except Exception as e:
        print(f"Error fetching enriched upcoming reminders: {e}")
        return []