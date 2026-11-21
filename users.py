"""Demo role selection and ownership checks. Owner: Josia.

Roles come from the seeded ``users`` table ('student' or 'advisor').
This is a classroom demo: users are picked from a menu with no passwords,
so it is NOT a production authentication system.
"""

STUDENT = "student"
ADVISOR = "advisor"


def _clean_id(value):
    """Return value as a positive int, or None if it is not a valid ID.

    Accepts ints and digit strings (e.g. "2" typed at the menu).
    Rejects bools (True would otherwise count as 1), negatives, zero and junk.
    """
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, str) and value.strip().isdigit():
        number = int(value.strip())
        return number if number > 0 else None
    return None


def list_users(conn):
    """Return every seeded user (id, name, role) ordered by id."""
    return conn.execute("SELECT id, name, role FROM users ORDER BY id").fetchall()


def get_user(conn, user_id):
    """Return the user's row (id, name, role), or None if it doesn't exist."""
    clean_id = _clean_id(user_id)
    if clean_id is None:
        return None
    return conn.execute(
        "SELECT id, name, role FROM users WHERE id = ?", (clean_id,)
    ).fetchone()


def can_edit_assignment(conn, user_id, assignment_id):
    """Return True only if the user is a student AND owns the assignment.

    Advisors are read-only, so they always get False. A missing user,
    missing assignment or invalid ID also gives False (never an error).
    """
    clean_user = _clean_id(user_id)
    clean_assignment = _clean_id(assignment_id)
    if clean_user is None or clean_assignment is None:
        return False

    row = conn.execute(
        """SELECT 1
           FROM assignments AS a
           JOIN users AS u ON u.id = a.student_id
           WHERE a.id = ? AND u.id = ? AND u.role = ?""",
        (clean_assignment, clean_user, STUDENT),
    ).fetchone()
    return row is not None
