# MedLife — Frontend ↔ Backend Connection Guide

This covers exactly one thing: how the frontend (`frontend/*.html`) talks to the backend (`api_server.py`), and how to wire up the pages that aren't connected yet. Assumes the backend and DB layer already exist and work — this is not a general project overview.

---

## 1. The shape of the connection

```
Browser (frontend/*.html)
    │
    │  fetch() calls, via frontend/js/api.js
    ▼
FastAPI backend (api_server.py) — http://localhost:8000
    │
    │  execute_write / fetch_one / fetch_all
    ▼
SQLite (medlife.db) — via core/database/connection.py
```

The frontend never touches the database directly. It only ever calls the backend over HTTP. This means the browser doesn't need to know anything about SQL, table names, or the DB file — it only needs to know the API's URLs and JSON shapes.

## 2. Running both sides

```bash
python3 run_dev.py
```

- Backend: `http://localhost:8000` (docs at `/docs`)
- Frontend: `http://localhost:5500`

Keep both running while you develop — the frontend won't have anything to talk to if the backend isn't up.

## 3. Why cross-origin calls work at all

The frontend (`:5500`) and backend (`:8000`) are different origins as far as the browser is concerned, so normally it would block `fetch()` calls between them. `api_server.py` already has this open:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
```

You don't need to do anything about this yourself — it's handled. (Just know that `allow_origins=["*"]` is a dev-only setting; it should be locked down to a specific origin before this goes anywhere production-like.)

## 4. The shared client: `frontend/js/api.js`

Every page includes this once, then calls its methods instead of writing raw `fetch()` calls inline:

```html
<script src="js/api.js"></script>
```

Currently available methods (all return Promises, all talk to `/drug-items`):

```js
MedLifeAPI.listDrugItems(filters)   // filters optional: { expiry_before, low_stock_threshold, shelf_location }
MedLifeAPI.getDrugItem(id)
MedLifeAPI.createDrugItem(item)     // item = plain object matching DrugItem fields
MedLifeAPI.updateDrugItem(id, updates)
MedLifeAPI.deleteDrugItem(id)
```

Errors from the backend (validation failures, 404s, etc.) come back as a thrown `Error` with the FastAPI `detail` message — wrap calls in `try/catch`.

**If you need to talk to a table that doesn't have endpoints yet** (e.g. `reminders`), those need to be added to `api_server.py` first — the frontend can only call what the backend exposes. See §7.

## 5. Wiring a page: the pattern

Every page follows the same three steps:

1. Include `api.js`
2. Call the relevant `MedLifeAPI.*` method
3. Take the returned data (or the error) and update the DOM

### Reading data on page load (`inventory.html`)

```html
<script src="js/api.js"></script>
<script>
  async function loadInventory() {
    try {
      const items = await MedLifeAPI.listDrugItems();
      const tbody = document.getElementById("inventory-body");
      tbody.innerHTML = items.map(item => `
        <tr>
          <td>${item.name}</td>
          <td>${item.batch_number}</td>
          <td>${item.expiry_date}</td>
          <td>${item.quantity}</td>
        </tr>
      `).join("");
    } catch (err) {
      console.error("Failed to load inventory:", err);
    }
  }

  loadInventory();
</script>
```

### Submitting a form (`new_medicine.html`)

```html
<form id="new-medicine-form">
  <input name="id" placeholder="ID" required>
  <input name="name" placeholder="Name" required>
  <input name="date_of_purchase" type="date" required>
  <input name="date_of_manufacture" type="date" required>
  <input name="expiry_date" type="date" required>
  <input name="batch_number" placeholder="Batch number" required>
  <input name="quantity" type="number" value="0">
  <input name="price" type="number" step="0.01" value="0">
  <button type="submit">Add Medicine</button>
</form>

<script src="js/api.js"></script>
<script>
  document.getElementById("new-medicine-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = Object.fromEntries(new FormData(e.target));
    formData.quantity = Number(formData.quantity);
    formData.price = Number(formData.price);

    try {
      await MedLifeAPI.createDrugItem(formData);
      alert("Medicine added!");
      e.target.reset();
    } catch (err) {
      alert(`Error: ${err.message}`);
    }
  });
</script>
```

### Deleting a row (pattern for a delete button inside a rendered table row)

```js
async function handleDelete(id) {
  if (!confirm(`Delete item ${id}?`)) return;
  try {
    await MedLifeAPI.deleteDrugItem(id);
    loadInventory();  // re-fetch and re-render
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}
```

## 6. Testing the connection is actually working

1. Start both servers: `python3 run_dev.py`
2. Open `http://localhost:5500/new_medicine.html`, submit the form
3. Open `http://localhost:5500/inventory.html` — the new item should appear
4. If nothing shows up, open the browser DevTools console (F12) — `fetch()` errors, CORS errors, or JSON parsing errors will show there first. Also check the terminal running `run_dev.py` — a 4xx/5xx from the backend will be logged there.

Common breakages:
| Symptom | Likely cause |
|---|---|
| `Failed to fetch` in console | Backend isn't running, or wrong port in `api.js`'s `BASE_URL` |
| Item added but list doesn't update | Forgot to re-call `loadInventory()` after a successful create/delete |
| 422 error on submit | Form field names don't match `DrugItem`'s expected fields exactly, or a date field is empty |
| 409 error on submit | Reused an `id` that already exists — `drug_items.id` must be unique |

## 7. Adding a connection for a table that isn't wired yet (e.g. `reminders`)

Two steps, both needed:

1. **Backend:** add routes to `api_server.py` for the new table, copying the `drug_items` block as a template (Pydantic model + GET/POST/PATCH/DELETE routes using `fetch_one`/`fetch_all`/`execute_write`).
2. **Frontend:** add corresponding methods to `api.js` (same pattern as the existing `drug_items` methods), then wire the relevant HTML page to call them, following §5 above.

Do the backend route first and confirm it works via `/docs` (test it there directly) before wiring any frontend JS to it — isolates whether a bug is in the API or in the page's JS.
