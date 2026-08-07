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
| Database | PostgreSQL (`psycopg2`) |

## Features

**Barista interface** — take orders, view recipes with step-by-step preparation,
track completed orders

**Manager interface** — inventory management with purchasing, employee records
(add, edit salary, remove), accounting reports with running balance

**Behind the scenes** — recording a sale validates the order against the menu,
decrements ingredient stock, and updates the account balance in one flow

## Data model

Nine tables, designed collaboratively by the team:

- `Employee`, with `Barista` and `Manager` as one-to-one specializations
- `Menu`, `Recipe`, `InventoryManagement` — recipes link menu items to ingredients
  with quantities and ordered preparation steps
- `Sale`, `Promotion`, `Accounting`

Constraints are enforced at the model level: unique-together on natural keys,
validated choice fields for payment method and drink type, and `Decimal` columns
for all monetary values. The relational model diagram is in `Relational-Model.pdf`.

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

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET, POST | `/baristas/`, `/managers/` | Staff records; supports `?first_name=` filtering |
| GET, POST | `/inventory/` | Ingredient stock |
| PATCH | `/inventory/update/` | Add purchased stock |
| GET, POST | `/menu/` | Drinks offered |
| GET, POST | `/recipes/` | Ingredients and steps; supports `?recipe_name=` filtering |
| GET, POST | `/promotions/` | Time-based promotional pricing |
| GET, POST | `/sales/` | Sale records |
| POST | `/sales/record-sale` | Record a sale, decrement stock, update balance |
| GET, POST | `/accounting/` | Balance history |
| GET, POST | `/accounting/check/` | Current balance / record a purchase |
| DELETE | `/employees/delete/?ssn=` | Remove an employee |
| PUT | `/employees/update-salary/?ssn=` | Update salary |

## Team

Three-person project — Milan Joksimovic, Osman Khan, Jonathan Hung.
The schema was designed collaboratively; implementation was split across the stack.

**My contributions (13 of 40 commits):**

- Lead author of the REST API layer — endpoints and routing across inventory,
  sales, menu, recipes, promotions, accounting, and employee management
- The sale-recording flow: order validation, ingredient stock decrement, and
  running account balance
- Barista and manager dashboards, and the inventory management interface in React
- Shared order state across barista pages using React Context

## What I would do differently

Revisiting this a year later, these are the changes I would make:

**Use the Recipe table in the sale flow.** `RecordSaleAPIView` hardcodes ingredient
quantities for two drinks, even though the `Recipe` table already stores exactly
that data. Adding a third drink today means changing code. It should query recipes
and decrement generically.

**Wrap the sale in a transaction.** Recording a sale writes to three tables in
sequence, so a failure partway through can decrement inventory without recording
the sale. `@transaction.atomic` plus `select_for_update()` on the inventory rows
would also close a race condition on concurrent sales.

**Move authentication server-side.** Login is currently handled in the browser
against `localStorage`, with roles inferred from the username string. It should use
Django's auth system with hashed passwords, session handling, and permission classes
on the API — which is entirely open right now.

**Reconsider SSN as a primary key.** It came from the assignment's ER diagram, but a
numeric column strips leading zeros, and sensitive identifiers shouldn't be keys. A
surrogate key would be correct.

**Configure the API URL once.** The frontend hardcodes `http://localhost:8000` in
every request, so the app can't be deployed without editing each file.
