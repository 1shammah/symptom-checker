# Use a fake User model to test only the controller logic
# Skips setting up a real database
# Helps to check the controller calls the right model methods
# Passes the correct info and handles success/errors correctly

import unittest
from unittest.mock import MagicMock
from controllers.user_controller import UserController
from models.user import User

class TestUserController(unittest.TestCase):
    def setUp(self):
        # create controller with fake Database
        self.fake_db = MagicMock() 
        self.controller = UserController(self.fake_db)
        
        # replace its UserModel with a MagicMock
        self.fake_user_model = MagicMock()
        self.controller.user_model = self.fake_user_model


############# register_user() #############

    def test_register_user_success(self):
        """Should return True when model.register_user succeeds."""
        
        self.fake_user_model.register_user.return_value = True

        result = self.controller.register_user(
            name="Alice",
            email="alice@example.com",
            password="securepass",
            gender="Female",
            role="User"
        )

        self.assertTrue(result)
        self.fake_user_model.register_user.assert_called_once_with(
            name="Alice",
            email="alice@example.com",
            password="securepass",
            gender="Female",
            role="User"
        )

    def test_register_user_failure(self):
        """Should return False when model.register_user returns False."""
        self.fake_user_model.register_user.return_value = False

        result = self.controller.register_user(
            name="Bob",
            email="bob@example.com",
            password="pass123",
            gender="Other",
            role="User"
        )

        self.assertFalse(result)

    def test_register_user_exception(self):
        """Should return False when model.register_user raises."""
        
        self.fake_user_model.register_user.side_effect = RuntimeError("DB error")

        result = self.controller.register_user(
            name="Carol",
            email="carol@example.com",
            password="pw",
            gender="Other",
            role="User"
        )

        self.assertFalse(result) 

############# login_user() #############

    def test_login_user_success(self):
            """Should return a User when credentials are correct."""
            
            fake_user = User(name="Dave", email="dave@x.com", gender="Male", role="User")
            self.fake_user_model.authenticate_user.return_value = fake_user

            returned = self.controller.login_user(email="dave@x.com", password="pw")

            self.assertIs(returned, fake_user)
            self.fake_user_model.authenticate_user.assert_called_once_with(
                email="dave@x.com", password="pw"
            )

    def test_login_user_bad_credentials(self):
            """Should return None when credentials are wrong."""
            
            self.fake_user_model.authenticate_user.return_value = None

            returned = self.controller.login_user(email="eve@x.com", password="wrong")

            self.assertIsNone(returned)

    def test_login_user_exception(self):
        """Should return None when model.authenticate_user raises an exception."""
        
        self.fake_user_model.authenticate_user.side_effect = Exception("fail")

        returned = self.controller.login_user(email="f@x.com", password="pw")

        self.assertIsNone(returned)

############# get_profile() #############


    def test_get_profile_found(self):
        """Should return User object when model.get_user_by_id finds a user."""
        
        fake_user = User(name="Gina", email="g@x.com", gender="Other", role="User")
        self.fake_user_model.get_user_by_id.return_value = fake_user

        returned = self.controller.get_profile(user_id=10)

        self.assertIs(returned, fake_user)
        self.fake_user_model.get_user_by_id.assert_called_once_with(10)
    
    def test_get_profile_not_found(self):
        """Should return None when no user with given ID exists."""
        
        self.fake_user_model.get_user_by_id.return_value = None

        returned = self.controller.get_profile(user_id=999)

        self.assertIsNone(returned)

    def test_get_profile_exception(self):
        """Should return None when model.get_user_by_id raises."""
        
        self.fake_user_model.get_user_by_id.side_effect = Exception("oops")

        returned = self.controller.get_profile(user_id=5)

        self.assertIsNone(returned)

############# update_profile() #############

    def test_update_profile_success(self):
        """Should return True when update_user succeeds."""
        
        self.fake_user_model.update_user.return_value = True

        result = self.controller.update_profile(user_id=2, name="Helen", gender="Female")

        self.assertTrue(result)
        self.fake_user_model.update_user.assert_called_once_with(2, "Helen", "Female")

    def test_update_profile_failure(self):
        """Should return False when update_user returns False."""
        
        self.fake_user_model.update_user.return_value = False

        result = self.controller.update_profile(user_id=3, name="Ian", gender="Male")

        self.assertFalse(result)

    def test_update_profile_exception(self):
        """Should return False when model.update_user raises."""
        
        self.fake_user_model.update_user.side_effect = RuntimeError("err")

        result = self.controller.update_profile(user_id=4, name="Jack", gender="Other")

        self.assertFalse(result)

############# change_password() #############

    def test_change_password_success(self):
        """Should return True when change_password succeeds."""
        
        self.fake_user_model.change_password.return_value = True

        result = self.controller.change_password(
            user_id=7,
            old_password="oldpass",
            new_password="newpass"
        )

        self.assertTrue(result)
        self.fake_user_model.change_password.assert_called_once_with(
            user_id=7, old_password="oldpass", new_password="newpass"
        )

    def test_change_password_failure(self):
        """Should return False when change_password returns False."""
        
        self.fake_user_model.change_password.return_value = False

        result = self.controller.change_password(
            user_id=8,
            old_password="old",
            new_password="new"
        )

        self.assertFalse(result)

    def test_change_password_exception(self):
        """Should return False when model.change_password raises an exception."""
        
        self.fake_user_model.change_password.side_effect = Exception("fail")

        result = self.controller.change_password(
            user_id=9,
            old_password="x",
            new_password="y"
        )

        self.assertFalse(result)

############# delete_account() #############

    def test_delete_account_success(self):
        """Should return True when delete_user succeeds."""
        
        self.fake_user_model.delete_user.return_value = True

        result = self.controller.delete_account(user_id=11, password="pw11")

        self.assertTrue(result)
        self.fake_user_model.delete_user.assert_called_once_with(user_id=11, password="pw11")

    def test_delete_account_failure(self):
        """Should return False when delete_user returns False."""
        
        self.fake_user_model.delete_user.return_value = False

        result = self.controller.delete_account(user_id=12, password="pw12")

        self.assertFalse(result)

    def test_delete_account_exception(self):
        """Should return False when model.delete_user raises."""
        
        self.fake_user_model.delete_user.side_effect = RuntimeError("err")

        result = self.controller.delete_account(user_id=13, password="pw13")

        self.assertFalse(result)

    ############# delete_account() #############

    def test_logout_user_noop(self):
        """Should not raise when logout_user is called."""
        
        # no return value expected
        self.controller.logout_user()
        # reaching here means success

if __name__ == "__main__":
    unittest.main()