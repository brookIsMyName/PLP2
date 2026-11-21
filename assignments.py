from datetime import date
import re

PRIORITIES = {"High", "Medium", "Low"}

def list_courses(conn):
    return conn.execute("SELECT id, code, name FROM courses ORDER BY id").fetchall()

def _validate_fields(title, due_date, priority):
    if not title or not title.strip():
        raise ValueError("Assignment title cannot be blank.")
    if not isinstance(due_date, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", due_date):
        raise ValueError("Due date must be a valid YYYY-MM-DD date.")
    try:
        date.fromisoformat(due_date)
    except (ValueError, TypeError):
        raise ValueError("Due date must be a valid YYYY-MM-DD date.") from None
    if priority not in PRIORITIES:
        raise ValueError("Priority must be High, Medium, or Low.")

def add_assignment(conn, student_id, course_id, title, due_date, priority):
    """Create a pending assignment; return its integer id."""
    _validate_fields(title, due_date, priority)
    u = conn.execute("SELECT role FROM users WHERE id=?", (student_id,)).fetchone()
    if u is None or u["role"] != "student":
        raise ValueError("Only a valid student may create assignments.")
    if conn.execute("SELECT 1 FROM courses WHERE id=?", (course_id,)).fetchone() is None:
        raise ValueError("Please choose an existing course ID.")
    cursor = conn.execute(
        """INSERT INTO assignments (student_id, course_id, title, due_date, priority)
        VALUES (?, ?, ?, ?, ?)""",
        (student_id, course_id, title.strip(), due_date, priority),
    )
    conn.commit()
    return cursor.lastrowid
