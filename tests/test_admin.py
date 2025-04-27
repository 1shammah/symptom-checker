# use unittest not pytest

import unittest
from models.database import Database
from models.admin import AdminModel, AdminUser

class TestAdminModel(unittest.TestCase):
    def setUp(self):
        # Create a temporary in-memory database for testing. Each test will have a fresh database.
        self.db = Database(dbname=":memory:")
        self.db.create_tables()
        self.model = AdminModel(self.db)

        
    def test_get_all_users_empty(self):
        """ Should return an empty list when there are no users. """
        
        users = self.model.get_all_users()
        self.assertEqual(users, [])

    def test_get_all_users_nonempty(self):
        """ Should return a list of AdminUser objects for existing users. """
        
        # insert two users
        self.db.add_user("Alice", "alice@example.com", "pw1", gender="Female", role="User")
        self.db.add_user("Bob",   "bob@example.com",   "pw2", gender="Male",   role="Admin")
        self.db.conn.commit()

        users = self.model.get_all_users()
        
        # two entries in order of insertion
        self.assertEqual(len(users), 2)
        self.assertIsInstance(users[0], AdminUser)
        self.assertEqual(users[0].name, "Alice")
        self.assertEqual(users[0].email, "alice@example.com")
        self.assertEqual(users[0].gender, "Female")
        self.assertEqual(users[0].role, "User")
        self.assertEqual(users[1].name, "Bob")
        self.assertEqual(users[1].role, "Admin")

    def test_promote_to_admin_success(self):
        """ Should set a User’s role to Admin and return True. """
        
        self.db.add_user("Carol", "carol@example.com", "pw", role="User")
        self.db.conn.commit()
        result = self.model.promote_to_admin("carol@example.com")
        self.assertTrue(result)
        updated = self.db.get_user_by_email("carol@example.com")
        self.assertEqual(updated["role"], "Admin")

    def test_promote_to_admin_already_admin(self):
        """ Should return False if the user is already Admin. """
        
        self.db.add_user("Dave", "dave@example.com", "pw", role="Admin")
        self.db.conn.commit()
        result = self.model.promote_to_admin("dave@example.com")
        self.assertFalse(result)

    def test_promote_to_admin_nonexistent(self):
        """ Should return False when no user with given email exists. """
        
        result = self.model.promote_to_admin("nouser@example.com")
        self.assertFalse(result)

    def test_demote_to_user_success(self):
        """ Should set an Admin’s role back to User and return True. """
        
        self.db.add_user("Eve", "eve@example.com", "pw", role="Admin")
        self.db.conn.commit()
        result = self.model.demote_to_user("eve@example.com")
        self.assertTrue(result)
        updated = self.db.get_user_by_email("eve@example.com")
        self.assertEqual(updated["role"], "User")

    def test_demote_to_user_not_admin(self):
        """ Should return False if the user is not currently Admin. """
        
        self.db.add_user("Frank", "frank@example.com", "pw", role="User")
        self.db.conn.commit()
        result = self.model.demote_to_user("frank@example.com")
        self.assertFalse(result)

    def test_demote_to_user_nonexistent(self):
        """ Should return False when no user with given email exists. """
        
        result = self.model.demote_to_user("ghost@example.com")
        self.assertFalse(result)

    def test_delete_user_success(self):
        """ Should delete an existing user by ID and return True. """
        
        self.db.add_user("Grace", "grace@example.com", "pw")
        self.db.conn.commit()
        row = self.db.get_user_by_email("grace@example.com")
        user_id = row["id"]

        result = self.model.delete_user(user_id)
        self.assertTrue(result)
        
        # confirm removal
        self.assertIsNone(self.db.get_user_by_email("grace@example.com"))
        self.assertIsNone(self.db.get_user_by_id(user_id))

    def test_delete_user_nonexistent(self):
        """ Should return False when attempting to delete a non-existent user. """
        
        result = self.model.delete_user(12345)
        self.assertFalse(result)

    def test_delete_user_invalid_id_type(self):
        """ Should return False when passed a non-integer ID. """
        
        self.assertFalse(self.model.delete_user("not_an_int"))
        self.assertFalse(self.model.delete_user(None))


if __name__ == "__main__":
    unittest.main()