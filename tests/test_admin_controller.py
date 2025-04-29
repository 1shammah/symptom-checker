# Use a fake User model to test only the controller logic
# Skips setting up a real database
# Helps to check the controller calls the right model methods
# Passes the correct info and handles success/errors correctly

import unittest
from unittest.mock import MagicMock
from controllers.admin_controller import AdminController
from models.admin import AdminUser

class TestAdminController(unittest.TestCase):
    def setUp(self):
        # Create controller with a fake Database instance
        self.fake_db = MagicMock()
        self.controller = AdminController(self.fake_db)
        # Replace its AdminModel with a MagicMock to isolate controller logic
        self.fake_admin_model = MagicMock()
        self.controller.admin_model = self.fake_admin_model

    ############# list_users #############

    def test_list_users_success(self):
        """Should return list of AdminUser when model.get_all_users succeeds."""
        
        fake_users = [
            AdminUser(name="Alice", email="alice@example.com", gender="Female", role="User"),
            AdminUser(name="Bob",   email="bob@example.com",   gender="Male",   role="Admin")
        ]
        self.fake_admin_model.get_all_users.return_value = fake_users

        result = self.controller.list_users()

        self.assertEqual(result, fake_users)
        self.fake_admin_model.get_all_users.assert_called_once()

    def test_list_users_exception(self):
        """Should return empty list when model.get_all_users raises an exceptions."""
        
        self.fake_admin_model.get_all_users.side_effect = RuntimeError("DB error")

        result = self.controller.list_users()

        self.assertEqual(result, [])
        self.fake_admin_model.get_all_users.assert_called_once()

    ############# promote_user #############

    def test_promote_user_success(self):
        """Should return True when model.promote_to_admin succeeds."""
        
        self.fake_admin_model.promote_to_admin.return_value = True

        result = self.controller.promote_user("carol@example.com")

        self.assertTrue(result)
        self.fake_admin_model.promote_to_admin.assert_called_once_with("carol@example.com")

    def test_promote_user_failure(self):
        """Should return False when model.promote_to_admin returns False."""
        
        self.fake_admin_model.promote_to_admin.return_value = False

        result = self.controller.promote_user("dave@example.com")

        self.assertFalse(result)
        self.fake_admin_model.promote_to_admin.assert_called_once_with("dave@example.com")

    def test_promote_user_exception(self):
        """Should return False when model.promote_to_admin raises."""
        
        self.fake_admin_model.promote_to_admin.side_effect = RuntimeError("Permission denied")

        result = self.controller.promote_user("eve@example.com")

        self.assertFalse(result)
        self.fake_admin_model.promote_to_admin.assert_called_once_with("eve@example.com")

    ############# demote_user #############

    def test_demote_user_success(self):
        """Should return True when model.demote_to_user succeeds."""
        
        self.fake_admin_model.demote_to_user.return_value = True

        result = self.controller.demote_user("frank@example.com")

        self.assertTrue(result)
        self.fake_admin_model.demote_to_user.assert_called_once_with("frank@example.com")

    def test_demote_user_failure(self):
        """Should return False when model.demote_to_user returns False."""
        
        self.fake_admin_model.demote_to_user.return_value = False

        result = self.controller.demote_user("gina@example.com")

        self.assertFalse(result)
        self.fake_admin_model.demote_to_user.assert_called_once_with("gina@example.com")

    def test_demote_user_exception(self):
        """Should return False when model.demote_to_user raises."""
        
        self.fake_admin_model.demote_to_user.side_effect = RuntimeError("Cannot demote")

        result = self.controller.demote_user("harry@example.com")

        self.assertFalse(result)
        self.fake_admin_model.demote_to_user.assert_called_once_with("harry@example.com")

    ############# delete_user #############

    def test_delete_user_success(self):
        """Should return True when model.delete_user succeeds."""
        
        self.fake_admin_model.delete_user.return_value = True

        result = self.controller.delete_user(42)

        self.assertTrue(result)
        self.fake_admin_model.delete_user.assert_called_once_with(42)

    def test_delete_user_failure(self):
        """Should return False when model.delete_user returns False."""
        
        self.fake_admin_model.delete_user.return_value = False

        result = self.controller.delete_user(100)

        self.assertFalse(result)
        self.fake_admin_model.delete_user.assert_called_once_with(100)

    def test_delete_user_exception(self):
        """Should return False when model.delete_user raises."""
        
        self.fake_admin_model.delete_user.side_effect = RuntimeError("Deletion error")

        result = self.controller.delete_user(7)

        self.assertFalse(result)
        self.fake_admin_model.delete_user.assert_called_once_with(7)

if __name__ == "__main__":
    unittest.main()
