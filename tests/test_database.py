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


    ############# get_symptoms_by_disease #############

    def test_get_symptoms_by_disease_empty(self):
        """ When no link exists between disease and symptoms, should return empty list """
        self.assertEqual(self.db.get_symptoms_by_disease("Nonexistent"), [])
        
        #"Nonexistent" is the name of a disease that doesn't exist in the database

    def test_get_symptoms_by_disease_with_single_link(self):
        """ Should return a single symptom linked to one disease"""

        # seed the database with a disease and a symptom
        self.db.cur.execute("INSERT INTO diseases (disease_name) VALUES ('DiseaseA')")
        self.db.cur.execute("INSERT INTO symptoms (symptom_name) VALUES ('SymptomX')")
        self.db.conn.commit()

        disease_id = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = 'DiseaseA'"

        ).fetchone()["id"]
        symptom_id = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = 'SymptomX'"
        ).fetchone()["id"]

        # link the disease and symptom
        self.db.cur.execute(
            "INSERT INTO symptom_disease (disease_id, symptom_id) VALUES (?, ?)",
            (disease_id, symptom_id)
        )
        self.db.conn.commit()

        self.assertEqual(self.db.get_symptoms_by_disease("DiseaseA"), ["SymptomX"])

    def test_get_symptoms_by_disease_with_multiple_links(self):
        """ Should return all symptoms linked to a disease """
        
        # seed disease and multiple symptoms
        self.db.cur.execute("INSERT INTO diseases (disease_name) VALUES ('D2')")
        self.db.cur.executemany(
            "INSERT INTO symptoms (symptom_name) VALUES (?)",
            [("s1",), ("s2",), ("s3",)] #this is a tuple ("s1",) not a string
        )
        self.db.conn.commit()

        # get the disease id and symptom ids
        disease_id = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = 'D2'"
        ).fetchone()["id"]
        symptom_ids = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name IN ('s1', 's2', 's3')"
        ).fetchall()
        symptom_ids = [r["id"] for r in self.db.cur.execute("SELECT id FROM symptoms")]

        # link the disease and symptoms
        for symptom_id in symptom_ids:
            self.db.cur.execute(
                "INSERT INTO symptom_disease (disease_id, symptom_id) VALUES (?, ?)",
                (disease_id, symptom_id)
            )
        self.db.conn.commit()

        self.assertCountEqual(self.db.get_symptoms_by_disease("D2"), ["s1", "s2", "s3"])

        ############# get_diseases_by_symptom #############

    def test_get_disease_by_symptom_empty(self):
        """ When no link exists between disease and symptoms, should return empty list """
        self.assertEqual(self.db.get_diseases_by_symptom("NoSymptom"), [])

        # "NoSymptom" is the name of a symptom that doesn't exist in the database

    def test_get_disease_by_symptom_with_single_link(self):
        """ Should return a single disease linked to one symptom """

        # seed disease and symptom
        self.db.cur.execute("INSERT INTO diseases (disease_name) VALUES ('DA')")
        self.db.cur.execute("INSERT INTO symptoms (symptom_name) VALUES ('SX')")
        self.db.conn.commit()

        # get the disease id and symptom id
        disease_id = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = 'DA'"   
        ).fetchone()["id"]
        symptom_id = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = 'SX'"
        ).fetchone()["id"]

        # link the disease and symptom
        self.db.cur.execute(
            "INSERT INTO symptom_disease (disease_id, symptom_id) VALUES (?, ?)",
            (disease_id, symptom_id)
        )
        self.db.conn.commit()

        self.assertEqual(self.db.get_diseases_by_symptom("SX"), ["DA"])

    def test_get_disease_by_symptom_with_multiple_links(self):
        """ Should return all diseases linked to a symptom """

        # seed multiple diseases and one symptom
        self.db.cur.executemany(
            "INSERT INTO diseases (disease_name) VALUES (?)",
            [("dA",), ("dB",), ("dC",)]
        )
        self.db.cur.execute("INSERT INTO symptoms (symptom_name) VALUES ('sZ')")
        self.db.conn.commit()

        # get symptom id and disease ids

        symptom_id = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = 'sZ'"
        ).fetchone()["id"]
        disease_ids = [r["id"] for r in self.db.cur.execute("SELECT id FROM diseases").fetchall()]

        # link the symptom and diseases
        for disease_id in disease_ids:
            self.db.cur.execute(
                "INSERT INTO symptom_disease (disease_id, symptom_id) VALUES (?, ?)",
                (disease_id, symptom_id)
            )
        self.db.conn.commit()

        ############# get_description_by_symptom #############

    def test_get_description_by_symptom_empty(self):
        """ SHould return None when no symptom exists """
        self.assertIsNone(self.db.get_description_by_symptom("Nonexistent"))

    def test_get_description_by_symptom_single(self):
        """ Should return the correct description for an existing symptom"""

        # insert a symptom with a description
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name, description) VALUES (?, ?)",
            ("Headache", "Pain in head")
        )
        self.db.conn.commit()
        self.assertEqual(
            self.db.get_description_by_symptom("Headache"), "Pain in head"
        )
    
    def test_get_description_by_symptom_null(self):
        """ Should return None if the symptom exists but description is NULL """
        # insert a symptom with no description (NULL)
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name) VALUES (?)",
            ("Itching",)
        )
        self.db.conn.commit()
        self.assertIsNone(self.db.get_description_by_symptom("Itching"))

    ############# get_precautions_by_disease #############

    def test_get_precautions_by_disease_empty(self):
        """ Should return None when no disease exists """
        self.assertIsNone(self.db.get_precautions_by_disease("NoDisease"))

    def test_get_precautions_by_disease_single(self):
        """ Should return a single-tem list when there's one precaution """
        # seed one disease
        self.db.cur.execute(

            "INSERT INTO diseases (disease_name) VALUES (?)",
            ("Disease1",)
        )
        self.db.conn.commit()

        # get the disease id
        disease_id = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = ?", 
            ("Disease1",)
        ).fetchone()["id"]

        # insert one precaution for the disease

        self.db.cur.execute(
            "INSERT INTO symptom_precautions (disease_id, precaution_steps) VALUES (?, ?)",
            (disease_id, "step1")
        )
        self.db.conn.commit()

        self.assertEqual(
            self.db.get_precautions_by_disease("Disease1"), ["step1"]
        )

    def test_get_precautions_by_disease_multiple(self):
        """ Should split a comma-separated string into a list """
        # seed disease

        self.db.cur.execute(
            "INSERT INTO diseases (disease_name) VALUES (?)",
            ("Disease2",)
        )
        self.db.conn.commit()

        # get the disease id
        disease_id = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = ?",
            ("Disease2",)
        ).fetchone()["id"]

        # insert multiple precautions for the disease

        self.db.cur.execute(
            "INSERT INTO symptom_precautions (disease_id, precaution_steps) VALUES (?, ?)",
            (disease_id, "step1, step2, step3")
        )
        self.db.conn.commit()

        self.assertEqual(
            self.db.get_precautions_by_disease("Disease2"),
            ["step1", "step2", "step3"]
        )

    def test_get_precautions_by_disease_null_steps(self):

        """ Split should still return [''] if precaution_steps is an empty string """

        # seed disease
        self.db.cur.execute(
            "INSERT INTO diseases (disease_name) VALUES (?)",
            ("Disease3",)
        )
        self.db.conn.commit()

        # get the disease id
        disease_id = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = ?",
            ("Disease3",)
        ).fetchone()["id"]

        # insert empty precaution steps for the disease
        self.db.cur.execute(
            "INSERT INTO symptom_precautions (disease_id, precaution_steps) VALUES (?, ?)",
            (disease_id, "")
        )

        self.db.conn.commit()

        self.assertEqual(
            self.db.get_precautions_by_disease("Disease3"),
            [""]
        )
    
    
        ############# get_severity_by_symptom #############

    def test_get_severity_by_symptom_empty(self):
        """ Should retunr None when no symptom exists """
        self.assertIsNone(self.db.get_severity_by_symptom("NoSymptom"))

    def test_get_severity_by_symptom_single(self):
        """ Should return the correct severity level for an existing symptom """
        # seed symptom
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name) VALUES (?)",
            ("Fatigue",)
        )
        self.db.conn.commit()

        # fetch the symptom id
        symptom_id = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = ?",
            ("Fatigue",)
        ).fetchone()["id"]

        # insert severity level for the symptom
        self.db.cur.execute(
            "INSERT INTO symptom_severity (symptom_id, severity_level) VALUES (?, ?)",
            (symptom_id, "2")
        )
        self.db.conn.commit()

        self.assertEqual(
            self.db.get_severity_by_symptom("Fatigue"), "2"
        )
            
    def test_get_severity_by_symptom_no_mapping(self):
        """ should return None when a symptom exists but no severity row"""

        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name) VALUES (?)",
            ("Nausea",)
        )
        self.db.conn.commit()
        self.assertIsNone(self.db.get_severity_by_symptom("Nausea"))
    
    def test_get_severity_by_symptom_type(self):
        """ Should return a string for severity level representing a number """
        # insert symptom
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name) VALUES (?)",
            ("Dizziness",)
        )
        self.db.conn.commit()

        # fetch the symptom id
        symptom_id = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = ?",
            ("Dizziness",)
        ).fetchone()["id"]

        # insert severity level for the symptom
        self.db.cur.execute(
            "INSERT INTO symptom_severity (symptom_id, severity_level) VALUES (?, ?)",
            (symptom_id, "5")
        )
        self.db.conn.commit()

        severity = self.db.get_severity_by_symptom("Dizziness")
        self.assertIsInstance(severity, str)
        self.assertEqual(severity, "5")


    ########### get_disease_symptom_matrix #############

    def test_get_disease_symptom_matrix_empty(self):
        """ Should return an empty DataFrame when there are no links"""
        df = self.db.get_disease_symptom_matrix()
        self.assertTrue(df.empty, "Expected an empty DataFrame for no data") 


    def test_get_disease_symptom_matrix_single(self):
        """ Should returna a single row DataFrame for one disease->symptom link """
        # seed disease and symptom
        self.db.cur.execute("INSERT INTO diseases (disease_name) VALUES (?)", ("A",))
        self.db.cur.execute("INSERT INTO symptoms (symptom_name) VALUES (?)", ("B",))
        self.db.conn.commit()

        # get the disease and symptom ids and link them

        disease_id = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = ?",
            ("A",)
        ).fetchone()["id"]      
        symptom_id = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = ?",
            ("B",)
        ).fetchone()["id"]
        self.db.cur.execute(
            "INSERT INTO symptom_disease (disease_id, symptom_id) VALUES (?, ?)",
            (disease_id, symptom_id)
        )
        self.db.conn.commit()

        # get the disease-symptom matrix
        df = self.db.get_disease_symptom_matrix()

        #correct columns

        self.assertListEqual(list(df.columns), ["disease", "symptom"])
        
        # one row matching A->B
        self.assertEqual(len(df), 1)
        self.assertEqual(df.loc[0]["disease"], "A")
        self.assertEqual(df.loc[0]["symptom"], "B")
    
    def test_get_disease_dedupiclate_and_sort(self):
        """ Duplicates should be removed and symptoms sorted alphabetically """

        # seed one disease and two symptoms

        self.db.cur.execute("INSERT INTO diseases (disease_name) VALUES (?)", ("D",))
        self.db.cur.executemany(
            "INSERT INTO symptoms (symptom_name) VALUES (?)",
            [("b",), ("a",)]
        )
        self.db.conn.commit()
        
        # get disease and symptom ids
        disease_id = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = ?",
            ("D",)
        ).fetchone()["id"]

        # get symptom ids
        symptom_ids = [r["id"] for r in self.db.cur.execute("SELECT id FROM symptoms")]

        # insert duplicate and both links

        for symptom_id in symptom_ids + [symptom_ids[0]]: # add duplicate  a,b,a
            self.db.cur.execute(
                "INSERT INTO symptom_disease (disease_id, symptom_id) VALUES (?, ?)",
                (disease_id, symptom_id)
            )
        self.db.conn.commit()

        # get the disease-symptom matrix
        df = self.db.get_disease_symptom_matrix()
        row = df.loc[0, "symptom"]

        # 'a b' exactly once, sorted 
        self.assertEqual(row, "a b")


#
# db HELPER FUNCTIONS FOR USERS
#   

    ########### add_user #############

    def test_add_user_success_and_defaults(self):
        """ Should rturn True and set default gender and role"""
        ok = self.db.add_user("Alice", "alice@example.com", "hashedpw")
        self.assertTrue(ok, "Expected add_user to return True on first insert")

        # verify the use exists with default gender and role
        row = self.db.get_user_by_email("alice@example.com")
        self.assertIsNotNone(row, "Expected to find the newly added user")
        self.assertEqual(row["name"], "Alice")
        self.assertEqual(row["email"], "alice@example.com")
        self.assertEqual(row["gender"], "Other")
        self.assertEqual(row["role"], "User")

    def test_add_user_duolicate_email(self):
        """ Should return False when adding a user with an existing email """
        first = self.db.add_user("John", "john@example.com", "pw1")
        self.assertTrue(first)
        second = self.db.add_user("John2", "john@example.com", "pw2")
        self.assertFalse(second, "Expected add_user to return False on duplicate email")

        # ensure only one record exists

        rows = self.db.get_all_users()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "John")

    def test_add_user_custom_gender_and_role(self):
        """ Should accept custom gender and role """

        ok = self.db.add_user("Bob", "bob@example.com", "pw", gender="Male", role="Admin")
        self.assertTrue(ok)

        row = self.db.get_user_by_email("bob@example.com")
        self.assertEqual(row["gender"], "Male")
        self.assertEqual(row["role"], "Admin")

    
    def test_add_user_invalid_parameters(self):
        """Should return False if required fields are invalid (e.g., None email)."""
        
        # name is None
        self.assertFalse(self.db.add_user(None, "d@example.com", "pw"))
        # email is None

        self.assertFalse(self.db.add_user("Dave", None, "pw"))
        # password is None

        self.assertFalse(self.db.add_user("Eve", "eve@example.com", None))

        # Database should remain empty
        self.assertEqual(self.db.get_all_users(), [])
    
    
    ########### get_user by_email #############
    
    def test_get_user_by_email_success(self):
        """ Should return None when no users are in the database"""
        self.assertIsNone(self.db.get_user_by_email("noone@example.com"))
    
    def test_get_user_by_email_success(self):
        """ Should return a sqlite3.Row with all expected fields for an existing user """
    
        # add a user
        added = self.db.add_user("Charlie", "charlie@example.com", "hashedpw")
        self.assertTrue(added, "Failed to insert user for lookup test")

        # get the user by email
        row = self.db.get_user_by_email("charlie@example.com")
        self.assertIsNotNone(row, "Expected get_user_by_email to return a row")

        # check core fields
        self.assertEqual(row["name"], "Charlie")
        self.assertEqual(row["email"], "charlie@example.com")
        self.assertEqual(row["password"], "hashedpw")

        # check default values                        
        self.assertEqual(row["gender"], "Other")
        self.assertEqual(row["role"], "User")

        # check all columns exist for schema integrity
        cols = row.keys()
        for col in ["id", "name", "email", "password", "gender", "role", "created_at"]:
            self.assertIn(col, cols)
    

    def test_get_user_by_email_nonexistent(self):
        """ Should return None when querying an email that wasn't inserted."""

        # insert a different user 
        self.db.add_user("Frank", "frank@example.com", "pw")
        self.assertIsNone(self.db.get_user_by_email("michael@example.com"))
    
    def test_get_user_by_email_invalid_type(self):

        """ Should return (rather than crashing) when passed a non-string (e.g. None)"""

        ### passing None into the parameterised query results in no match, not exception
        self.assertIsNone(self.db.get_user_by_email(None))
    
    
    ########### email_exists #############
    
    
    # do I end with:
    # if __name__ == '__main__':
    #     unittest.main()