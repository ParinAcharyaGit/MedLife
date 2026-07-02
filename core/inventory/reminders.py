# import relevant data model
from models.data_models import Reminder
from datetime import date, timedelta
from typing import List

# database imports
from core.database.connection import execute_write, fetch_all

# Reminder functions
async def set_reminder(
    item_id: str,
    reminder_date: date,
    reminder_type: str
) -> bool:
    """Set a reminder for batch or expiry date."""
    try:
        return await execute_write(
            # the patterm below prevents SQL injection attacks
            """
            INSERT INTO reminders (item_id, reminder_date, type)
            VALUES (?, ?, ?)
            """,
            (item_id, reminder_date, reminder_type)
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
            (date.today() + timedelta(days=days_ahead),) # counts x days ahead from today, days are PASSED by REFERENCE
        )
        return [Reminder(**row) for row in rows] # the for loop builds the list, while **row converts each db row into a Reminder object
        
        # Example:
        # row = {"item_id": "123", "reminder_date": "2026-07-10", "type": "expiry"}
        # Reminder(**row)
        # Is equivalent to:
        # Reminder(item_id="123", reminder_date="2026-07-10", type="expiry")

    except Exception as e:
        print(f"Error fetching upcoming reminders: {e}")
        return []

async def auto_generate_expiry_reminders() -> int:
    """Automatically generate reminders for all items expiring within 30 days. Returns count of reminders created."""
    try:
        # First fetch all items that are expiring within the next 30 days
        rows = await fetch_all(
            conn,
            """
            SELECT * FROM drug_items
            """,
            (date.today() + timedelta(days=30),) # days are PASSED BY VALUE
        )
        count = 0
        for row in rows:
            item_id = row['id']
            expiry_date = row['expiry_date']
            # Check if an expiry reminder already exists for this item and date
            existing_reminders = await fetch_all(
                """
                SELECT * FROM reminders
                WHERE item_id = ? AND reminder_date = ? AND type = 'expiry'
                """,
                (item_id, expiry_date)
            )
            if not existing_reminders:
                # Set a new reminder
                success = await set_reminder(item_id, expiry_date, 'expiry')
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