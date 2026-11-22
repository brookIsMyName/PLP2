"""Role and ownership tests for users.py (owner: Josia).

Run: python3 -m unittest discover -s tests -v
"""
import unittest
from datetime import date, timedelta

from database import get_connection, initialize_database
from users import get_user, list_users, can_edit_assignment
from assignments import add_assignment


class UserRoleTests(unittest.TestCase):
    def setUp(self):
        self.conn = get_connection(":memory:")
        initialize_database(self.conn)
        due = (date.today() + timedelta(days=3)).isoformat()
        # One assignment owned by Student One (user 1).
        self.aid = add_assignment(self.conn, 1, 1, "Roles Lab", due, "Medium")

    def tearDown(self):
        self.conn.close()

    def test_list_users_order_and_roles(self):
        users = list_users(self.conn)
        self.assertEqual([u["id"] for u in users], [1, 2, 3])
        self.assertEqual([u["role"] for u in users],
                         ["student", "student", "advisor"])

    def test_get_user_found_and_missing(self):
        self.assertEqual(get_user(self.conn, 1)["name"], "Student One")
        self.assertIsNone(get_user(self.conn, 99))

    def test_get_user_rejects_bad_ids(self):
        for bad in (0, -1, True, None, "abc", 1.5):
            self.assertIsNone(get_user(self.conn, bad), bad)
        self.assertEqual(get_user(self.conn, "2")["id"], 2)

    def test_owner_student_can_edit(self):
        self.assertTrue(can_edit_assignment(self.conn, 1, self.aid))

    def test_other_student_and_advisor_cannot_edit(self):
        self.assertFalse(can_edit_assignment(self.conn, 2, self.aid))
        self.assertFalse(can_edit_assignment(self.conn, 3, self.aid))

    def test_missing_user_or_assignment_is_false(self):
        self.assertFalse(can_edit_assignment(self.conn, 99, self.aid))
        self.assertFalse(can_edit_assignment(self.conn, 1, 9999))
        self.assertFalse(can_edit_assignment(self.conn, True, self.aid))
        self.assertFalse(can_edit_assignment(self.conn, "x", self.aid))


if __name__ == "__main__":
    unittest.main()
