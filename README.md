# Coffee Shop Ordering & Inventory System

[![tests](https://github.com/milanj08/Coffee-Shop-App/actions/workflows/tests.yml/badge.svg)](https://github.com/milanj08/Coffee-Shop-App/actions/workflows/tests.yml)

A full-stack cafe management application with separate interfaces for baristas and
managers. Baristas take and prepare orders; managers handle inventory, staffing,
and accounting. Built for CS 480 (Database Systems) at the University of Illinois
Chicago, Spring 2025.

## Stack

| Layer | Technology |
| --- | --- |
| Backend | Django 5.2, Django REST Framework 3.16 |
| Frontend | React, React Router, axios |
| Database | SQLite |
| Auth | DRF token authentication, role permissions derived from the schema |
| CI | GitHub Actions — 42 tests on every push |

## Features

**Authentication** — token-based sign-in, with barista and manager roles derived
from the database and enforced on every endpoint. A barista can read the menu
and record sales; only a manager can change prices, recipes, stock, employee
records, or the accounts.

**Barista interface** — take orders with a running total, view recipes with
step-by-step preparation, track completed orders

**Manager interface** — inventory management with purchasing, employee records
(add, edit salary, remove), accounting reports with running balance

**Behind the scenes** — recording a sale reads the ingredient amounts each drink
needs from the `Recipe` table, prices the order from the menu server-side, and
deducts stock inside a transaction with row locking. If any ingredient is short
the whole order is refused with a 409 and nothing is written. Adding a new drink
requires no code changes.

## Data model

Nine tables, designed collaboratively by the team:

- `Employee`, with `Barista` and `Manager` as one-to-one specializations
- `Menu`, `Recipe`, `InventoryManagement` — recipes link menu items to ingredients
  with quantities and ordered preparation steps
- `Sale`, `Promotion`, `Accounting`

Constraints are enforced at the model level: unique-together on natural keys,
validated choice fields for payment method and drink type, and `Decimal` columns
for all monetary values. The relational model diagram is in `Relational-Model.pdf`.

Two notes on the design, both inherited from the assignment's ER model. `Employee`
uses SSN as its primary key, so it is copied into every child table and appears in
URLs; a surrogate key with SSN as an encrypted non-key column would be correct.
And `Promotion` exists in the schema but no code path reads it — the promotional
pricing flow was never built.

## Running locally

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements_backend.txt
python manage.py migrate
python manage.py loaddata demo
python manage.py runserver
```

Runs on `http://localhost:8000`. `loaddata demo` seeds a menu, ingredients,
recipes, employees, and a starting account balance so the screens aren't empty.

### Signing in

The fixture creates two accounts:

| Username | Password | Role |
|---|---|---|
| `manager` | `CoffeeShop2026` | Manager — inventory, employees, accounting |
| `barista` | `CoffeeShop2026` | Barista — taking orders |

You can also register your own account from the login screen. **Self-signup
always creates a barista** — the registration serializer has no `role` field,
so a request asking for one is ignored. Manager accounts are created by a
manager.

Role is derived server-side from the `Barista` and `Manager` tables on every
request. The frontend stores a role in `localStorage` and uses it to decide
which screens to offer, but editing that value only changes the menu you see:
the API re-derives the role and returns 403. See `cafe/permissions.py`.

> Authentication uses DRF token auth, with the token in `localStorage`. That
> means any script on the page can read it, so an XSS bug would leak it. An
> `httpOnly` cookie is stronger, at the cost of session auth plus
> CORS-with-credentials and CSRF handling across two origins — a trade-off
> taken deliberately, not overlooked.

> **On the database.** This runs on SQLite so it can be cloned and started without
> installing a database server. PostgreSQL was the original course requirement and
> `psycopg2` was pinned in the requirements file, but `settings.py` has configured
> SQLite in every commit — the project was in fact developed against SQLite.
>
> One consequence worth knowing: `select_for_update()` in `cafe/services.py` is a
> **no-op on SQLite**. The row locking that prevents two concurrent sales from
> losing an inventory deduction is written correctly but only enforced on
> PostgreSQL or MySQL, which is what this would be deployed against.

**Frontend**

```bash
cd frontend
npm install
npm start
```

Runs on `http://localhost:3000` and expects the backend on port 8000.

## API

All endpoints are under `/api/`.

All of them require an `Authorization: Token <key>` header except register and
login. Employee records, accounting, and every write to the menu, recipes, or
inventory are manager-only.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/auth/register/` | Create an account — always a barista |
| POST | `/auth/login/` | Exchange credentials for a token |
| POST | `/auth/logout/` | Delete the caller's token |
| GET | `/auth/me/` | Current account and role |
| GET, POST | `/baristas/`, `/managers/` | Staff records; supports `?first_name=` filtering |
| GET, POST | `/inventory/` | Ingredient stock |
| PATCH | `/inventory/update/` | Add purchased stock |
| GET, POST | `/menu/` | Drinks offered |
| GET, POST | `/recipes/` | Ingredients and steps; supports `?recipe_name=` filtering |
| GET, POST | `/promotions/` | Time-based promotional pricing |
| GET, POST | `/sales/` | Sale records |
| POST | `/sales/record-sale` | Record a sale, decrement stock, update balance |
| GET, POST | `/accounting/` | Balance history |
| GET, POST | `/accounting/balance/` | Current balance (GET) / record a purchase (POST) |
| DELETE | `/employees/delete/?ssn=` | Remove an employee and their login |
| PATCH | `/employees/update-salary/?ssn=` | Update salary |

## Team

Three-person project — Milan Joksimovic, Osman Khan, Jonathan Hung.
The schema was designed collaboratively; implementation was split across the stack.

**My contributions (28 of 55 commits):**

- The three business-logic endpoints — recording a sale, restocking inventory,
  and the account balance
- Barista order entry, recipe display, and the inventory management interface
  in React
- Shared order state across barista pages using React Context

Jonathan implemented the models and serializers; Osman built the employee
management screens and the accounting report.

### Revisited solo, August 2026

Everything below was done alone, eight months after the course ended:

- Sale processing rewritten to read ingredient amounts from the `Recipe` table
  rather than hardcoded per-drink branches
- Order pricing moved server-side; stock deduction wrapped in a transaction with
  row locking, returning 409 when an order cannot be fulfilled
- Token authentication with role permissions derived from the `Barista` and
  `Manager` tables, replacing a browser-side login
- 42 tests, a seed fixture, and GitHub Actions running the suite on every push

