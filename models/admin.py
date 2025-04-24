# logic for admin-level ops
# view all users, promote/demote roles, delete users
# separates business logic from controllers and views
# resuses database helpers for user management

from database import Database
from dataclasses import dataclass
from typing import List, Optional 

@dataclass
class AdminUser:
    name: str
    email: str
    gender: str
    role: str

class AdminModel:
    def __init__(self, db: Database):
        self.db = db

    def get_all_users(self) -> List[AdminUser]:
        """ 
        Returns all users in the system

        Returns:
            list[AdminUser]: List of AdminUser objects representing all users
        """

        try: 
            rows = self.db.get_all_users()
            return [AdminUser(name=row["name"], email=row["email"], gender=row["gender"], role=row["role"]) for row in rows]
        except Exception as e:
            print(f"Error fetching all users: {e}")
            return []
        
    def promote_to_admin(self, email: str) -> bool:
        """
        Promotes a user to admin role

        Args:
            email (str): Email of the user to promote

        Returns:
            bool: True if promotion was successful, False otherwise
        """

        try:
            user = self.db.get_user_by_email(email)
            if user and user["role"] != "Admin":
                return self.db.set_user_role(user["id"], "Admin")
            return False
        except Exception as e:
            print(f"Error promoting user to admin: {e}")
            return False
        
    
    #demote_to_user() – for downgrading admin to user role.

    def demote_to_user(self, email: str) -> bool:
        """
        Demote admin to a regular user role
        """

        try:
            user = self.db.get_user_by_email(email)
            if user and user["role"] == "Admin":
                return self.db.set_user_role(user["id"], "User")
            return False
        except Exception as e:
            print(f"Error demoting user to regular: {e}")
            return False


    def delete_user(self, user_id: int) -> bool:
        """
        Deletes a user account (irreversible action)
        """
        try:
            return self.db.delete_user_by_id(user_id)
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False