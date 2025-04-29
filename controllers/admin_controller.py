# Controller handles admin actions
# it lists all users, demotes an admin to regular user, deletes a user account

from typing import List
from models.database import Database
from models.admin import AdminModel, AdminUser

class AdminController:
    def __init__(self, db: Database):
        """
        Initialise controller with a database instance.
        Creates an AdminModel to perform business logic.
        """
        self.db = db
        self.admin_model = AdminModel(db)

    def list_users(self) -> List[AdminUser]:
        """
        Fetch all users for the admin dashboard.

        Returns:
            List[AdminUser]: list of all users
        """
        try:
            
            return self.admin_model.get_all_users()
        
        except Exception as error:
            print(f"AdminController.list_users error: {error}")
            return []
        
    def promote_user(self, email: str) -> bool:
        """
        Promote the user with the given email to admin role.

        Returns:
            bool: True on success, False on failure
        """
        try:
            
            return self.admin_model.promote_to_admin(email)
        
        except Exception as error:
            print(f"AdminController.promote_user error: {error}")
            return False

    def demote_user(self, email: str) -> bool:
        """
        Demote the user with the given email to regular role.

        Returns:
            bool: True on success, False on failure
        """
        try:
            
            return self.admin_model.demote_to_user(email)
        
        except Exception as error:
            print(f"AdminController.demote_user error: {error}")
            return False

    def delete_user(self, user_id: int) -> bool:
        """
        Delete the user account matching the given ID.

        Returns:
            bool: True on success, False on failure
        """
        try:
            return self.admin_model.delete_user(user_id)
        except Exception as error:
            print(f"AdminController.delete_user error: {error}")
            return False