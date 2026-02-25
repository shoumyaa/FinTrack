"""
Database layer — all SQLite operations for FinTrack.
Single source of truth for every table.
"""
import sqlite3
import pandas as pd
from datetime import date

DB = "finance.db"

def conn():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    with conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            date        TEXT    NOT NULL,
            amount      REAL    NOT NULL,
            category    TEXT    NOT NULL,
            type        TEXT    NOT NULL,
            description TEXT,
            recurring   TEXT    DEFAULT 'None'
        );

        CREATE TABLE IF NOT EXISTS budgets (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            month    TEXT NOT NULL,
            category TEXT NOT NULL,
            budget   REAL NOT NULL,
            UNIQUE(month, category)
        );

        CREATE TABLE IF NOT EXISTS goals (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL,
            target      REAL NOT NULL,
            saved       REAL NOT NULL DEFAULT 0,
            deadline    TEXT,
            icon        TEXT DEFAULT '🎯',
            created     TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS split_groups (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            created TEXT NOT NULL
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

# ── Transactions ───────────────────────────────────────────────────────────────
def add_tx(d, amt, cat, typ, desc="", recurring="None"):
    with conn() as c:
        c.execute("INSERT INTO transactions(date,amount,category,type,description,recurring) VALUES(?,?,?,?,?,?)",
                  (str(d), amt, cat, typ, desc, recurring)); c.commit()

def del_tx(tid):
    with conn() as c:
        c.execute("DELETE FROM transactions WHERE id=?", (tid,)); c.commit()

def load_tx():
    with conn() as c:
        df = pd.read_sql("SELECT * FROM transactions ORDER BY date DESC", c)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
    return df

# ── Budgets ────────────────────────────────────────────────────────────────────
def upsert_budget(month, cat, val):
    with conn() as c:
        c.execute("INSERT INTO budgets(month,category,budget) VALUES(?,?,?) "
                  "ON CONFLICT(month,category) DO UPDATE SET budget=excluded.budget",
                  (month, cat, val)); c.commit()

def load_budgets(month):
    with conn() as c:
        return pd.read_sql("SELECT category,budget FROM budgets WHERE month=?", c, params=(month,))

# ── Goals ──────────────────────────────────────────────────────────────────────
def add_goal(name, target, deadline, icon):
    with conn() as c:
        c.execute("INSERT INTO goals(name,target,saved,deadline,icon,created) VALUES(?,?,0,?,?,?)",
                  (name, target, str(deadline), icon, str(date.today()))); c.commit()

def update_goal_saved(gid, amount):
    with conn() as c:
        c.execute("UPDATE goals SET saved=saved+? WHERE id=?", (amount, gid)); c.commit()

def delete_goal(gid):
    with conn() as c:
        c.execute("DELETE FROM goals WHERE id=?", (gid,)); c.commit()

def load_goals():
    with conn() as c:
        return pd.read_sql("SELECT * FROM goals", c)

# ── Split Groups ───────────────────────────────────────────────────────────────
def create_group(name):
    with conn() as c:
        c.execute("INSERT INTO split_groups(name,created) VALUES(?,?)", (name, str(date.today())))
        c.commit()
        return c.execute("SELECT last_insert_rowid()").fetchone()[0]

def load_groups():
    with conn() as c:
        return pd.read_sql("SELECT * FROM split_groups ORDER BY created DESC", c)

def add_member(group_id, name):
    with conn() as c:
        c.execute("INSERT INTO split_members(group_id,name) VALUES(?,?)", (group_id, name)); c.commit()

def load_members(group_id):
    with conn() as c:
        return pd.read_sql("SELECT * FROM split_members WHERE group_id=?", c, params=(group_id,))

def add_split_expense(group_id, desc, amount, paid_by, exp_date, shares: dict):
    with conn() as c:
        c.execute("INSERT INTO split_expenses(group_id,description,amount,paid_by,date,settled) VALUES(?,?,?,?,?,0)",
                  (group_id, desc, amount, paid_by, str(exp_date)))
        eid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
        for member, share in shares.items():
            c.execute("INSERT INTO split_shares(expense_id,member,share) VALUES(?,?,?)", (eid, member, share))
        c.commit()

def load_split_expenses(group_id):
    with conn() as c:
        return pd.read_sql("SELECT * FROM split_expenses WHERE group_id=? ORDER BY date DESC", c, params=(group_id,))

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
