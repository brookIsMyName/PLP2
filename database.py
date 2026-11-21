"""SQLite lifecycle and schema."""
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "academic_planner.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

def get_connection(db_path=None):
    """Return a connection with dict-like rows and FK enforcement."""
    path = db_path if db_path is not None else DB_PATH
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database(conn):
    """Create missing tables and seed stable demo users/courses (idempotent)."""
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    conn.executemany(
        "INSERT OR IGNORE INTO users (id, name, role) VALUES (?, ?, ?)",
        [(1, "Student One", "student"), (2, "Student Two", "student"),
         (3, "Academic Advisor", "advisor")],
    )
    conn.executemany(
        "INSERT OR IGNORE INTO courses (id, code, name) VALUES (?, ?, ?)",
        [(1, "PY101", "Python Programming"),
         (2, "SQL101", "Introduction to SQL"),
         (3, "AW101", "Academic Writing")],
    )
    conn.commit()
