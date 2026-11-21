"""Status update and deletion tests for actions.py (owner: Valentin).

Run: python3 -m unittest discover -s tests -v
"""
import unittest
from datetime import date, timedelta

from database import get_connection, initialize_database
from assignments import add_assignment, get_assignments
from actions import (
    STATUSES, delete_assignment, get_assignment, normalize_status,
    update_status,
)


class ActionsTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(":memory:")
        initialize_database(self.conn)
        due = (date.today() + timedelta(days=5)).isoformat()
        # Student One (id 1) owns `self.mine`, Student Two (id 2) owns `self.theirs`.
        self.mine = add_assignment(self.conn, 1, 1, "Python Lab", due, "High")
        self.theirs = add_assignment(self.conn, 2, 2, "SQL Quiz", due, "Low")

    def tearDown(self):
        self.conn.close()


class NormalizeStatusTests(ActionsTestCase):
    def test_exact_and_case_insensitive_text(self):
        self.assertEqual(normalize_status("Completed"), "Completed")
        self.assertEqual(normalize_status("in progress"), "In Progress")
        self.assertEqual(normalize_status("  PENDING "), "Pending")

    def test_option_numbers(self):
        self.assertEqual(normalize_status(1), "Pending")
        self.assertEqual(normalize_status("2"), "In Progress")
        self.assertEqual(normalize_status(3), "Completed")

    def test_rejects_unknown_values(self):
        for bad in ("Done", "", 0, 4, None, True, 2.0, ["Completed"]):
            with self.assertRaises(ValueError, msg=bad):
                normalize_status(bad)


class UpdateStatusTests(ActionsTestCase):
    def test_owner_updates_status(self):
        row = update_status(self.conn, 1, self.mine, "In Progress")
        self.assertEqual(row["status"], "In Progress")
        self.assertEqual(get_assignment(self.conn, self.mine)["status"], "In Progress")

    def test_update_is_persisted_in_list_view(self):
        update_status(self.conn, 1, self.mine, "Completed")
        rows = get_assignments(self.conn, 1)
        self.assertEqual([r["status"] for r in rows], ["Completed"])

    def test_accepts_menu_style_inputs(self):
        row = update_status(self.conn, "1", str(self.mine), "3")
        self.assertEqual(row["status"], "Completed")

    def test_every_status_is_reachable(self):
        for status in ("In Progress", "Completed", "Pending"):
            self.assertEqual(update_status(self.conn, 1, self.mine, status)["status"], status)

    def test_same_status_twice_is_reported(self):
        with self.assertRaises(ValueError) as error:
            update_status(self.conn, 1, self.mine, "Pending")
        self.assertIn("already", str(error.exception))

    def test_invalid_status_changes_nothing(self):
        with self.assertRaises(ValueError):
            update_status(self.conn, 1, self.mine, "Done")
        self.assertEqual(get_assignment(self.conn, self.mine)["status"], "Pending")

    def test_other_student_cannot_update(self):
        with self.assertRaises(ValueError) as error:
            update_status(self.conn, 2, self.mine, "Completed")
        self.assertIn("own", str(error.exception))
        self.assertEqual(get_assignment(self.conn, self.mine)["status"], "Pending")

    def test_advisor_cannot_update(self):
        with self.assertRaises(ValueError) as error:
            update_status(self.conn, 3, self.mine, "Completed")
        self.assertIn("Advisors", str(error.exception))

    def test_unknown_user_or_assignment(self):
        with self.assertRaises(ValueError):
            update_status(self.conn, 99, self.mine, "Completed")
        with self.assertRaises(ValueError) as error:
            update_status(self.conn, 1, 9999, "Completed")
        self.assertIn("No assignment", str(error.exception))

    def test_bad_ids_are_rejected(self):
        for bad in (0, -1, True, None, "abc", 1.5):
            with self.assertRaises(ValueError, msg=bad):
                update_status(self.conn, bad, self.mine, "Completed")
            with self.assertRaises(ValueError, msg=bad):
                update_status(self.conn, 1, bad, "Completed")


class DeleteAssignmentTests(ActionsTestCase):
    def test_owner_deletes_assignment(self):
        deleted = delete_assignment(self.conn, 1, self.mine)
        self.assertEqual(deleted["title"], "Python Lab")
        self.assertIsNone(get_assignment(self.conn, self.mine))
        self.assertEqual(get_assignments(self.conn, 1), [])

    def test_delete_leaves_other_students_data(self):
        delete_assignment(self.conn, 1, self.mine)
        self.assertEqual(get_assignment(self.conn, self.theirs)["title"], "SQL Quiz")

    def test_accepts_menu_style_ids(self):
        deleted = delete_assignment(self.conn, "2", str(self.theirs))
        self.assertEqual(deleted["id"], self.theirs)

    def test_deleting_twice_fails_cleanly(self):
        delete_assignment(self.conn, 1, self.mine)
        with self.assertRaises(ValueError) as error:
            delete_assignment(self.conn, 1, self.mine)
        self.assertIn("No assignment", str(error.exception))

    def test_other_student_cannot_delete(self):
        with self.assertRaises(ValueError):
            delete_assignment(self.conn, 2, self.mine)
        self.assertIsNotNone(get_assignment(self.conn, self.mine))

    def test_advisor_cannot_delete(self):
        with self.assertRaises(ValueError):
            delete_assignment(self.conn, 3, self.mine)
        self.assertIsNotNone(get_assignment(self.conn, self.mine))

    def test_bad_ids_are_rejected(self):
        for bad in (0, -1, True, None, "abc", 1.5):
            with self.assertRaises(ValueError, msg=bad):
                delete_assignment(self.conn, 1, bad)


class GetAssignmentTests(ActionsTestCase):
    def test_returns_view_columns(self):
        row = get_assignment(self.conn, self.mine)
        self.assertEqual(row["course_code"], "PY101")
        self.assertEqual(row["student_name"], "Student One")
        self.assertEqual(row["status"], STATUSES[0])

    def test_missing_or_bad_id_gives_none(self):
        self.assertIsNone(get_assignment(self.conn, 9999))
        self.assertIsNone(get_assignment(self.conn, "x"))
        self.assertIsNone(get_assignment(self.conn, True))


if __name__ == "__main__":
    unittest.main()
