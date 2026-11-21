"""SQL-based upcoming/overdue deadlines and progress."""
from datetime import date, datetime, timedelta

_VIEW = """SELECT a.id, a.student_id, u.name AS student_name,
                  a.title, c.code AS course_code, c.name AS course_name,
                  a.due_date, a.priority, a.status
           FROM assignments a
           JOIN users u ON u.id = a.student_id
           JOIN courses c ON c.id = a.course_id"""


def _as_date(value):
    """Return value as a plain date: None, date, datetime or ISO text."""
    if value is None:
        return date.today()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            raise ValueError(
                "reference_date must be an ISO 'YYYY-MM-DD' date string, "
                "got {!r}.".format(value))
    raise ValueError(
        "reference_date must be a date, a datetime, or an ISO "
        "'YYYY-MM-DD' string, got {!r}.".format(type(value).__name__))


def get_upcoming_deadlines(conn, student_id=None, days_ahead=7, reference_date=None):
    """Incomplete assignments due today through N days ahead, inclusive."""
    if not isinstance(days_ahead, int) or days_ahead < 0:
        raise ValueError("days_ahead must be a nonnegative integer.")
    today = _as_date(reference_date)
    end = today + timedelta(days=days_ahead)
    sql = _VIEW + " WHERE a.status <> 'Completed' AND a.due_date BETWEEN ? AND ?"
    args = [today.isoformat(), end.isoformat()]
    if student_id is not None:
        sql += " AND a.student_id=?"
        args.append(student_id)
    sql += " ORDER BY a.due_date, a.id"
    return conn.execute(sql, args).fetchall()


def get_overdue_assignments(conn, student_id=None, reference_date=None):
    """Incomplete assignments with due dates before today."""
    today = _as_date(reference_date)
    sql = _VIEW + " WHERE a.status <> 'Completed' AND a.due_date < ?"
    args = [today.isoformat()]
    if student_id is not None:
        sql += " AND a.student_id=?"
        args.append(student_id)
    sql += " ORDER BY a.due_date, a.id"
    return conn.execute(sql, args).fetchall()


def get_progress_summary(conn, student_id=None):
    """Return {'total', 'pending', 'in_progress', 'completed'} counts."""
    sql = """SELECT COUNT(*) AS total,
        COALESCE(SUM(CASE WHEN status='Pending' THEN 1 ELSE 0 END),0) AS pending,
        COALESCE(SUM(CASE WHEN status='In Progress' THEN 1 ELSE 0 END),0) AS in_progress,
        COALESCE(SUM(CASE WHEN status='Completed' THEN 1 ELSE 0 END),0) AS completed
        FROM assignments"""
    args = []
    if student_id is not None:
        sql += " WHERE student_id=?"
        args.append(student_id)
    return dict(conn.execute(sql, args).fetchone())
