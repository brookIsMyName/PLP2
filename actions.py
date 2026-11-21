"""Update the status of an assignment and delete assignments. Owner: Valentin.

Both actions are only allowed for the student who owns the assignment.
Advisors are read-only in this demo, so they can neither update nor delete.
Every problem is reported with a ValueError carrying a message that the menu
can print as it is, so the program never crashes on bad input.
"""

STATUSES = ("Pending", "In Progress", "Completed")

_ASSIGNMENT_VIEW = """SELECT a.id, a.student_id, u.name AS student_name,
                             a.title, c.code AS course_code, c.name AS course_name,
                             a.due_date, a.priority, a.status
                      FROM assignments a
                      JOIN users u ON u.id = a.student_id
                      JOIN courses c ON c.id = a.course_id
                      WHERE a.id = ?"""


def _clean_id(value, what):
    """Return value as a positive int or raise a ValueError naming `what`.

    Accepts ints and digit strings typed at the menu. Rejects bools,
    zero, negatives and anything that is not a whole number.
    """
    if isinstance(value, bool):
        raise ValueError("{} must be a positive numeric ID.".format(what))
    if isinstance(value, int) and value > 0:
        return value
    if isinstance(value, str) and value.strip().isdigit() and int(value) > 0:
        return int(value.strip())
    raise ValueError("{} must be a positive numeric ID.".format(what))


def normalize_status(value):
    """Return the canonical status for value, or raise a ValueError.

    The menu may collect the status as text ("completed", "IN PROGRESS")
    or as the option number (1, 2, 3) shown next to each status.
    """
    if isinstance(value, bool):
        raise ValueError("Status must be one of: " + ", ".join(STATUSES) + ".")
    if isinstance(value, int) and 1 <= value <= len(STATUSES):
        return STATUSES[value - 1]
    if isinstance(value, str):
        text = value.strip()
        if text.isdigit() and 1 <= int(text) <= len(STATUSES):
            return STATUSES[int(text) - 1]
        for status in STATUSES:
            if text.lower() == status.lower():
                return status
    raise ValueError("Status must be one of: " + ", ".join(STATUSES) + ".")


def get_assignment(conn, assignment_id):
    """Return the assignment row (same columns as the list view) or None."""
    try:
        clean_id = _clean_id(assignment_id, "Assignment ID")
    except ValueError:
        return None
    return conn.execute(_ASSIGNMENT_VIEW, (clean_id,)).fetchone()


def _owned_assignment(conn, user_id, assignment_id):
    """Return the assignment if `user_id` is a student who owns it.

    Raises a ValueError explaining the problem otherwise: bad IDs, unknown
    user, unknown assignment, advisor account or another student's work.
    """
    clean_user = _clean_id(user_id, "User ID")
    clean_assignment = _clean_id(assignment_id, "Assignment ID")

    user = conn.execute(
        "SELECT id, role FROM users WHERE id = ?", (clean_user,)
    ).fetchone()
    if user is None:
        raise ValueError("Unknown user. Choose a listed ID.")
    if user["role"] != "student":
        raise ValueError("Advisors can only view assignments, not change them.")

    assignment = conn.execute(_ASSIGNMENT_VIEW, (clean_assignment,)).fetchone()
    if assignment is None:
        raise ValueError("No assignment found with ID {}.".format(clean_assignment))
    if assignment["student_id"] != clean_user:
        raise ValueError("You can only change your own assignments.")
    return assignment


def update_status(conn, user_id, assignment_id, new_status):
    """Set the status of one of the student's assignments; return the row.

    `new_status` can be the text or the option number of a value in STATUSES.
    The returned row shows the assignment after the update.
    """
    status = normalize_status(new_status)
    assignment = _owned_assignment(conn, user_id, assignment_id)
    if assignment["status"] == status:
        raise ValueError(
            "Assignment {} is already marked as {}.".format(assignment["id"], status))
    conn.execute(
        "UPDATE assignments SET status = ? WHERE id = ?",
        (status, assignment["id"]),
    )
    conn.commit()
    return conn.execute(_ASSIGNMENT_VIEW, (assignment["id"],)).fetchone()


def delete_assignment(conn, user_id, assignment_id):
    """Delete one of the student's assignments; return the deleted row.

    The returned row lets the menu confirm what was removed
    ("Deleted: Python Lab (PY101)").
    """
    assignment = _owned_assignment(conn, user_id, assignment_id)
    conn.execute("DELETE FROM assignments WHERE id = ?", (assignment["id"],))
    conn.commit()
    return assignment
