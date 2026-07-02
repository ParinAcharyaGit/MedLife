import json
import urllib.request
import urllib.error

data = {
    "id": "test-123",
    "name": "Test Medicine",
    "company_sourced_from": "Test Company",
    "batch_number": "BATCH-001",
    "serial_number": "SN-001",
    "quantity": 100,
    "price": 10.00,
    "shelf_location": "a1",
    "date_of_purchase": "2026-01-15",
    "date_of_manufacture": "2026-01-15",
    "expiry_date": "2027-01-15"
}

req = urllib.request.Request(
    'http://localhost:8000/drug-items',
    data=json.dumps(data).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST'
)

try:
    with urllib.request.urlopen(req) as response:
        print("Success:")
        print(response.read().decode())
except urllib.error.HTTPError as e:
    print(f"Error: {e.code}")
    print(e.read().decode())
except Exception as e:
    print(f"Exception: {e}")
