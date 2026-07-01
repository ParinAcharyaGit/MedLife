# MedLife Developer Guide

This guide explains how to integrate the HTML frontend with the Python API server and ensures that frontend fields, parameters, and requests match the backend logic.

## System Overview

The MedLife application consists of:
- **Backend API Server**: Python/FastAPI server (`api_server.py`) exposing REST endpoints
- **Frontend**: HTML/Tailwind CSS files in the `frontend/` directory
- **Core Logic**: Python modules in `core/` directory handling database operations

## Setting Up the Development Environment

### 1. Create and Activate Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## Running the Application

### 1. Start the API Server
```bash
# Make sure your virtual environment is activated
uvicorn api_server:app --reload --port 8000
```

The server will be available at `http://localhost:8000` with interactive API docs at `http://localhost:8000/docs`.

### 2. Serve the Frontend
The frontend HTML files can be served in several ways:

**Option A: Simple Static Server** (for development)
```bash
# From the frontend directory
python -m http.server 8080
```
Then access the frontend at `http://localhost:8080`

**Option B: Serve via FastAPI** (recommended for production)
Modify `api_server.py` to serve static files:
```python
from fastapi.staticfiles import StaticFiles
app.mount("/static", StaticFiles(directory="frontend"), name="static")
```

## API Endpoints and Frontend Integration

### Drug Inventory Management

#### GET `/drug-items` - List Drug Items
**Backend Function**: `list_drug_items()` in `core/inventory/drug_item.py`
**Parameters** (query string):
- `expiry_before`: ISO date string (YYYY-MM-DD)
- `low_stock_threshold`: Integer
- `shelf_location`: String

**Frontend Usage** (inventory.html):
- Populates the inventory table
- Filters can be added via URL parameters
- Example: `/drug-items?low_stock_threshold=10` shows low stock items

#### GET `/drug-items/{item_id}` - Get Single Drug Item
**Backend Function**: `get_drug_item()` in `core/inventory/drug_item.py`
**Path Parameter**: `item_id` (string)

**Frontend Usage**:
- Used when editing a specific drug item
- Fetches details to pre-fill the edit form

#### POST `/drug-items` - Create New Drug Item
**Backend Function**: `add_drug_item()` in `core/inventory/drug_item.py`
**Request Body**: JSON matching `DrugItemIn` Pydantic model

**Field Mapping** (new_medicine.html → API):
| Frontend Field | Backend Field | Type | Notes |
|----------------|---------------|------|-------|
| Medicine Name | `name` | string | Required |
| Company Sourced From | `company_sourced_from` | string | Required |
| Batch Number | `batch_number` | string | Required |
| Serial Number | `serial_number` | string | Optional |
| Quantity | `quantity` | integer | Required, min 0 |
| Price per Unit ($) | `price` | float | Required, step 0.01 |
| Shelf Location | `shelf_location` | string | Required (from dropdown) |
| Date Brought In | `date_of_purchase` | date | Required (date input) |
| Expiry Date | `expiry_date` | date | Required (date input) |

**Frontend Implementation**:
- Form submission should send JSON to `/drug-items` endpoint
- On success: Show confirmation and redirect to inventory view
- On error: Display validation errors from API response

#### PATCH `/drug-items/{item_id}` - Update Drug Item
**Backend Function**: `update_drug_item()` in `core/inventory/drug_item.py`
**Path Parameter**: `item_id` (string)
**Request Body**: JSON with only fields to update (partial update)

**Frontend Usage**:
- Edit form in inventory.html (edit button per row)
- Should send only modified fields
- Example: If only quantity changed, send `{"quantity": 25}`

#### DELETE `/drug-items/{item_id}` - Delete Drug Item
**Backend Function**: `delete_drug_item()` in `core/inventory/drug_item.py`
**Path Parameter**: `item_id` (string)

**Frontend Usage**:
- Delete button in inventory.html table
- Should confirm deletion before sending request
- On success: Remove row from table

### Stock Tracking Management

#### POST `/stock-records` - Record Stock Movement
**Backend Function**: Uses `record_stock_in()` or `record_stock_out()` based on quantity sign
**Request Body**: JSON matching `StockRecordIn` Pydantic model

**Field Mapping**:
| Field | Type | Description |
|-------|------|-------------|
| item_id | string | ID of the drug item |
| quantity_change | integer | Positive for stock IN, negative for stock OUT |
| timestamp | date | Date of the stock movement |
| reason | string | Optional reason for the stock change |

**Frontend Usage**:
- Used when recording receipts or dispenses of medication
- Positive quantities represent stock received
- Negative quantities represent stock used/dispensed

#### GET `/stock-records/{item_id}` - Get Stock History
**Backend Function**: `get_stock_history()` in `core/inventory/stock_tracking.py`
**Path Parameter**: `item_id` (string)
**Query Parameters**:
- `start_date`: ISO date string (optional)
- `end_date`: ISO date string (optional)

**Frontend Usage**:
- Display stock movement history for a specific item
- Can filter by date range

#### POST `/stock/in/{item_id}` - Record Stock In
**Backend Function**: `record_stock_in()` in `core/inventory/stock_tracking.py`
**Path Parameter**: `item_id` (string)
**Query Parameters**:
- `quantity`: Integer (required)
- `received_date`: ISO date string (optional, defaults to today)

**Frontend Usage**:
- Quick endpoint for recording stock received
- Alternative to using `/stock-records` with positive quantity

#### POST `/stock/out/{item_id}` - Record Stock Out
**Backend Function**: `record_stock_out()` in `core/inventory/stock_tracking.py`
**Path Parameter**: `item_id` (string)
**Query Parameters**:
- `quantity`: Integer (required)
- `used_date`: ISO date string (optional, defaults to today)

**Frontend Usage**:
- Quick endpoint for recording stock used/dispensed
- Alternative to using `/stock-records` with negative quantity

### Reminder Management

#### POST `/reminders` - Create Reminder
**Backend Function**: `set_reminder()` in `core/inventory/reminders.py`
**Request Body**: JSON matching `ReminderIn` Pydantic model

**Field Mapping**:
| Field | Type | Description |
|-------|------|-------------|
| item_id | string | ID of the drug item |
| reminder_date | date | Date for the reminder |
| type | string | 'batch', 'expiry', or 'custom' |
| message | string | Reminder message/description |

**Frontend Usage**:
- Create reminders for batch tracking or expiry notifications
- Can be used for custom reminders as well

#### GET `/reminders` - Get Upcoming Reminders
**Backend Function**: `get_upcoming_reminders()` in `core/inventory/reminders.py`
**Query Parameter**:
- `days_ahead`: Integer (default 30) - how many days ahead to look

**Frontend Usage**:
- Display upcoming reminders for dashboard or alerts page
- Shows reminders for the next N days

#### POST `/reminders/auto-generate` - Generate Expiry Reminders
**Backend Function**: `auto_generate_expiry_reminders()` in `core/inventory/reminders.py`
**Request Body**: None
**Response**: JSON with count of reminders generated

**Frontend Usage**:
- Automatically generate expiry reminders for all items expiring soon
- Typically run as a scheduled task or manual operation
- Returns the number of new reminders created

### Health Check Endpoint

#### GET `/health` - Health Check
**Backend Function**: Simple health check
**Response**: JSON status indicator

**Frontend Usage**:
- Verify API server is running and responsive
- Can be used for monitoring or connection testing

## Data Flow Examples

### Adding a New Medicine
1. User fills form in `new_medicine.html`
2. On submit, frontend sends POST to `/drug-items` with JSON body:
   ```json
   {
     "id": "MED001",
     "name": "Amoxicillin 500mg",
     "date_of_purchase": "2024-01-15",
     "date_of_manufacture": "2023-11-01",
     "expiry_date": "2025-01-15",
     "batch_number": "AX-2024-001",
     "serial_number": "SN-1001",
     "shelf_location": "A1",
     "company_sourced_from": "Global Pharma Co.",
     "quantity": 100,
     "price": 12.50
   }
   ```
3. API validates and stores in database
4. API returns the created item with any server-generated fields
5. Frontend shows success message and redirects to inventory view

### Viewing Inventory
1. Frontend loads `inventory.html`
2. JavaScript sends GET request to `/drug-items` (with optional filters)
3. API returns array of drug items
4. Frontend populates table rows with item data
5. Table shows: Medicine name, serial/batch, dates, quantity, location, source, price, and action buttons

### Recording Stock Movement
1. User records receipt or dispense of medication
2. Frontend sends POST to `/stock/in/{item_id}` or `/stock/out/{item_id}` 
   OR sends POST to `/stock-records` with positive/negative quantity
3. API records the stock movement in the database
4. Frontend updates display if needed (e.g., refreshes stock count)

### Setting Reminders
1. User sets a reminder for a medication (e.g., expiry notification)
2. Frontend sends POST to `/reminders` with reminder details
3. API stores the reminder in the database
4. Frontend shows confirmation and may refresh reminder list

### Viewing Reminders
1. User navigates to reminders/alerts page
2. Frontend sends GET to `/reminders` with optional `days_ahead` parameter
3. API returns list of upcoming reminders
4. Frontend displays reminders in a list or calendar view

### Generating Expiry Reminders
1. User triggers automatic expiry reminder generation
2. Frontend sends POST to `/reminders/auto-generate`
3. API scans for items expiring soon and creates reminders
4. API returns count of new reminders created
5. Frontend shows confirmation message

## Implementation Notes

### Date Handling
- Frontend uses HTML `<input type="date">` which returns YYYY-MM-DD format
- Backend expects Python `date` objects or ISO strings
- API automatically handles conversion via Pydantic models

### Error Handling
- API returns appropriate HTTP status codes:
  - 200: Success
  - 201: Created
  - 400: Bad Request (validation errors)
  - 404: Not Found
  - 409: Conflict (duplicate ID)
  - 500: Internal Server Error
- Frontend should handle these statuses and display user-friendly messages

### Security Considerations
- CORS is currently set to allow all origins (`*`)
- For production, restrict `allow_origins` to your frontend domain
- Consider adding authentication for sensitive operations

### Database Initialization
- The API server automatically initializes the SQLite database on startup
- Database file: `medlife.db` in project root
- Schema is defined in `core/database/schemas.py`

## Testing the Integration

1. Start the API server: `uvicorn api_server:app --reload`
2. Serve frontend: `cd frontend && python -m http.server 8080`
3. Visit `http://localhost:8080/new_medicine.html` to test adding medicines
4. Visit `http://localhost:8080/inventory.html` to view inventory
5. Check API docs at `http://localhost:8000/docs` to test endpoints directly

## Future Enhancements

1. Add user authentication endpoints (login/logout)
2. Implement transfer/donation functionality for clinic-to-clinic transfers
3. Create forecasting algorithms for restocking recommendations
4. Add upload/export functionality for CSV data
5. Enhance UI with loading states and better error handling
6. Implement advanced filtering and search capabilities
7. Add reporting and analytics endpoints