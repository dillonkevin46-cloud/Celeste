import sqlite3
import os

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

    # Create Tasks table (To-Do List)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL,
            assignee TEXT NOT NULL,
            priority TEXT NOT NULL,
            due_date TEXT NOT NULL,
            status TEXT NOT NULL
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
            task_name TEXT UNIQUE NOT NULL,
            mon INTEGER DEFAULT 0,
            tue INTEGER DEFAULT 0,
            wed INTEGER DEFAULT 0,
            thu INTEGER DEFAULT 0,
            fri INTEGER DEFAULT 0,
            sat INTEGER DEFAULT 0
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

    # Seed some default KPI tasks
    kpi_tasks = ["Morning Briefing", "Client Calls", "Data Entry", "End of Day Report"]
    for task in kpi_tasks:
        try:
            cursor.execute("INSERT INTO kpi_tasks (task_name) VALUES (?)", (task,))
        except sqlite3.IntegrityError:
            pass

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

# --- To-Do Tasks ---
def get_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task_name, assignee, priority, due_date, status FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def add_task(task_name, assignee, priority, due_date, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (task_name, assignee, priority, due_date, status) VALUES (?, ?, ?, ?, ?)",
        (task_name, assignee, priority, due_date, status)
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
def get_kpi_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, task_name, mon, tue, wed, thu, fri, sat FROM kpi_tasks")
    kpis = cursor.fetchall()
    conn.close()
    return kpis

def add_kpi_task(task_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO kpi_tasks (task_name) VALUES (?)", (task_name,))
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
