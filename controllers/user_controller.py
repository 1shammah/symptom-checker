from typing import Optional
from models.database import Database
from models.user import UserModel, User

class UserController:
    """
    Controller for user-facing actions:
    registration, authentication, profile management, and account deletion
    Separates view logic from model logic
    """

    def __init__ (self, db: Optional[Database] = None):
        """
        Initialise UserController with a Database instance and UserModel
        If no database is passed, use the default file-based db
        """

        # use provded db or create a new one
        self.db = db if db else Database()
        
        #ensure tables exist
        self.db.create_tables()
        
        #instantiate the user model with the database
        self.user_model = UserModel(self.db)

    def register_user(
            self,
            name: str,
            email: str,
            password: str,
            gender: str = "Other",
            role: str = "User",
    ) -> bool:
        """
        Register a new user with hashed password.

        Checks email uniqueness. Delegates hashing and insertion.

        Args:
            name: Full name of the user
            email: Unique email address
            password: Plain text password
            gender: Gender field, defaults to 'Other'
            role: Role field, defaults to 'User'

        Returns:
            True if registration succeeds, False otherwise.
        """

        try:
            success = self.user_model.register_user(
                name=name,
                email=email,
                password=password,
                gender=gender,
                role=role,
            )
            return success
        except Exception as e:
            print(f"UserController.register_user error: {e}")
            return False
        
    
    def login_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user credentials
        Returns a User object on success, or None on failure
        """
        try:
            
            user = self.user_model.authenticate_user(email=email, password=password)
            return user
        
        except Exception as error:
            print(f"UserController.login_user error: {error}")
            return None

    def logout_user(self) -> None:
        """
        Placeholder for logout logic
        Session or token clearing is handled at the view layer
        """
        return None
    
    def get_profile(self, user_id: int) -> Optional[User]:
        """
        Retrieve a User by their ID
        Returns a User object or None if not found
        """
        try:
            
            return self.user_model.get_user_by_id(user_id)
        
        except Exception as error:
            print(f"UserController.get_profile error: {error}")
            return None
        
    def update_profile(self, user_id: int, name: str, gender: str) -> bool:
        """
        Update a user's name and gender.
        Returns True if update succeeds, False otherwise.
        """
        try:
            return self.user_model.update_user(user_id, name, gender)
        except Exception as error:
            print(f"UserController.update_profile error: {error}")
            return False
        
    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change a user's password after verifying the old password.
        Returns True if password change succeeds, False otherwise.
        """
        try:
            
            return self.user_model.change_password(
                user_id=user_id,
                old_password=old_password,
                new_password=new_password
            )
        
        except Exception as error:
            print(f"UserController.change_password error: {error}")
            return False

    def delete_account(self, user_id: int, password: str) -> bool:
        """
        Delete a user's account after verifying their password.
        Returns True if deletion succeeds, False otherwise.
        """
        try:
            
            return self.user_model.delete_user(user_id=user_id, password=password)
        
        except Exception as error:
            print(f"UserController.delete_account error: {error}")
            return False