import sqlite3
from contextlib import closing

from database import get_connection, initialize_database
from users import list_users, get_user
from assignments import add_assignment, list_courses, get_assignments
from actions import update_status, delete_assignment
from deadlines import (
    get_upcoming_deadlines, get_overdue_assignments, get_progress_summary,
)

def _ask_number(prompt):
    raw = input(prompt).strip()
    if not raw.isdigit() or int(raw) <= 0:
        raise ValueError("Enter a positive numeric ID.")
    return int(raw)



def _role_menu(conn):
    while True:
        print("\n===== STUDENT ACADEMIC PLANNER =====")
        print("Demo role selection. No passwords. Classroom/test data only.")
        for user in list_users(conn):
            print(f"  {user['id']} {user['name']} ({user['role']})")
        print("  0 Exit")
        raw = input("Select role: ").strip()
        if raw == "0":
            print("Goodbye!")
            return
        try:
            user_id = _positive_id(raw)
        except ValueError as exc:
            print(exc)
            continue
        user = get_user(conn, user_id)
        if user is None:
            print("Unknown user. Choose a listed ID.")
        elif user["role"] == "student":
            _student_menu(conn, user)
        elif user["role"] == "advisor":
            _advisor_menu(conn)
        else:
            print("Unsupported user role. Choose another listed ID.")


def main() -> None:
    try:
        with closing(get_connection()) as conn:
            initialize_database(conn)
            _role_menu(conn)
    except (KeyboardInterrupt, EOFError):
        print("\nExiting planner.")
    except (sqlite3.Error, OSError) as exc:
        print(f"Could not continue with the planner database: {exc}")


if __name__ == '__main__':
    main()
