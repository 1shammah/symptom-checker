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

    ############# get_all_diseases #############

    def test_get_all_diseases_empty(self):
        """Should return an empty list when there are no diseases in the database"""
        self.assertEqual(self.db.get_all_diseases(), [])

    def test_get_all_diseases_nonempty(self):
        """ Should return one entry after inserting a single disease """
        # Seed the database with a single disease for testing
        self.db.cur.execute("INSERT INTO diseases (disease_name) VALUES ('Flu')")
        self.db.conn.commit()
        rows = self.db.get_all_diseases()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["disease_name"], "Flu")

    def test_get_all_diseases_multiple_rows(self):
        """ Should return all inserted diseases in insertion order"""
        self.db.cur.executemany("INSERT INTO diseases (disease_name) VALUES (?)",
            [("Cold",), ("Malaria",), ("Allergy",)]
        )
        self.db.conn.commit()
        rows = self.db.get_all_diseases()
        self.assertEqual(len(rows), 3)
        # check order by primary key
        self.assertEqual([r["disease_name"] for r in rows],
                        ["Cold", "Malaria", "Allergy"]) 
        
    def test_get_all_diseases_uniqueness_constraint(self):
        """ Should not allow duplicates, using INSERT OR IGNORE """
        # first insert succeeds
        self.db.cur.execute(
            "INSERT OR IGNORE INTO diseases (disease_name) VALUES ('Flu')"
        )
        # second insert is ignored due to UNIQUE constraint
        self.db.cur.execute(
            "INSERT OR IGNORE INTO diseases (disease_name) VALUES ('Flu')"
        )
        self.db.conn.commit()
        rows = self.db.get_all_diseases()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["disease_name"], "Flu")

    def test_get_all_diseases_schema_integrity(self):
        """ Each returned row must have 'id' as int and disease_name as str """
        self.db.cur.execute(
            "INSERT INTO diseases (disease_name) VALUES ('TestDisease')"
        )
        self.db.conn.commit()
        row = self.db.get_all_diseases()[0] ## get the first row
        
        # check that the column names are correct
        cols = row.keys() #keys() returns the column names
        self.assertIn("id", cols)
        self.assertIn("disease_name", cols)
        
        # check that the types are correct
        self.assertIsInstance(row["id"], int)
        self.assertIsInstance(row["disease_name"], str)

    ############# get_all_symptoms #############
    
    def test_get_all_symptoms_empty(self):
        """Should return an empry list when no symptoms exist """
        self.assertEqual(self.db.get_all_symptoms(), [])

    def test_get_all_symptoms_nonempty(self):
        """ Should return one entry after inserting a single symptom with description"""
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name, description) VALUES ('Cough', 'Dry cough')"
        )
        self.db.conn.commit()
        rows = self.db.get_all_symptoms()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["symptom_name"], "Cough")
        self.assertEqual(rows[0]["description"], "Dry cough")

    def test_get_all_symptoms_multiple_rows(self):
        """ Should return all inserted symptoms in insertion order, keeping NULL values """
        # insert symtoms with and without description
        self.db.cur.executemany(
            "INSERT INTO symptoms (symptom_name, description) VALUES (?, ?)",
            [
                ("Sneezing", None),
                ("Fever", "High temperature"),
                ("Headache", "Pain in head"),
            ]
        )
        self.db.conn.commit()
        rows = self.db.get_all_symptoms()
        self.assertEqual(len(rows), 3)
        names = [r["symptom_name"] for r in rows]
        self.assertEqual(names, ["Sneezing", "Fever", "Headache"])

    def test_get_all_symptoms_null_description(self):
        """ A symptom inserted with no description should be return description=None"""
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name) VALUES ('Itching')"
        )
        self.db.conn.commit()
        row = self.db.get_all_symptoms()[0]
        self.assertEqual(row["symptom_name"], "Itching")
        self.assertIsNone(row["description"])

    def test_get_all_symptoms_uniqueness_constraint(self):
        """ Each row returned must have 'id', 'symptom_name' and 'description' keys with correct types"""
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name, description) VALUES ('TestSymptom', 'Desc')"
        )
        self.db.conn.commit()
        row = self.db.get_all_symptoms()[0]

        # check that the column names are correct
        cols = row.keys()
        self.assertIn("id", cols)
        self.assertIn("symptom_name", cols)
        self.assertIn("description", cols)

        # check that the types are correct
        self.assertIsInstance(row["id"], int)
        self.assertIsInstance(row["symptom_name"], str)

        # description can be NULL, so we check that it is either str or None
        self.assertTrue(isinstance(row["description"], str) or row["description"] is None)





    # do I end with:
    # if __name__ == '__main__':
    #     unittest.main()