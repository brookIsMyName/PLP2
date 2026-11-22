import sqlite3
from contextlib import closing

from database import get_connection, initialize_database
from users import list_users, get_user
from assignments import add_assignment, list_courses, get_assignments
from actions import update_status, delete_assignment
from deadlines import (
    get_upcoming_deadlines, get_overdue_assignments, get_progress_summary,
)

def _display(rows):
    if not rows:
        print("No matching assignments found.")
        return
    print("\n ID | Student          | Course  | Due date   | Priority | Status      | Title")
    print("-" * 90)
    for r in rows:
        print(f"{r['id']:3} | {r['student_name'][:16]:16} | "
              f"{r['course_code'][:7]:7} | {r['due_date']:10} | "
              f"{r['priority']:8} | {r['status']:11} | {r['title'][:35]}")


def _ask_number(prompt):
    return _positive_id(input(prompt).strip())


def _positive_id(raw):
    if not raw.isdecimal():
        raise ValueError("Enter a positive numeric ID.")
    number = int(raw)
    if not 0 < number <= 2**63 - 1:
        raise ValueError("Enter a positive numeric ID.")
    return number

def _show_summary(conn, student_id):
    stats = get_progress_summary(conn, student_id)
    print("\nProgress:", ", ".join(f"{key}: {value}" for key, value in stats.items()))

def _student_menu(conn, user):
    student_id = user['id']
    while True:
        print("\n--- STUDENT MENU ---")
        print("1 Add assignment | 2 View mine | 3 Update status | 4 Upcoming (7 days)")
        print("5 Delete assignment | 6 Overdue | 7 Progress | 0 Log out")
        choice = input("Choose: ").strip()
        try:
            if choice == "0":
                return
            elif choice == "1":
                print("Courses:")
                for c in list_courses(conn):
                    print(f"  {c['id']}. {c['code']} - {c['name']}")
                course_id = _ask_number("Course ID: ")
                title = input("Assignment title: ").strip()
                due_date = input("Due date YYYY-MM-DD: ").strip()
                priority = input("Priority (High/Medium/Low): ").strip()
                aid = add_assignment(conn, student_id, course_id, title, due_date, priority)
                print(f"Saved assignment #{aid} to SQLite.")
            elif choice == "2":
                _display(get_assignments(conn, student_id))
            elif choice == "3":
                aid = _ask_number("Assignment ID: ")
                status = input("New status (Pending/In Progress/Completed): ").strip()
                update_status(conn, student_id, aid, status)
                print("Updated.")
            elif choice == "4":
                _display(get_upcoming_deadlines(conn, student_id))
            elif choice == "5":
                aid = _ask_number("Assignment ID: ")
                if input("Type DELETE to confirm: ").strip() == "DELETE":
                    delete_assignment(conn, student_id, aid)
                    print("Deleted.")
                else:
                    print("Deletion cancelled.")
            elif choice == "6":
                _display(get_overdue_assignments(conn, student_id))
            elif choice == "7":
                _show_summary(conn, student_id)
            else:
                print("Invalid menu choice. Please try again.")
        except (ValueError, sqlite3.Error) as exc:
            print(f"Could not complete operation: {exc}")


def _advisor_menu(conn):
    while True:
        print("\n--- ACADEMIC ADVISOR (READ ONLY) ---")
        print("1 All assignments | 2 Upcoming (7 days) | 3 Overdue | 4 Progress | 0 Log out")
        choice = input("Choose: ").strip()
        try:
            if choice == "0":
                return
            elif choice == "1":
                _display(get_assignments(conn))
            elif choice == "2":
                _display(get_upcoming_deadlines(conn))
            elif choice == "3":
                _display(get_overdue_assignments(conn))
            elif choice == "4":
                _show_summary(conn, None)
            else:
                print("Invalid menu choice. Please try again.")
        except (ValueError, sqlite3.Error) as exc:
            print(f"Could not complete operation: {exc}")

def _role_menu(conn):
    while True:
        print("\n===== TECHO: THE STUDENT ACADEMIC PLANNER =====")
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
