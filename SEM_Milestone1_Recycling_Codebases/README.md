# CSEB5213 Milestone 1 — Recycling Booking Prototype

Three small Flask + SQLite implementations of the **same** local prototype API: `codebase_a` (single-file baseline), `codebase_b` (layered baseline), and `codebase_a_refactored` (refactoring demonstration). These are class-project implementations inspired by Trash4Cash, **not** Trash4Cash's source code, API, pricing, booking process or official services.

## API contract
- `GET /api/materials` — illustrative tariff list (RM/kg)
- `POST /api/quote` — JSON `{ "item_type": "paper", "weight_kg": 2 }`
- `POST /api/bookings` — JSON `{ "user_id": 7, "item_type": "paper", "weight_kg": 2, "address": "Putrajaya", "pickup_date": "2026-11-02" }`
- `GET /api/bookings/1` — fetch persisted prototype booking

## Run in VS Code terminal
1. Create virtual environment: `python -m venv .venv`.
2. Activate it (`.venv\\Scripts\\activate` on Windows, `source .venv/bin/activate` on Mac/Linux).
3. `pip install -r requirements.txt` (requires an internet connection once).
4. `cd codebase_a` and `python app.py`. Repeat with `codebase_b` or `codebase_a_refactored` for the comparison (stop the server before changing folders because all use port 5000).
5. Open `http://127.0.0.1:5000/api/materials` or use Thunder Client/Postman for POST requests.
6. From the project root, run `python tests/verify.py codebase_a`, `python tests/verify.py codebase_b`, and `python tests/verify.py codebase_a_refactored` for the isolated handler-level smoke tests. If Flask is not installed, the test harness provides a minimal *test-only* interface shim. That verifies logic/persistence but is **not** an HTTP integration test.

## Scope and limitations
Rates are **synthetic assumptions** for educational comparisons (paper RM0.50/kg, plastic RM0.80/kg, metal RM1.20/kg, ewaste RM2.50/kg). No payments, collection dispatch, geolocation, authentication, multi-tenancy, live tariff feeds or integrations. Booking creation stores `pending` state, but pickup is not physically scheduled. SQLite stores demo-only records; do not place real personal addresses or IDs into this experiment. Future feature changes should be treated as Milestone 2 modifications, not as already implemented features.
