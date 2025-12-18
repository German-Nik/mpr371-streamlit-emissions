import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "app.db"

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS branches (
        branch_id INTEGER PRIMARY KEY AUTOINCREMENT,
        branch_name TEXT NOT NULL UNIQUE
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin','user')),
        branch_id INTEGER,
        FOREIGN KEY(branch_id) REFERENCES branches(branch_id)
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS fuel_usage (
        usage_id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT NOT NULL,
        branch_id INTEGER NOT NULL,
        username TEXT NOT NULL,
        fuel_name TEXT NOT NULL,
        qty REAL NOT NULL,
        unit TEXT NOT NULL,
        comment TEXT,
        FOREIGN KEY(branch_id) REFERENCES branches(branch_id)
    );
    """)

    conn.commit()
    conn.close()

def seed_if_empty() -> None:
    """Seed demo branches and users if DB is empty."""
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) AS c FROM branches;")
    if cur.fetchone()["c"] == 0:
        cur.executemany("INSERT INTO branches(branch_name) VALUES (?)", [
            ("Архангельск",),
            ("Котлас",),
            ("Северодвинск",),
        ])

    cur.execute("SELECT COUNT(*) AS c FROM users;")
    if cur.fetchone()["c"] == 0:
        # Password hashes are generated in auth.py helper, but we keep deterministic seed here:
        # admin/adminpass, user1/userpass, user2/userpass
        from .auth import hash_password
        cur.execute("SELECT branch_id FROM branches WHERE branch_name='Котлас'")
        kotlas = cur.fetchone()["branch_id"]
        cur.execute("SELECT branch_id FROM branches WHERE branch_name='Архангельск'")
        ark = cur.fetchone()["branch_id"]

        users = [
            ("admin", hash_password("adminpass"), "admin", None),
            ("user1", hash_password("userpass"), "user", kotlas),
            ("user2", hash_password("userpass"), "user", ark),
        ]
        cur.executemany(
            "INSERT INTO users(username, password_hash, role, branch_id) VALUES (?,?,?,?)",
            users
        )

    conn.commit()
    conn.close()
