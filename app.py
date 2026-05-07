from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# DATABASE
def connect_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# CREATE TABLE
def create_table():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employee_name TEXT,
        laptop_model TEXT,
        windows_model TEXT,
        cpu TEXT,
        gpu TEXT,
        ram TEXT,
        storage TEXT,
        installed_apps TEXT
    )
    """)

    conn.commit()

    # USER
    users = [
        ("admin", "Global@1234", "admin"),
        ("GameMaster", "Ipinfra@1234", "gamemaster")
    ]

    for user in users:
        try:
            cursor.execute(
                "INSERT INTO users (username,password,role) VALUES (?,?,?)",
                user
            )
        except:
            pass

    conn.commit()
    conn.close()

create_table()

# LOGIN
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = connect_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            session["username"] = user["username"]
            session["role"] = user["role"]

            return redirect("/dashboard")

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "username" not in session:
        return redirect("/")

    conn = connect_db()

    inventory = conn.execute(
        "SELECT * FROM inventory"
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        inventory=inventory,
        role=session["role"]
    )

# INVENTORY
@app.route("/inventory/<int:id>", methods=["GET", "POST"])
def inventory(id):

    conn = connect_db()

    if request.method == "POST":

        employee_name = request.form["employee_name"]
        laptop_model = request.form["laptop_model"]
        windows_model = request.form["windows_model"]
        cpu = request.form["cpu"]
        gpu = request.form["gpu"]
        ram = request.form["ram"]
        storage = request.form["storage"]
        installed_apps = request.form["installed_apps"]

        conn.execute("""
        UPDATE inventory
        SET
        employee_name=?,
        laptop_model=?,
        windows_model=?,
        cpu=?,
        gpu=?,
        ram=?,
        storage=?,
        installed_apps=?
        WHERE id=?
        """, (
            employee_name,
            laptop_model,
            windows_model,
            cpu,
            gpu,
            ram,
            storage,
            installed_apps,
            id
        ))

        conn.commit()

    data = conn.execute(
        "SELECT * FROM inventory WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template("inventory.html", data=data)

# CREATE INVENTORY
@app.route("/create_inventory", methods=["GET", "POST"])
def create_inventory():

    if session["role"] != "gamemaster":
        return redirect("/dashboard")

    if request.method == "POST":

        employee_name = request.form["employee_name"]

        conn = connect_db()

        conn.execute("""
        INSERT INTO inventory (
            employee_name,
            laptop_model,
            windows_model,
            cpu,
            gpu,
            ram,
            storage,
            installed_apps
        ) VALUES (?, '', '', '', '', '', '', '')
        """, (employee_name,))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("create_inventory.html")

# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

app.run(debug=True)