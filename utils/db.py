"""
Database layer — all SQLite operations for FinTrack.
Includes user authentication and per-user data isolation.
"""
import sqlite3
import pandas as pd
import hashlib
import os
from datetime import date

DB = "finance.db"

def conn():
    return sqlite3.connect(DB, check_same_thread=False)

def hash_password(password: str) -> str:
    """Hash password using SHA-256 with a salt."""
    salt = "fintrack_salt_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT    NOT NULL UNIQUE,
            password   TEXT    NOT NULL,
            created    TEXT    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            date        TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            type        TEXT    NOT NULL,
            description TEXT,
            recurring   TEXT    DEFAULT 'None',
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            month    TEXT NOT NULL,
            category TEXT NOT NULL,
            budget   REAL NOT NULL,
            UNIQUE(user_id, month, category),
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS goals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            name        TEXT NOT NULL,
            target      REAL NOT NULL,
            saved       REAL NOT NULL DEFAULT 0,
            deadline    TEXT,
            icon        TEXT DEFAULT '🎯',
            created     TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS split_groups (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name    TEXT NOT NULL,
            created TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS split_members (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id INTEGER NOT NULL,
            name     TEXT    NOT NULL,
            FOREIGN KEY(group_id) REFERENCES split_groups(id)
        );

        CREATE TABLE IF NOT EXISTS split_expenses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            group_id    INTEGER NOT NULL,
            description TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            paid_by     TEXT    NOT NULL,
            date        TEXT    NOT NULL,
            settled     INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(group_id) REFERENCES split_groups(id)
        );

        CREATE TABLE IF NOT EXISTS split_shares (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            expense_id INTEGER NOT NULL,
            member     TEXT    NOT NULL,
            share      REAL    NOT NULL,
            FOREIGN KEY(expense_id) REFERENCES split_expenses(id)
        );
        """)
        c.commit()

# ── Auth ───────────────────────────────────────────────────────────────────────
def create_user(username: str, password: str) -> tuple[bool, str]:
    """Create a new user. Returns (success, message)."""
    try:
        with conn() as c:
            c.execute(
                "INSERT INTO users(username, password, created) VALUES(?,?,?)",
                (username.strip().lower(), hash_password(password), str(date.today()))
            )
            c.commit()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists. Please choose another."

def login_user(username: str, password: str):
    """Verify credentials. Returns user row dict or None."""
    with conn() as c:
        row = c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username.strip().lower(), hash_password(password))
        ).fetchone()
    if row:
        return {"id": row[0], "username": row[1]}
    return None

def get_user(user_id: int):
    """Get user by ID."""
    with conn() as c:
        row = c.execute("SELECT id, username FROM users WHERE id=?", (user_id,)).fetchone()
    return {"id": row[0], "username": row[1]} if row else None

# ── Transactions ───────────────────────────────────────────────────────────────
def add_tx(user_id, d, amt, cat, typ, desc="", recurring="None"):
    with conn() as c:
        c.execute(
            "INSERT INTO transactions(user_id,date,amount,category,type,description,recurring) VALUES(?,?,?,?,?,?,?)",
            (user_id, str(d), amt, cat, typ, desc, recurring)
        ); c.commit()

def del_tx(tid):
    with conn() as c:
        c.execute("DELETE FROM transactions WHERE id=?", (tid,)); c.commit()

def load_tx(user_id):
    with conn() as c:
        df = pd.read_sql(
            "SELECT * FROM transactions WHERE user_id=? ORDER BY date DESC", c,
            params=(user_id,)
        )
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df

# ── Budgets ────────────────────────────────────────────────────────────────────
def upsert_budget(user_id, month, cat, val):
    with conn() as c:
        c.execute(
            "INSERT INTO budgets(user_id,month,category,budget) VALUES(?,?,?,?) "
            "ON CONFLICT(user_id,month,category) DO UPDATE SET budget=excluded.budget",
            (user_id, month, cat, val)
        ); c.commit()

def load_budgets(user_id, month):
    with conn() as c:
        return pd.read_sql(
            "SELECT category,budget FROM budgets WHERE user_id=? AND month=?",
            c, params=(user_id, month)
        )

# ── Goals ──────────────────────────────────────────────────────────────────────
def add_goal(user_id, name, target, deadline, icon):
    with conn() as c:
        c.execute(
            "INSERT INTO goals(user_id,name,target,saved,deadline,icon,created) VALUES(?,?,0,?,?,?,?)",
            (user_id, name, target, str(deadline), icon, str(date.today()))
        ); c.commit()

def update_goal_saved(gid, amount):
    with conn() as c:
        c.execute("UPDATE goals SET saved=saved+? WHERE id=?", (amount, gid)); c.commit()

def delete_goal(gid):
    with conn() as c:
        c.execute("DELETE FROM goals WHERE id=?", (gid,)); c.commit()

def load_goals(user_id):
    with conn() as c:
        return pd.read_sql("SELECT * FROM goals WHERE user_id=?", c, params=(user_id,))

# ── Split Groups ───────────────────────────────────────────────────────────────
def create_group(user_id, name):
    with conn() as c:
        c.execute(
            "INSERT INTO split_groups(user_id,name,created) VALUES(?,?,?)",
            (user_id, name, str(date.today()))
        )
        c.commit()
        return c.execute("SELECT last_insert_rowid()").fetchone()[0]

def load_groups(user_id):
    with conn() as c:
        return pd.read_sql(
            "SELECT * FROM split_groups WHERE user_id=? ORDER BY created DESC",
            c, params=(user_id,)
        )

def add_member(group_id, name):
    with conn() as c:
        c.execute("INSERT INTO split_members(group_id,name) VALUES(?,?)", (group_id, name)); c.commit()

def load_members(group_id):
    with conn() as c:
        return pd.read_sql("SELECT * FROM split_members WHERE group_id=?", c, params=(group_id,))

def add_split_expense(group_id, desc, amount, paid_by, exp_date, shares: dict):
    with conn() as c:
        c.execute(
            "INSERT INTO split_expenses(group_id,description,amount,paid_by,date,settled) VALUES(?,?,?,?,?,0)",
            (group_id, desc, amount, paid_by, str(exp_date))
        )
        eid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
        for member, share in shares.items():
            c.execute("INSERT INTO split_shares(expense_id,member,share) VALUES(?,?,?)", (eid, member, share))
        c.commit()

def load_split_expenses(group_id):
    with conn() as c:
        return pd.read_sql(
            "SELECT * FROM split_expenses WHERE group_id=? ORDER BY date DESC",
            c, params=(group_id,)
        )

def load_shares(expense_id):
    with conn() as c:
        return pd.read_sql("SELECT * FROM split_shares WHERE expense_id=?", c, params=(expense_id,))

def settle_expense(eid):
    with conn() as c:
        c.execute("UPDATE split_expenses SET settled=1 WHERE id=?", (eid,)); c.commit()

def delete_group(gid):
    with conn() as c:
        c.executescript(f"""
            DELETE FROM split_shares WHERE expense_id IN
                (SELECT id FROM split_expenses WHERE group_id={gid});
            DELETE FROM split_expenses WHERE group_id={gid};
            DELETE FROM split_members WHERE group_id={gid};
            DELETE FROM split_groups WHERE id={gid};
        """); c.commit()
