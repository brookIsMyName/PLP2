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
