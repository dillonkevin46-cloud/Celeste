import sqlite3
import datetime
from dateutil.relativedelta import relativedelta

DB_PATH = "tradecore.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Create Months table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS months (
            month_year TEXT PRIMARY KEY,
            is_archived INTEGER DEFAULT 0
        )
    """)

    # Create Tasks table (To-Do List)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month_year TEXT NOT NULL,
            task_name TEXT NOT NULL,
            assignee TEXT NOT NULL,
            priority TEXT NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (month_year) REFERENCES months(month_year)
        )
    """)

    # Create Assignees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assignees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    # Create KPI daily tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS kpi_tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            month_year TEXT NOT NULL,
            task_name TEXT NOT NULL,
            mon INTEGER DEFAULT 0,
            tue INTEGER DEFAULT 0,
            wed INTEGER DEFAULT 0,
            thu INTEGER DEFAULT 0,
            fri INTEGER DEFAULT 0,
            sat INTEGER DEFAULT 0,
            FOREIGN KEY (month_year) REFERENCES months(month_year)
        )
    """)

    # Seed Superuser
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", ("Tradecore", "Tradecore"))
    except sqlite3.IntegrityError:
        pass

    # Seed Assignees
    assignees = ["Rogan", "Vitto", "Jared", "Lee"]
    for assignee in assignees:
        try:
            cursor.execute("INSERT INTO assignees (name) VALUES (?)", (assignee,))
        except sqlite3.IntegrityError:
            pass

    # Ensure current month exists
    current_my = datetime.datetime.now().strftime("%B %Y")
    cursor.execute("INSERT OR IGNORE INTO months (month_year) VALUES (?)", (current_my,))

    # Check if we need to seed initial KPIs for current month
    cursor.execute("SELECT COUNT(*) FROM kpi_tasks WHERE month_year = ?", (current_my,))
    if cursor.fetchone()[0] == 0:
        kpi_tasks = ["Morning Briefing", "Client Calls", "Data Entry", "End of Day Report"]
        for task in kpi_tasks:
            cursor.execute("INSERT INTO kpi_tasks (month_year, task_name) VALUES (?, ?)", (current_my, task))

    conn.commit()
    conn.close()

# --- Auth / Users ---
def authenticate(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()
    return user is not None

def get_users():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def add_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def update_user(user_id, username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE users SET username = ?, password = ? WHERE id = ?", (username, password, user_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def delete_user(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()

# --- Assignees ---
def get_assignees():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM assignees")
    assignees = cursor.fetchall()
    conn.close()
    return assignees

def get_assignee_names():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM assignees")
    assignees = [row[0] for row in cursor.fetchall()]
    conn.close()
    return assignees

def add_assignee(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO assignees (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def update_assignee(assignee_id, name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE assignees SET name = ? WHERE id = ?", (name, assignee_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def delete_assignee(assignee_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assignees WHERE id = ?", (assignee_id,))
    conn.commit()
    conn.close()

# --- Months & Archiving ---
def get_all_months():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Ensure current month is always in the list
    current_my = datetime.datetime.now().strftime("%B %Y")
    cursor.execute("INSERT OR IGNORE INTO months (month_year) VALUES (?)", (current_my,))
    conn.commit()

    cursor.execute("SELECT month_year FROM months ORDER BY month_year DESC")
    months = [row[0] for row in cursor.fetchall()]
    conn.close()
    return months

def is_month_archived(month_year):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT is_archived FROM months WHERE month_year = ?", (month_year,))
    row = cursor.fetchone()
    conn.close()
    return bool(row[0]) if row else False

def archive_month(current_month_year):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Archive current month
    cursor.execute("UPDATE months SET is_archived = 1 WHERE month_year = ?", (current_month_year,))

    # 2. Generate next month string
    # Parse "March 2026"
    date_obj = datetime.datetime.strptime(current_month_year, "%B %Y")
    next_month_obj = date_obj + relativedelta(months=1)
    next_month_year = next_month_obj.strftime("%B %Y")

    # 3. Create next month record
    cursor.execute("INSERT OR IGNORE INTO months (month_year, is_archived) VALUES (?, 0)", (next_month_year,))

    # 4. Copy KPI task names (blank slate)
    cursor.execute("SELECT DISTINCT task_name FROM kpi_tasks WHERE month_year = ?", (current_month_year,))
    distinct_tasks = cursor.fetchall()

    # Check if already seeded to prevent duplication
    cursor.execute("SELECT COUNT(*) FROM kpi_tasks WHERE month_year = ?", (next_month_year,))
    if cursor.fetchone()[0] == 0:
        for t in distinct_tasks:
            cursor.execute("INSERT INTO kpi_tasks (month_year, task_name) VALUES (?, ?)", (next_month_year, t[0]))

    conn.commit()
    conn.close()

# --- To-Do Tasks ---
def get_tasks(month_year):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task_name, assignee, priority, due_date, status FROM tasks WHERE month_year = ?", (month_year,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def add_task(month_year, task_name, assignee, priority, due_date, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (month_year, task_name, assignee, priority, due_date, status) VALUES (?, ?, ?, ?, ?, ?)",
        (month_year, task_name, assignee, priority, due_date, status)
    )
    conn.commit()
    conn.close()

def update_task_status(task_id, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (status, task_id))
    conn.commit()
    conn.close()

def update_task(task_id, task_name, assignee, priority, due_date, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET task_name = ?, assignee = ?, priority = ?, due_date = ?, status = ? WHERE id = ?",
        (task_name, assignee, priority, due_date, status, task_id)
    )
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

# --- KPI Tasks ---
def get_kpi_tasks(month_year):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task_name, mon, tue, wed, thu, fri, sat FROM kpi_tasks WHERE month_year = ?", (month_year,))
    kpis = cursor.fetchall()
    conn.close()
    return kpis

def add_kpi_task(month_year, task_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kpi_tasks (month_year, task_name) VALUES (?, ?)", (month_year, task_name))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def update_kpi_task_name(task_id, task_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE kpi_tasks SET task_name = ? WHERE id = ?", (task_name, task_id))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()

def update_kpi_task_day(task_id, day_col, value):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    query = f"UPDATE kpi_tasks SET {day_col} = ? WHERE id = ?"
    cursor.execute(query, (value, task_id))
    conn.commit()
    conn.close()

def delete_kpi_task(task_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM kpi_tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
