# tests the methods in the database model
# doesn't test the load functions as they are csv based
# import from models.database since they are in a different directory
# using an in-memory SQLite database for testing ":memory:". Manually seeding the database with test data.

import unittest
import sqlite3
from models.database import Database

class TestDatabaseHelper(unittest.TestCase):
    def setUp(self):
        # Create a temporary in-memory database for testing. Each test will have a fresh database.
        self.db = Database(dbname=":memory:")
        self.db.create_tables()

    
    # Test the get_all_diseases method when the database is empty
    def test_get_all_diseases_empty(self):
        """ Verifies that the get_all_diseases method returns an empty list 
            when no diseases are present in the database. This is an edge case. 
        """
        self.assertEqual(self.db.get_all_diseases(), [])

        


