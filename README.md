# 📦 InvenTrack — Inventory Management System

A mini project for Computer Science coursework: a full-stack inventory
management system with login, dashboard, product/category/supplier
management, sales & purchase workflows with automatic stock updates,
low-stock & expiry alerts, reports with charts, invoice generation,
CSV export, and dark/light mode.

**Stack:** Flask (Python) · MySQL · HTML/CSS/JavaScript · Chart.js

## 1. Project Flow

```
LOGIN -> DASHBOARD -> ADD PRODUCT -> VIEW PRODUCT -> MAKE SALE
-> STOCK AUTO-DECREASES -> LOW STOCK ALERT -> MAKE PURCHASE
-> STOCK AUTO-INCREASES -> REPORTS/CHARTS -> DATABASE
```

## 2. Folder Structure

```
inventory_system/
|-- app.py                # Flask app: all routes/logic
|-- schema.sql             # MySQL database schema + seed data
|-- requirements.txt
|-- templates/              # Jinja2 HTML templates
|   |-- base.html
|   |-- login.html
|   |-- dashboard.html
|   |-- products.html
|   |-- product_form.html
|   |-- categories.html
|   |-- suppliers.html
|   |-- sales.html
|   |-- sale_new.html
|   |-- purchases.html
|   |-- purchase_new.html
|   |-- invoice.html
|   `-- reports.html
`-- static/
    |-- css/style.css
    `-- js/theme.js
```

## 3. Setup Instructions

### Step 1 - Install MySQL & create the database
Make sure MySQL Server is installed and running, then:
```bash
mysql -u root -p < schema.sql
```
This creates the `inventory_db` database with all tables and some seed
categories/suppliers.

### Step 2 - Install Python dependencies
```bash
cd inventory_system
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### Step 3 - Configure database credentials
Open `app.py` and edit the `DB_CONFIG` dictionary near the top with your
MySQL username/password:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database": "inventory_db",
}
```

### Step 4 - Create the first admin login
```bash
flask --app app.py seed-admin
```
This creates an admin account: **username `admin`, password `admin123`**
(change the password after first login in a real deployment - this demo
has no "change password" screen, but you can update the `users` table
directly, or add one as an extra feature).

### Step 5 - Run the app
```bash
python app.py
```
Visit **http://127.0.0.1:5000** in your browser.

## 4. Feature Checklist (for your report/viva)

| Feature | Where it's implemented |
|---|---|
| Login system | `app.py` -> `/login`, sessions, hashed passwords (Werkzeug) |
| Dashboard | `/dashboard` - totals, stock value, today's sales, alerts |
| Product CRUD | `/products`, `/products/add`, `/products/edit/<id>`, `/products/delete/<id>` |
| Categories | `/categories` |
| Low stock alert | Dashboard query: `quantity <= min_stock` |
| Expiry alert | Dashboard query: `expiry_date` within 30 days |
| Supplier management | `/suppliers` |
| Sales (stock decreases) | `/sales/new` - inserts sale + sale_items, then `UPDATE products SET quantity = quantity - qty` |
| Purchases (stock increases) | `/purchases/new` - inserts purchase + purchase_items, then `UPDATE products SET quantity = quantity + qty` |
| Reports & charts | `/reports` + `/api/reports/*` (JSON) rendered with Chart.js |
| Search & filter | `/products?q=...&category=...` |
| Invoice generation | `/invoice/<sale_id>` (printable via browser print) |
| Export CSV | `/export/products`, `/export/sales` |
| Dark/light mode | `static/js/theme.js` + CSS variables, saved in `localStorage` |
| Responsive UI | CSS grid/flexbox + a mobile breakpoint in `style.css` |

## 5. Possible Extensions (for extra marks)
- Role-based permissions (admin vs staff - the `role` column is already there, just add `@admin_required` where needed)
- PDF invoices (e.g. with `reportlab` or `wkhtmltopdf`)
- Barcode scanning for product lookup
- Multi-user activity log

## 6. Notes
- This project uses plain SQL via `mysql-connector-python` (no ORM) so
  it's easy to explain in a viva - every query is visible in `app.py`.
- Passwords are stored as salted hashes (`werkzeug.security`), never in
  plain text.
- All stock changes happen inside the same DB transaction as the sale/
  purchase record, so stock and history always stay in sync.
