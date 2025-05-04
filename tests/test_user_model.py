# use unittest not pytest

import unittest
from models.database import Database
from models.admin import AdminModel, AdminUser

class TestAdminModel(unittest.TestCase):
    
    def setUp(self):
    # fresh in-memory database
        self.db = Database(dbname=":memory:")
        self.db.reset_schema()
        self.admin_model = AdminModel(self.db)

    ############# get_all_users() #############

    def test_get_all_users_empty(self):
        """ Should return an empty list when no users exist. """
        
        users = self.admin_model.get_all_users()
        self.assertEqual(users, [])

    def test_get_all_users_nonempty(self):
        """ Should return a list of AdminUser objects for each user. """
        
        # add two users with different roles
        self.db.add_user("Alice Example", "alice@example.com", "hash1", gender="Female", role="User")
        self.db.add_user("Bob Example",   "bob@example.com",   "hash2", gender="Male",   role="Admin")
        self.db.conn.commit()

        users = self.admin_model.get_all_users()
        self.assertEqual(len(users), 2)

        # ensure each is an AdminUser and fields match
        alice_user, bob_user = users
        self.assertIsInstance(alice_user, AdminUser)
        self.assertEqual(alice_user.name, "Alice Example")
        self.assertEqual(alice_user.email, "alice@example.com")
        self.assertEqual(alice_user.gender, "Female")
        self.assertEqual(alice_user.role, "User")

        self.assertIsInstance(bob_user, AdminUser)
        self.assertEqual(bob_user.name, "Bob Example")
        self.assertEqual(bob_user.email, "bob@example.com")
        self.assertEqual(bob_user.gender, "Male")
        self.assertEqual(bob_user.role, "Admin")

    
    ############# promote_to_admin() #############

    def test_promote_to_admin_success(self):
        """ Should change a User to Admin and return True. """
        
        # add a regular user
        self.db.add_user("Carol User", "carol@example.com", "hash3", gender="Other", role="User")
        self.db.conn.commit()

        result = self.admin_model.promote_to_admin("carol@example.com")
        self.assertTrue(result)

        # verify role updated in database
        record = self.db.get_user_by_email("carol@example.com")
        self.assertEqual(record["role"], "Admin")

    def test_promote_to_admin_already_admin(self):
        """ Should do nothing and return False if the user is already an Admin. """
        
        # add an admin user
        self.db.add_user("Dave Admin", "dave@example.com", "hash4", gender="Male", role="Admin")
        self.db.conn.commit()

        result = self.admin_model.promote_to_admin("dave@example.com")
        self.assertFalse(result)

        # role remains Admin
        record = self.db.get_user_by_email("dave@example.com")
        self.assertEqual(record["role"], "Admin")

    def test_promote_to_admin_nonexistent_email(self):
        """ Should return False when the email does not match any user. """
        
        result = self.admin_model.promote_to_admin("noone@nowhere.com")
        self.assertFalse(result)

    ############# demote_to_user() #############

    def test_demote_to_user_success(self):
        """ Should change an Admin to User and return True. """
        
        # add an admin user
        self.db.add_user("Eve Admin", "eve@example.com", "hash5", gender="Female", role="Admin")
        self.db.conn.commit()

        result = self.admin_model.demote_to_user("eve@example.com")
        self.assertTrue(result)

        # verify role updated in database
        record = self.db.get_user_by_email("eve@example.com")
        self.assertEqual(record["role"], "User")

    def test_demote_to_user_not_admin(self):
        """ Should do nothing and return False if the user is not an Admin. """
        
        # add a regular user
        self.db.add_user("Frank User", "frank@example.com", "hash6", gender="Male", role="User")
        self.db.conn.commit()

        result = self.admin_model.demote_to_user("frank@example.com")
        self.assertFalse(result)

        # role remains User
        record = self.db.get_user_by_email("frank@example.com")
        self.assertEqual(record["role"], "User")

    def test_demote_to_user_nonexistent_email(self):
        """ Should return False when the email does not match any user. """
        
        result = self.admin_model.demote_to_user("ghost@domain.com")
        self.assertFalse(result)

    ############# delete_user() #############

    def test_delete_user_success(self):
        """ Should remove the user and return True given a valid user_id. """
        
        # add and commit a user
        self.db.add_user("Grace Delete", "grace@example.com", "hash7", gender="Female", role="User")
        self.db.conn.commit()
        record = self.db.get_user_by_email("grace@example.com")
        user_id = record["id"]

        result = self.admin_model.delete_user(user_id)
        self.assertTrue(result)

        # ensure user no longer exists
        self.assertIsNone(self.db.get_user_by_email("grace@example.com"))

    def test_delete_user_nonexistent_id(self):
        """ Should return False when attempting to delete a non-existent user_id. """
        
        result = self.admin_model.delete_user(9999)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()