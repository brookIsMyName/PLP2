# PLP7 — Student Academic Planner

African Leadership University (ALU) · BSE Year 1 Trimester 2 · Peer Learning Project II

University students need one place to track coursework, due dates, priorities, and completion. The Student Academic Planner provides a terminal interface for recording assignments by course and reviewing what is due, overdue, or complete.

## Features

- Students can add, view, update the status of, and delete their own assignments. New assignments start as `Pending`. The other statuses are `In Progress` and `Completed`.
- The academic advisor can view assignments, deadline reports, and progress across all students in a read-only menu.
- Upcoming includes incomplete assignments due today through seven days from today, inclusive. Overdue includes incomplete assignments due before today.
- Progress shows total, pending, in-progress, and completed counts. Assignments persist across sessions in local SQLite.

## Technology and architecture

The project uses Python 3.10+, the standard-library `sqlite3` module, a local `academic_planner.db` file, and GitHub for collaboration. It has no external pip dependencies.

`main.py` handles prompts, role routing, and display. It passes the open connection and inputs to `users.py`, `assignments.py`, `actions.py`, and `deadlines.py`, which handle access checks, validation, and SQL queries. `database.py` opens the SQLite connection, enables foreign keys, and initializes the tables defined by `schema.sql`.

## Project files and team ownership

```text
PLP7_Academic_Planner/
├── CONTRACT.md
├── main.py
├── README.md
├── database.py
├── schema.sql
├── assignments.py
├── actions.py
├── deadlines.py
├── users.py
├── tests/
│   └── test_integration.py
├── .gitignore
└── academic_planner.db       (generated locally, ignored by Git)
```

These are assigned responsibilities. Reviewed commits record actual contributions.

| Member | Assigned files | Responsibility |
| --- | --- | --- |
| Biruk | `main.py`, `README.md` | CLI, integration, documentation, and final review |
| Genereuse | `database.py`, `schema.sql` | SQLite connection, schema, and fixed demo seeds |
| Gabriel | `assignments.py` | Assignment creation and listing |
| Valentin | `actions.py` | Status updates and assignment deletion |
| Brasen | `deadlines.py` | Upcoming and overdue queries and progress summaries |
| Josia | `users.py` | User lookup, roles, and assignment ownership checks |

`CONTRACT.md` defines the shared interfaces. `tests/test_integration.py` contains the shared integration checks.

## Database outline

| Table | Columns |
| --- | --- |
| `users` | `id`, `name`, `role` |
| `courses` | `id`, `code`, `name` |
| `assignments` | `id`, `student_id`, `course_id`, `title`, `due_date`, `priority`, `status` |

Each table uses `id` as its primary key. The assignments table references `users.id` through `student_id` and `courses.id` through `course_id`. Enter due dates as `YYYY-MM-DD` and priorities as `High`, `Medium`, or `Low`.

## Getting started

From the repository root, check your Python version and launch the planner.

```bash
python3 --version
python3 main.py
```

Startup creates `academic_planner.db` beside the app if needed and applies the schema automatically. No MySQL setup, manual schema import, or pip install is required. Keep the database file between runs to retain your assignments. Git ignores the file, so it stays local.

## Tests

From the repository root, run the integration suite. It uses in-memory SQLite databases.

```bash
python3 -m unittest discover -s tests -v
```

## Demo role IDs

| Select | Demo user | Access |
| --- | --- | --- |
| 1 | Student One | View and manage own assignments |
| 2 | Student Two | View and manage own assignments |
| 3 | Academic Advisor | View all assignments and reports |

These menu selections require no passwords. Startup seeds the same users and courses (`PY101`, `SQL101`, `AW101`) without duplicates. Create sample assignments through the student menu.

## 15-minute demonstration

Before starting, prepare one date within the next seven days and one date before today, both in `YYYY-MM-DD` format.

| Time | Walkthrough |
| --- | --- |
| 0–4 min | Select Student One. View current assignments, add a future-due Python assignment and a past-due SQL assignment, then list them and note their IDs. |
| 4–7 min | Update the future assignment to `In Progress`. Show upcoming deadlines, overdue assignments, and progress to illustrate where each record appears. |
| 7–10 min | Log out and select Student Two. Verify that Student One’s records are absent and try updating one of their IDs to show that the ownership check rejects it. |
| 10–12 min | Log out and select Academic Advisor. View all assignments and overall progress. Point out the student names and the read-only menu. |
| 12–15 min | Return as Student One and delete the overdue sample using `DELETE`. Log out, exit, and relaunch. Verify that the updated assignment is still present and the deleted one is absent. |

## Q&A source map

| Topic | Where to look |
| --- | --- |
| Role routing and menus | `main.py` → `main`, `_role_menu`, `_student_menu`, `_advisor_menu` |
| SQLite connection and startup | `database.py` → `get_connection`, `initialize_database` |
| SQL table definitions and constraints | `schema.sql` → `CREATE TABLE` statements |
| Assignment ownership | `users.py` → `can_edit_assignment` |
| Assignment SELECT and INSERT | `assignments.py` → `get_assignments`, `add_assignment` |
| Status UPDATE and assignment DELETE | `actions.py` → `update_status`, `delete_assignment` |
| Deadline SQL and progress counts | `deadlines.py` → `get_upcoming_deadlines`, `get_overdue_assignments`, `get_progress_summary` |

## Security and limitations

Role selection is a classroom demo. Anyone at the terminal can select a demo role. The app has no login, passwords, production authentication, or hosting. Use local test data only and keep `academic_planner.db` out of GitHub.

## Git workflow

Each contributor works on their own feature branch and reviews and tests changes to their assigned files before opening a pull request. Biruk reviews and merges accepted work onto `main`. Only commits merged onto `main` count toward the project rubric. Credit the starter scaffold separately from individual changes.
