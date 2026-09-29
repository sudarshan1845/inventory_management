"""
Inventory Management System - Flask Backend
Mini Project - BSc/BCA/Engineering Computer Science

Run:
    pip install -r requirements.txt
    mysql -u root -p < schema.sql
    python app.py
"""

import csv
import io
from datetime import date, datetime, timedelta
from functools import wraps

import mysql.connector
from flask import (Flask, render_template, request, redirect, url_for,
                    session, flash, jsonify, Response)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change-this-secret-key-in-production"

# ---------------------- DATABASE CONFIG ----------------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Novivothing#1",   # <-- change this
    "database": "inventory_db",
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


def query(sql, params=None, fetch=False, one=False, commit=False):
    """Small helper to avoid repeating boilerplate everywhere."""
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(sql, params or ())
    result = None
    if fetch:
        result = cur.fetchone() if one else cur.fetchall()
    last_id = cur.lastrowid
    if commit:
        conn.commit()
    cur.close()
    conn.close()
    return result if fetch else last_id


# ---------------------- AUTH HELPERS ----------------------
def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*a, **kw)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if session.get("role") != "admin":
            flash("Admins only.", "error")
            return redirect(url_for("dashboard"))
        return f(*a, **kw)
    return wrapper


# ---------------------- SEED FIRST ADMIN (one-time helper) ----------------------
@app.cli.command("seed-admin")
def seed_admin():
    """Run: flask --app app.py seed-admin  (creates admin/admin123 if not present)"""
    existing = query("SELECT id FROM users WHERE username=%s", ("admin",), fetch=True, one=True)
    if not existing:
        pw = generate_password_hash("admin123")
        query("INSERT INTO users (username, password_hash, role) VALUES (%s,%s,%s)",
              ("admin", pw, "admin"), commit=True)
        print("Admin created -> username: admin | password: admin123")
    else:
        print("Admin already exists.")


# ---------------------- LOGIN / LOGOUT ----------------------
@app.route("/", methods=["GET"])
def index():
    return redirect(url_for("dashboard") if "user_id" in session else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = query("SELECT * FROM users WHERE username=%s", (username,), fetch=True, one=True)
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------- CHART DATA HELPERS ----------------------
def chart_data():
    """All numbers used by the dashboard/report charts (plain floats/ints/strings)."""
    rows = query("""SELECT DATE(created_at) d, SUM(total_amount) total FROM sales
                     WHERE created_at >= %s GROUP BY DATE(created_at)""",
                 (date.today() - timedelta(days=6),), fetch=True)
    days = {str(date.today() - timedelta(days=i)): 0.0 for i in range(6, -1, -1)}
    for r in rows:
        days[str(r["d"])] = float(r["total"])
    stock = query("""SELECT c.name, COALESCE(SUM(p.quantity),0) qty,
                      COALESCE(SUM(p.quantity*p.price),0) val
                      FROM categories c LEFT JOIN products p ON p.category_id=c.id
                      GROUP BY c.id HAVING qty > 0 ORDER BY qty DESC""", fetch=True)
    top = query("""SELECT p.name, SUM(si.quantity) sold FROM sale_items si
                    JOIN products p ON si.product_id=p.id
                    GROUP BY p.id ORDER BY sold DESC LIMIT 5""", fetch=True)
    return {
        "sales_labels": [d[5:] for d in days.keys()],
        "sales_values": list(days.values()),
        "cat_labels": [r["name"] for r in stock],
        "cat_qty": [int(r["qty"]) for r in stock],
        "cat_val": [float(r["val"]) for r in stock],
        "top_labels": [r["name"] for r in top],
        "top_values": [int(r["sold"]) for r in top],
    }


# ---------------------- DASHBOARD ----------------------
@app.route("/dashboard")
@login_required
def dashboard():
    total_products = query("SELECT COUNT(*) c FROM products", fetch=True, one=True)["c"]
    stock_value = query("SELECT COALESCE(SUM(price*quantity),0) v FROM products", fetch=True, one=True)["v"]
    total_sales_today = query(
        "SELECT COALESCE(SUM(total_amount),0) v FROM sales WHERE DATE(created_at)=CURDATE()",
        fetch=True, one=True)["v"]
    low_stock = query("SELECT * FROM products WHERE quantity <= min_stock ORDER BY quantity ASC",
                       fetch=True)
    expiring_soon = query(
        "SELECT * FROM products WHERE expiry_date IS NOT NULL "
        "AND expiry_date <= %s ORDER BY expiry_date ASC",
        (date.today() + timedelta(days=30),), fetch=True)
    todays_sales = query(
        "SELECT * FROM sales WHERE DATE(created_at)=CURDATE() ORDER BY created_at DESC",
        fetch=True)
    # Groceries get a tighter, more urgent expiry window (perishables)
    grocery_expiry = query(
        """SELECT p.* FROM products p JOIN categories c ON p.category_id=c.id
           WHERE c.name='Grocery' AND p.expiry_date IS NOT NULL
           AND p.expiry_date <= %s ORDER BY p.expiry_date ASC""",
        (date.today() + timedelta(days=7),), fetch=True)
    return render_template("dashboard.html", total_products=total_products,
                           stock_value=stock_value, total_sales_today=total_sales_today,
                           low_stock=low_stock, expiring_soon=expiring_soon,
                           todays_sales=todays_sales, grocery_expiry=grocery_expiry,
                           today=date.today(), charts=chart_data())


# ---------------------- PRODUCTS ----------------------
@app.route("/products")
@login_required
def products():
    search = request.args.get("q", "")
    category_id = request.args.get("category", "")
    sql = """SELECT p.*, c.name AS category_name, s.name AS supplier_name
             FROM products p
             LEFT JOIN categories c ON p.category_id=c.id
             LEFT JOIN suppliers s ON p.supplier_id=s.id
             WHERE p.name LIKE %s"""
    params = [f"%{search}%"]
    if category_id:
        sql += " AND p.category_id=%s"
        params.append(category_id)
    sql += " ORDER BY p.id DESC"
    rows = query(sql, params, fetch=True)
    categories = query("SELECT * FROM categories ORDER BY name", fetch=True)
    return render_template("products.html", products=rows, categories=categories,
                           search=search, selected_category=category_id)


@app.route("/products/add", methods=["GET", "POST"])
@login_required
def add_product():
    categories = query("SELECT * FROM categories ORDER BY name", fetch=True)
    suppliers = query("SELECT * FROM suppliers ORDER BY name", fetch=True)
    if request.method == "POST":
        f = request.form
        query("""INSERT INTO products (name, category_id, supplier_id, price, cost_price,
                  quantity, min_stock, expiry_date) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""",
              (f["name"], f.get("category_id") or None, f.get("supplier_id") or None,
               f["price"], f["cost_price"], f["quantity"], f["min_stock"],
               f.get("expiry_date") or None), commit=True)
        flash("Product added successfully.", "success")
        return redirect(url_for("products"))
    return render_template("product_form.html", categories=categories, suppliers=suppliers,
                           product=None)


@app.route("/products/edit/<int:pid>", methods=["GET", "POST"])
@login_required
def edit_product(pid):
    categories = query("SELECT * FROM categories ORDER BY name", fetch=True)
    suppliers = query("SELECT * FROM suppliers ORDER BY name", fetch=True)
    product = query("SELECT * FROM products WHERE id=%s", (pid,), fetch=True, one=True)
    if request.method == "POST":
        f = request.form
        query("""UPDATE products SET name=%s, category_id=%s, supplier_id=%s, price=%s,
                  cost_price=%s, quantity=%s, min_stock=%s, expiry_date=%s WHERE id=%s""",
              (f["name"], f.get("category_id") or None, f.get("supplier_id") or None,
               f["price"], f["cost_price"], f["quantity"], f["min_stock"],
               f.get("expiry_date") or None, pid), commit=True)
        flash("Product updated.", "success")
        return redirect(url_for("products"))
    return render_template("product_form.html", categories=categories, suppliers=suppliers,
                           product=product)


@app.route("/products/delete/<int:pid>")
@login_required
def delete_product(pid):
    query("DELETE FROM products WHERE id=%s", (pid,), commit=True)
    flash("Product deleted.", "success")
    return redirect(url_for("products"))


# ---------------------- CATEGORIES ----------------------
@app.route("/categories", methods=["GET", "POST"])
@login_required
def categories():
    if request.method == "POST":
        query("INSERT IGNORE INTO categories (name) VALUES (%s)", (request.form["name"],), commit=True)
        flash("Category added.", "success")
        return redirect(url_for("categories"))
    rows = query("""SELECT c.*, COUNT(p.id) AS product_count,
                     COALESCE(SUM(p.quantity),0) AS total_stock
                     FROM categories c LEFT JOIN products p ON p.category_id=c.id
                     GROUP BY c.id ORDER BY c.name""", fetch=True)
    # Products that have fallen at/below their minimum stock, grouped by category,
    # with a suggested "required" quantity to top back up to 2x the minimum.
    low_rows = query(
        """SELECT p.*, c.name AS category_name FROM products p
           JOIN categories c ON p.category_id=c.id
           WHERE p.quantity <= p.min_stock ORDER BY c.name, p.quantity ASC""",
        fetch=True)
    required_by_category = {}
    for p in low_rows:
        p["required_qty"] = max((p["min_stock"] * 2) - p["quantity"], 0)
        required_by_category.setdefault(p["category_name"], []).append(p)
    return render_template("categories.html", categories=rows,
                           required_by_category=required_by_category)


@app.route("/categories/delete/<int:cid>")
@login_required
def delete_category(cid):
    query("DELETE FROM categories WHERE id=%s", (cid,), commit=True)
    return redirect(url_for("categories"))


# ---------------------- SUPPLIERS ----------------------
@app.route("/suppliers", methods=["GET", "POST"])
@login_required
def suppliers():
    if request.method == "POST":
        f = request.form
        query("INSERT INTO suppliers (name, contact, email, address) VALUES (%s,%s,%s,%s)",
              (f["name"], f.get("contact"), f.get("email"), f.get("address")), commit=True)
        flash("Supplier added.", "success")
        return redirect(url_for("suppliers"))
    rows = query("SELECT * FROM suppliers ORDER BY name", fetch=True)
    return render_template("suppliers.html", suppliers=rows)


@app.route("/suppliers/delete/<int:sid>")
@login_required
def delete_supplier(sid):
    query("DELETE FROM suppliers WHERE id=%s", (sid,), commit=True)
    return redirect(url_for("suppliers"))


# ---------------------- SALES (stock decreases) ----------------------
@app.route("/sales")
@login_required
def sales():
    q = request.args.get("q", "").strip()
    d_from = request.args.get("from", "")
    d_to = request.args.get("to", "")
    sql = """SELECT s.*, u.username AS sold_by,
             (SELECT COALESCE(SUM(quantity),0) FROM sale_items WHERE sale_id=s.id) AS units,
             (SELECT GROUP_CONCAT(CONCAT(p.name,' x',si.quantity) SEPARATOR ', ')
                FROM sale_items si JOIN products p ON p.id=si.product_id
                WHERE si.sale_id=s.id) AS items_summary,
             (SELECT COALESCE(SUM((si.price-p.cost_price)*si.quantity),0)
                FROM sale_items si JOIN products p ON p.id=si.product_id
                WHERE si.sale_id=s.id) AS profit
             FROM sales s LEFT JOIN users u ON s.user_id=u.id
             WHERE (s.invoice_no LIKE %s OR s.customer_name LIKE %s)"""
    params = [f"%{q}%", f"%{q}%"]
    if d_from:
        sql += " AND DATE(s.created_at) >= %s"
        params.append(d_from)
    if d_to:
        sql += " AND DATE(s.created_at) <= %s"
        params.append(d_to)
    sql += " ORDER BY s.id DESC"
    rows = query(sql, params, fetch=True)
    revenue = sum(float(r["total_amount"]) for r in rows)
    units = sum(int(r["units"]) for r in rows)
    profit = sum(float(r["profit"]) for r in rows)
    summary = {"count": len(rows), "revenue": revenue, "units": units, "profit": profit,
               "avg": (revenue / len(rows)) if rows else 0}
    return render_template("sales.html", sales=rows, summary=summary,
                           q=q, d_from=d_from, d_to=d_to)


@app.route("/sales/new", methods=["GET", "POST"])
@login_required
def new_sale():
    products_list = query("""SELECT p.*, c.name AS category_name FROM products p
                              LEFT JOIN categories c ON p.category_id=c.id
                              WHERE p.quantity > 0 ORDER BY p.name""", fetch=True)
    if request.method == "POST":
        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("quantity[]")
        customer_name = request.form.get("customer_name") or "Walk-in Customer"

        if not product_ids:
            flash("Add at least one product to the sale.", "error")
            return redirect(url_for("new_sale"))

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        total = 0
        line_items = []
        # Validate stock & compute total
        for pid, qty in zip(product_ids, quantities):
            qty = int(qty)
            cur.execute("SELECT * FROM products WHERE id=%s", (pid,))
            p = cur.fetchone()
            if not p or p["quantity"] < qty:
                flash(f"Insufficient stock for {p['name'] if p else pid}.", "error")
                cur.close(); conn.close()
                return redirect(url_for("new_sale"))
            total += float(p["price"]) * qty
            line_items.append((p, qty))

        invoice_no = "INV" + datetime.now().strftime("%Y%m%d%H%M%S")
        cur.execute("INSERT INTO sales (invoice_no, user_id, customer_name, total_amount) "
                    "VALUES (%s,%s,%s,%s)", (invoice_no, session["user_id"], customer_name, total))
        sale_id = cur.lastrowid

        for p, qty in line_items:
            cur.execute("INSERT INTO sale_items (sale_id, product_id, quantity, price) "
                        "VALUES (%s,%s,%s,%s)", (sale_id, p["id"], qty, p["price"]))
            # stock automatically decreases
            cur.execute("UPDATE products SET quantity = quantity - %s WHERE id=%s", (qty, p["id"]))

        conn.commit()
        cur.close()
        conn.close()
        flash("Sale recorded. Stock updated.", "success")
        return redirect(url_for("invoice", sale_id=sale_id))

    return render_template("sale_new.html", products=products_list)


@app.route("/invoice/<int:sale_id>")
@login_required
def invoice(sale_id):
    sale = query("""SELECT s.*, u.username AS staff_name FROM sales s
                     LEFT JOIN users u ON s.user_id=u.id WHERE s.id=%s""",
                (sale_id,), fetch=True, one=True)
    items = query("""SELECT si.*, p.name FROM sale_items si
                      JOIN products p ON si.product_id=p.id WHERE si.sale_id=%s""",
                  (sale_id,), fetch=True)
    return render_template("invoice.html", sale=sale, items=items)


# ---------------------- PURCHASES (stock increases) ----------------------
@app.route("/purchases")
@login_required
def purchases():
    rows = query("""SELECT pu.*, s.name AS supplier_name FROM purchases pu
                     LEFT JOIN suppliers s ON pu.supplier_id=s.id ORDER BY pu.id DESC""",
                fetch=True)
    return render_template("purchases.html", purchases=rows)


@app.route("/purchases/new", methods=["GET", "POST"])
@login_required
def new_purchase():
    products_list = query("SELECT * FROM products ORDER BY name", fetch=True)
    suppliers_list = query("SELECT * FROM suppliers ORDER BY name", fetch=True)
    low_stock = query("""SELECT p.*, s.name AS supplier_name FROM products p
                          LEFT JOIN suppliers s ON p.supplier_id=s.id
                          WHERE p.quantity <= p.min_stock ORDER BY p.quantity ASC""", fetch=True)
    for p in low_stock:
        p["required_qty"] = max(p["min_stock"] * 2 - p["quantity"], 1)
    if request.method == "POST":
        product_ids = request.form.getlist("product_id[]")
        quantities = request.form.getlist("quantity[]")
        cost_prices = request.form.getlist("cost_price[]")
        supplier_id = request.form.get("supplier_id") or None

        if not product_ids:
            flash("Add at least one product to the purchase.", "error")
            return redirect(url_for("new_purchase"))

        conn = get_db()
        cur = conn.cursor(dictionary=True)
        total = 0
        for cp, qty in zip(cost_prices, quantities):
            total += float(cp) * int(qty)

        cur.execute("INSERT INTO purchases (supplier_id, user_id, total_amount) VALUES (%s,%s,%s)",
                    (supplier_id, session["user_id"], total))
        purchase_id = cur.lastrowid

        for pid, qty, cp in zip(product_ids, quantities, cost_prices):
            qty = int(qty)
            cur.execute("INSERT INTO purchase_items (purchase_id, product_id, quantity, cost_price) "
                        "VALUES (%s,%s,%s,%s)", (purchase_id, pid, qty, cp))
            # stock automatically increases
            cur.execute("UPDATE products SET quantity = quantity + %s, cost_price=%s WHERE id=%s",
                        (qty, cp, pid))

        conn.commit()
        cur.close()
        conn.close()
        flash("Purchase recorded. Stock updated.", "success")
        return redirect(url_for("purchases"))

    return render_template("purchase_new.html", products=products_list,
                           suppliers=suppliers_list, low_stock=low_stock)


# ---------------------- REPORTS / CHARTS ----------------------
@app.route("/reports")
@login_required
def reports():
    return render_template("reports.html", charts=chart_data())


@app.route("/api/reports/sales-last-7-days")
@login_required
def api_sales_last7():
    rows = query("""SELECT DATE(created_at) d, SUM(total_amount) total FROM sales
                     WHERE created_at >= %s GROUP BY DATE(created_at) ORDER BY d""",
                (date.today() - timedelta(days=6),), fetch=True)
    data = {str(date.today() - timedelta(days=i)): 0 for i in range(6, -1, -1)}
    for r in rows:
        data[str(r["d"])] = float(r["total"])
    return jsonify({"labels": list(data.keys()), "values": list(data.values())})


@app.route("/api/reports/stock-by-category")
@login_required
def api_stock_by_category():
    rows = query("""SELECT c.name, COALESCE(SUM(p.quantity),0) qty FROM categories c
                     LEFT JOIN products p ON p.category_id=c.id GROUP BY c.id""", fetch=True)
    return jsonify({"labels": [r["name"] for r in rows], "values": [int(r["qty"]) for r in rows]})


@app.route("/api/reports/top-products")
@login_required
def api_top_products():
    rows = query("""SELECT p.name, SUM(si.quantity) sold FROM sale_items si
                     JOIN products p ON si.product_id=p.id
                     GROUP BY p.id ORDER BY sold DESC LIMIT 5""", fetch=True)
    return jsonify({"labels": [r["name"] for r in rows], "values": [int(r["sold"]) for r in rows]})


# ---------------------- EXPORT (CSV) ----------------------
@app.route("/export/products")
@login_required
def export_products():
    rows = query("SELECT * FROM products", fetch=True)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Name", "Price", "Cost Price", "Quantity", "Min Stock", "Expiry Date"])
    for r in rows:
        writer.writerow([r["id"], r["name"], r["price"], r["cost_price"], r["quantity"],
                         r["min_stock"], r["expiry_date"]])
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=products.csv"})


@app.route("/export/sales")
@login_required
def export_sales():
    rows = query("SELECT * FROM sales", fetch=True)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Invoice No", "Customer", "Total Amount", "Date"])
    for r in rows:
        writer.writerow([r["invoice_no"], r["customer_name"], r["total_amount"], r["created_at"]])
    return Response(output.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition": "attachment;filename=sales.csv"})


if __name__ == "__main__":
    app.run(debug=True)
