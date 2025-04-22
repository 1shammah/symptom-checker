# logic around user authentication, registration, and role management
# fetch and structire user data from the database
# securely handle password hashing and verification
# encapsulate login and registration logic
# user helper methods from db for SoC

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
        
    # should we do a login method here?


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
            print(f"Error authenicating user: {e}")
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

