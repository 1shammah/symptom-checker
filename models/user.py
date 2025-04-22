# logic around user authentication, registration, and role management
# fetch and structire user data from the database
# securely handle password hashing and verification
# encapsulate login and registration logic
# user helper methods from db for SoC
# handles crud operations for user data

from database import Database
from dataclasses import dataclass
from typing import Optional 
import bcrypt

# structured representation of a user
@dataclass
class User:
    name: str
    email: str
    gender: str = "Other"
    role: str = "User"

class UserModel:
    def __init__(self, db: Database):
        """
        Initialise with a database instance
        Args:
            db (Database): Database instance
        """
        self.db = db

    def register_user(self, name:str, email:str, password: str, gender="Other", role="User") -> bool:
        """
        Registers a new user with a hashed password if the email does not already exist
        Args:
            name (str): User name
            email (str): User email
            password (str): User password

        Returns:
            bool: True if registration is successful, False otherwise
        """

        try:
            if self.db.email_exists(email):
                print(f"Email already exists: {email}")
                return False
            
            hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            return self.db.add_user(name, email, hashed_pw, gender, role)
        
        except Exception as e:
            print(f"Error registering user: {e}")
            return False


    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Authenticates a user (login) by verifying the password. 

        Returns:
            User | None: Returns a User object if authentication is succesful, none otherwise
        """

        try:
            record = self.db.get_user_by_email(email)
            if record:
                stored_hash = record["password"]
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    return User(
                        name=record["name"],
                        email=record["email"],
                        gender=record["gender"],
                        role=record["role"]
                    )
            return None

        except Exception as e:
            print(f"Error authenticating user: {e}")
            return None

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        Retrieve a user by their ID

        Returns:
            User | None: user object if found, None otherwise
        """

        try:
            record = self.db.get_user_by_id(user_id)
            if record:
                return User(
                    name=record["name"],
                    email=record["email"],
                    gender=record["gender"],
                    role=record["role"]
                )
            return None
        except Exception as e:
            print(f"Error retrieving user by ID: {e}")
            return None
        
    def get_user_role(self, email: str) -> Optional[str]:
        """
        Fetches the role for a given user email. useful for access control

        Returns:
            str | None: user role if found, None otherwise
        """
        try:
            record = self.db.get_user_by_email(email)
            if record:
                return record["role"]
            return None
        except Exception as e:
            print(f"Error retrieving user role: {e}")
            return None

    def update_user(self, user_id: int, name: str, gender: str) -> bool:
        """
        Updates the user's name and gender
        
        Returns:
            bool: True if update is successful, False otherwise
        """
        try:
            return self.db.update_user(user_id, name, gender)
        except Exception as e:
            print(f"Error updating user {user_id}: {e}")
            return False
    
    def change_password(self, user_id: int, old_password: str, new_password: str) -> bool:

        """
        Verifies old password before updating to a new password
        
        Returns:
            bool: True if password change is successful, False otherwise
        """

        try:
            stored_hash = self.db.get_user_password(user_id)
            if stored_hash and bcrypt.checkpw(old_password.encode('utf-8'), stored_hash.encode('utf-8')):
                new_hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                return self.db.update_user_password(user_id, new_hashed)
            return False
        except Exception as e:
            print(f"Error changing password: {e}")
            return False

    def delete_user(self, user_id: int, password: str) -> bool:
        """
        Verifies user password before allowing deletion
        
        Returns:
            bool: True if account deleted successfully, False otherwise
        
        """

        try:
            stored_hash = self.db.get_user_password(user_id)
            if stored_hash and bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                return self.db.delete_user(user_id)
            return False
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

