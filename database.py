# database.py - this is where we handle the database

from pathlib import Path
import sqlite3

# find where this file is, so the db file is always next to it
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "academic_planner.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"

def get_connection(db_path=None):
    # if we give a path use it, if not use the normal one
    path = db_path if db_path is not None else DB_PATH
    conn = sqlite3.connect(str(path))
    # so we can do row["name"] instead of row[1]
    conn.row_factory = sqlite3.Row
    # make sure foreign keys actually work
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize_database(conn):
    # run our schema.sql file to create tables if they don't exist yet
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    # add some demo users, ignore if they are already there
    conn.executemany(
        "INSERT OR IGNORE INTO users (id, name, role) VALUES (?, ?, ?)",
        [(1, "Student One", "student"), (2, "Student Two", "student"),
         (3, "Academic Advisor", "advisor")],
    )
    # same for courses
    conn.executemany(
        "INSERT OR IGNORE INTO courses (id, code, name) VALUES (?, ?, ?)",
        [(1, "PY101", "Python Programming"),
         (2, "SQL101", "Introduction to SQL"),
         (3, "AW101", "Academic Writing")],
    )
    # save it
    conn.commit()
