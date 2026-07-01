# import relevant data model
from core.models.data_models import Reminder

# database imports
from core.database.connection import get_connection, execute_write, fetch_all
conn = get_connection()

# Reminder functions
async def set_reminder(
    item_id: str,
    reminder_date: date,
    reminder_type: str
) -> bool:
    """Set a reminder for batch or expiry date."""
    try:
        await execute_write(
            conn,
            # the patterm below prevents SQL injection attacks
            """
            INSERT INTO reminders (item_id, reminder_date, type)
            VALUES (?, ?, ?)
            """,
            (item_id, reminder_date, reminder_type)
        )
        return True
    except Exception as e:
        print(f"Error setting reminder: {e}")
        return False
    finally:
        await close_database()

async def get_upcoming_reminders(days_ahead: int = 30) -> List[Reminder]:
    """Get reminders for the next N days."""
    try:
        rows = await fetch_all(
            conn,
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
    finally:
        await close_database()

async def auto_generate_expiry_reminders() -> int:
    """Automatically generate reminders for all items expiring within 30 days. Returns count of reminders created."""
    try:
        # First fetch all items that are expiring within the next 30 days
        rows = await fetch_all(
            conn,
            """
            SELECT * FROM drug_items
            WHERE expiry_date <= ?
            """,
            (date.today() + timedelta(days=30),) # days are PASSED BY VALUE
        )
        count = 0
        for row in rows:
            item_id = row['id']
            expiry_date = row['expiry_date']
            # Check if an expiry reminder already exists for this item and date
            existing_reminders = await fetch_all(
                conn,
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
    finally:
        await close_database()