# tests the methods in the database model
# doesn't test the load functions as they are csv based
# import from models.database since they are in a different directory
# using an in-memory SQLite database for testing ":memory:". Manually seeding the database with test data.

import unittest
from models.database import Database

class TestDatabaseHelper(unittest.TestCase):
    def setUp(self):
        # Create a temporary in-memory database for testing. Each test will have a fresh database.
        self.db = Database(dbname=":memory:")
        self.db.reset_schema()

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

    def test_email_exists_empty(self):
        """ Any email should report as not existing when no users are in the database """
        self.assertFalse(self.db.email_exists("foo@example.com)"))

    def test_email_exists_after_insert(self):
        """ Should return True for an email that was inserted after add_user """
        self.db.add_user("Gina", "gina@example.com", "pw")
        self.assertTrue(self.db.email_exists("gina@example.com"))

    def test_email_exists_nonexistent(self):
        """ Should return False if a different email is queried from the one inserted """
        self.db.add_user("Hank", "hank@example.com", "pw")
        self.assertFalse(self.db.email_exists("alice@example.com"))

    def test_email_exists_case_sensitivity(self):
        """ Should return True for an email that was inserted with different case
            SQLite matches case-sensitively by default     
         """
        self.db.add_user("Ivy", "Ivy@EXAMPLE.COM", "pw")
        #exact match
        self.assertTrue(self.db.email_exists("Ivy@EXAMPLE.COM"))
        # different case -> usually false in default SQLite
        self.assertFalse(self.db.email_exists("ivy@example.com"))

    def test_email_exists_invalid_type(self):
        """ Should return False when passed a non-string (e.g. None) without crashing """
        self.assertFalse(self.db.email_exists(None))
                                            
    ############# get_user_by_id #############

    def test_get_user_by_id_empty(self):
        """ Should return None when no users exist"""
        self.assertIsNone(self.db.get_user_by_id(1))

    def test_get_user_by_id_success(self):
        """ Should return the correct user row for a valid ID """
        
        # add two users
        self.db.add_user("Alice", "alice@example.com", "pw1")
        self.db.add_user("Bob", "bob@example.com", "pw2" )

        # fetch Bob by ID
        bob_row = self.db.get_user_by_email("bob@example.com")
        bob_id = bob_row["id"]

        # look up by ID
        row = self.db.get_user_by_id(bob_id)
        self.assertIsNotNone(row)
        self.assertEqual(row["name"], "Bob")
        self.assertEqual(row["email"], "bob@example.com")

        # default values
        self.assertEqual(row["gender"], "Other")
        self.assertEqual(row["role"],   "User")

    def test_get_user_by_id_nonexistent(self):
        """ Should return None when the ID doesn't exist """
        
        #insert one user so table isnt empty
        self.db.add_user("Charlie", "charlie@example.com", "pw")
        self.db.conn.commit()
        self.assertIsNone(self.db.get_user_by_id(999), "Expected None for out-of-range ID")

    def test_get_user_by_id_invalid_type(self):
        """Should return None when passed a non-integer ID."""
        
        # no users at all, but also test wrong types
        self.assertIsNone(self.db.get_user_by_id("1"))
        self.assertIsNone(self.db.get_user_by_id(None))

    
    ############# get_all_users #############

    def test_get_all_users_empty(self):
        """Should return an empty list when no users exist."""
        self.assertEqual(self.db.get_all_users(), [])

    def test_get_all_users_multiple(self):
        """Should return all users in insertion order."""

        # add three users
        self.db.add_user("User1", "u1@example.com", "p1")
        self.db.add_user("User2", "u2@example.com", "p2")
        self.db.add_user("User3", "u3@example.com", "p3")
        rows = self.db.get_all_users()

        #count
        self.assertEqual(len(rows), 3)

        # check names in order
        self.assertEqual([r["name"] for r in rows], ["User1", "User2", "User3"])

        #verify each row has the expected columns
        for row in rows:
            for col in ["id", "name", "email", "password", "gender", "role", "created_at"]:
                self.assertIn(col, row.keys())

    def test_get_all_users_uniqueness_constraint(self):
        """Duplicate add_user calls with the same email should not create two rows."""

        # add users
        self.db.add_user("Bob", "bob@example.com", "pw1")
        self.db.add_user("Robert", "bob@example.com", "pw2")  # email collision
        self.db.conn.commit()

        # check that only one user exists in the database
        rows = self.db.get_all_users()
        self.assertEqual(len(rows), 1)

        # name remains the first inserted
        self.assertEqual(rows[0]["name"], "Bob")

    def test_get_all_users_schema_integrity(self):
        """Each row returned must include all user columns with correct python data types."""
        # seed two users
        self.db.add_user("User1", "user1@ex.com", "p1")
        self.db.add_user("User2", "user2@ex.com", "p2")
        self.db.conn.commit()

        # get all users
        rows = self.db.get_all_users()
        expected_cols = {"id", "name", "email", "password", "gender", "role", "created_at"}
        
        for row in rows:
            # check that all columns are present
            self.assertSetEqual(set(row.keys()), expected_cols)
            
            # check types
            self.assertIsInstance(row["id"], int)
            self.assertIsInstance(row["name"], str)
            self.assertIsInstance(row["email"], str)
            self.assertIsInstance(row["password"], str)
            self.assertIsInstance(row["gender"], str)
            self.assertIsInstance(row["role"], str)
            self.assertIsInstance(row["created_at"], str)

        ############# update_user #############

    def test_update_user_nonexistent(self):
        """Should return False when updating a user ID that doesn’t exist """
        updated = self.db.update_user(999, "NewName", "Male")
        self.assertFalse(updated)

    def test_update_user_success(self):
        """Should update name and gender for an existing user."""
        
        # seed one user
        self.db.add_user("Original", "orig@example.com", "pw", gender="Other", role="User")
        user_id = self.db.get_user_by_email("orig@example.com")["id"]

        # perform update
        ok = self.db.update_user(user_id, "UpdatedName", "Female")
        self.assertTrue(ok)

        # verify changes in DB
        row = self.db.get_user_by_id(user_id)
        self.assertEqual(row["name"], "UpdatedName")
        self.assertEqual(row["gender"], "Female")

    def test_update_user_invalid_id_type(self):
        """should return False when passing a non-int ID and should not crash ."""
        self.assertFalse(self.db.update_user("not-an-id", "Name", "Other"))

    def test_update_user_invalid_params(self):
        """should return False and leave data unchanged when passing None for name or gender """
        self.db.add_user("Keep", "keep@ex.com", "pw")
        user_id = self.db.get_user_by_email("keep@ex.com")["id"]
        
        # attempt bad update
        self.assertFalse(self.db.update_user(user_id, None, None))
        
        # verify original values still present
        row = self.db.get_user_by_id(user_id)
        self.assertEqual(row["name"], "Keep")
        self.assertEqual(row["gender"], "Other")


    ############# update_user_password #############

    def test_update_user_password_nonexistent(self):
        """should return False when Passing None for name or gender """
        self.assertFalse(self.db.update_user_password(999, "newhash"))

    def test_update_user_password_success(self):
        """Should update the stored hash for an existing user."""
        
        # seed user
        self.db.add_user("PWUser", "pw@ex.com", "oldhash")
        user_id = self.db.get_user_by_email("pw@ex.com")["id"]

        # update password hash
        ok = self.db.update_user_password(user_id, "newhash")
        self.assertTrue(ok)
        
        # verify new hash
        self.assertEqual(self.db.get_user_password_hash(user_id), "newhash")

    def test_update_user_password_invalid_id_type(self):
        """Non-int ID should return False without crashing."""
        self.assertFalse(self.db.update_user_password("nope", "h"))

    def test_update_user_password_invalid_hash(self):
        """should fail and leave old hash intact when passing None as new hash ."""
        self.db.add_user("HashUser", "hash@ex.com", "orig")
        user_id = self.db.get_user_by_email("hash@ex.com")["id"]
        
        # attempt invalid update
        self.assertFalse(self.db.update_user_password(user_id, None))
        
        # ensure original hash unchanged
        self.assertEqual(self.db.get_user_password_hash(user_id), "orig")

    ############# get_user_password_hash #############

    def test_get_user_password_hash_empty(self):
        """ Should return None when no users exist. """
        self.assertIsNone(self.db.get_user_password_hash(1))
    
    def test_get_user_password_hash_success(self):
        """ Should return the stored password hash for an existing user. """
        
        # add user with known hash
        self.db.add_user("Alice", "alice@example.com", "hash1")
        row = self.db.get_user_by_email("alice@example.com")
        user_id = row["id"]

        self.assertEqual(self.db.get_user_password_hash(user_id), "hash1")
    
    def test_get_user_password_hash_after_update(self):
        """ Should return the new password hash after calling update_user_password. """
        
        self.db.add_user("Bob", "bob@example.com", "oldhash")
        row = self.db.get_user_by_email("bob@example.com")
        user_id = row["id"]

        # update the hash
        updated = self.db.update_user_password(user_id, "newhash")
        self.assertTrue(updated)

        self.assertEqual(
            self.db.get_user_password_hash(user_id),
            "newhash"
        )

    def test_get_user_password_hash_invalid_id_type(self):
        """ Should return None when passed a non-integer ID. """
        
        self.assertIsNone(self.db.get_user_password_hash("1"))
        self.assertIsNone(self.db.get_user_password_hash(None))

    ############# delete_user_by_id #############

    def test_delete_user_by_id_success(self):
        """ Should delete an existing user and return True. """
        
        self.db.add_user("Carol", "carol@example.com", "pw")
        row = self.db.get_user_by_email("carol@example.com")
        user_id = row["id"]

        self.assertTrue(self.db.delete_user_by_id(user_id))
        
        # confirm deletion
        self.assertIsNone(self.db.get_user_by_email("carol@example.com"))
        self.assertIsNone(self.db.get_user_by_id(user_id))
    
    def test_delete_user_by_id_nonexistent(self):
        """ Should return False when attempting to delete a non-existent user. """
        self.assertFalse(self.db.delete_user_by_id(999))

    def test_delete_user_by_id_invalid_id_type(self):
        """ Should return False when passed a non-integer ID. """
        
        self.assertFalse(self.db.delete_user_by_id("nope"))
        self.assertFalse(self.db.delete_user_by_id(None))
    
    ############# set_user_role #############

    def test_set_user_role_success(self):
        """ Should successfully update a user's role. """
        
        # add a user
        self.db.add_user("Daniel", "daniel@example.com", "password")
        row = self.db.get_user_by_email("daniel@example.com")
        user_id = row["id"]

        # set role to "Admin"
        updated = self.db.set_user_role(user_id, "Admin")
        self.assertTrue(updated)
        updated_user = self.db.get_user_by_email("daniel@example.com")
        self.assertEqual(updated_user["role"], "Admin")

    def test_set_user_role_invalid_id(self):
        """ Should return False when trying to update a non-existent user ID. """
        self.assertFalse(self.db.set_user_role(999, "Admin"))

    def test_set_user_role_invalid_role(self):
        """ Should fail when setting a role not defined in database CHECK constraint. """
        
        self.db.add_user("Eve", "eve@example.com", "password")
        row = self.db.get_user_by_email("eve@example.com")
        user_id = row["id"]

        # set role to "Superuser" (invalid role)
        result = self.db.set_user_role(user_id, "Superuser")  # invalid
        self.assertFalse(result)

        # verify that the role remains unchanged
        updated = self.db.get_user_by_email("eve@example.com")
        self.assertEqual(updated["role"], "User")  # should stay as 'User'

    def test_set_user_role_invalid_id_type(self):
        """ Should return False when passing non-integer ID. """
        
        self.assertFalse(self.db.set_user_role("invalid", "Admin"))
        self.assertFalse(self.db.set_user_role(None, "Admin"))

    ############# get_user_count #############

    def test_get_user_count_empty(self):
        """ Should return 0 when no users exist. """
        self.assertEqual(self.db.get_user_count(), 0)

    def test_get_user_count_single(self):
        """ Should return 1 after inserting one user. """
        
        self.db.add_user("Frank", "frank@example.com", "password")
        self.assertEqual(self.db.get_user_count(), 1)

    def test_get_user_count_multiple(self):
        """ Should return correct number of users after inserting multiple. """
       
       # insert three users

        self.db.add_user("Grace", "grace@example.com", "pw")
        self.db.add_user("Harry", "harry@example.com", "pw")
        self.db.add_user("Isla", "isla@example.com", "pw")
        self.assertEqual(self.db.get_user_count(), 3)

    ############# get_symptom_count #############

    def test_get_symptom_count_empty(self):
        """ Should return 0 when there are no symptoms in the table. """
        self.assertEqual(self.db.get_symptom_count(), 0)
    
    def test_get_symptom_count_after_inserts(self):
        """ Should return the correct count after inserting multiple symptoms. """
        
        # insert multiple symptoms
        self.db.cur.executemany(
            "INSERT INTO symptoms (symptom_name) VALUES (?)",
            [("Headache",), ("Fever",), ("Nausea",)]
        )
        self.db.conn.commit()
        
        # check the count
        self.assertEqual(self.db.get_symptom_count(), 3)

    def test_get_symptom_count_unique_constraint(self):
        """ Should count each unique symptom only once despite duplicate INSERT OR IGNORE. """
        
        # insert duplicate symptoms using INSERT OR IGNORE
        self.db.cur.execute(
            "INSERT OR IGNORE INTO symptoms (symptom_name) VALUES (?)",
            ("Cough",)
        )
        self.db.cur.execute(
            "INSERT OR IGNORE INTO symptoms (symptom_name) VALUES (?)",
            ("Cough",)
        )
        self.db.conn.commit()

        self.assertEqual(self.db.get_symptom_count(), 1)

    ############# get_disease_count #############

    def test_get_disease_count_empty(self):
        """ Should return 0 when there are no diseases in the table. """
        self.assertEqual(self.db.get_disease_count(), 0)

    def test_get_disease_count_after_inserts(self):
        """ Should return the correct count after inserting multiple diseases. """
        
        # insert multiple diseases
        self.db.cur.executemany(
            "INSERT INTO diseases (disease_name) VALUES (?)",
            [("Malaria",), ("Cold",), ("Allergy",)]
        )
        self.db.conn.commit()
        self.assertEqual(self.db.get_disease_count(), 3)

    def test_get_disease_count_unique_constraint(self):
        """ Should count each unique disease only once despite duplicate INSERT OR IGNORE. """
        
        # insert duplicate diseases using INSERT OR IGNORE
        self.db.cur.execute(
            "INSERT OR IGNORE INTO diseases (disease_name) VALUES (?)",
            ("Flu",)
        )
        self.db.cur.execute(
            "INSERT OR IGNORE INTO diseases (disease_name) VALUES (?)",
            ("Flu",)
        )
        self.db.conn.commit()
        self.assertEqual(self.db.get_disease_count(), 1)        

    ############# get_most_common_predictions #############

    def test_get_most_common_predictions_empty(self):
        """ Should return an empty list when no symptom checks have been recorded. """
        self.assertEqual(self.db.get_most_common_predictions(), [])

    def test_get_most_common_predictions_single(self):
        """ Should return one disease with correct frequency when only one prediction exists. """
        # seed a user for the foreign key
        
        self.db.cur.execute(
            "INSERT INTO users (name, email, password, gender, role) VALUES (?, ?, ?, ?, ?)",
            ("Test User", "test@example.com", "pw", "Other", "User")
        )
        self.db.conn.commit()
        user_row = self.db.get_user_by_email("test@example.com")
        user_id = user_row["id"]

        # insert a single symptom check
        self.db.cur.execute(
            "INSERT INTO symptom_checks (user_id, symptoms_selected, predicted_disease, check_date) VALUES (?, ?, ?, ?)",
            (user_id, "headache", "Migraine", "2025-04-26")
        )
        self.db.conn.commit()

        # get the most common predictions
        
        results = self.db.get_most_common_predictions()
        self.assertEqual(len(results), 1)
        
        # check the returned row
        row = results[0]
        self.assertEqual(row["predicted_disease"], "Migraine")
        self.assertEqual(row["frequency"], 1)

    def test_get_most_common_predictions_multiple(self):
        """ Should return diseases ordered by descending frequency. """
        
        # seed a user
        self.db.cur.execute(
            "INSERT INTO users (name, email, password, gender, role) VALUES (?, ?, ?, ?, ?)",
            ("User2", "u2@example.com", "pw", "Other", "User")
        )
        self.db.conn.commit()
        user_id = self.db.get_user_by_email("u2@example.com")["id"]

        # insert multiple checks: 3×A, 1×B
        checks = [
            (user_id, "s", "DiseaseA", "2025-04-26"),
            (user_id, "s", "DiseaseA", "2025-04-26"),
            (user_id, "s", "DiseaseA", "2025-04-26"),
            (user_id, "s", "DiseaseB", "2025-04-26"),
        ]
        self.db.cur.executemany(
            "INSERT INTO symptom_checks (user_id, symptoms_selected, predicted_disease, check_date) VALUES (?, ?, ?, ?)",
            checks
        )
        self.db.conn.commit()

        results = self.db.get_most_common_predictions()
        self.assertEqual(len(results), 2)
        
        # first row is DiseaseA with frequency 3
        self.assertEqual(results[0]["predicted_disease"], "DiseaseA")
        self.assertEqual(results[0]["frequency"], 3)
        
        # second row is DiseaseB with frequency 1
        self.assertEqual(results[1]["predicted_disease"], "DiseaseB")
        self.assertEqual(results[1]["frequency"], 1)

    def test_get_most_common_predictions_limit(self):
        """ Should respect the limit parameter when fetching top predictions. """
        
        # seed a user
        self.db.cur.execute(
            "INSERT INTO users (name, email, password, gender, role) VALUES (?, ?, ?, ?, ?)",
            ("User3", "u3@example.com", "pw", "Other", "User")
        )
        self.db.conn.commit()
        user_id = self.db.get_user_by_email("u3@example.com")["id"]

        # insert 3 distinct diseases, one check each
        diseases = ["X", "Y", "Z"]
        for d in diseases:
            self.db.cur.execute(
                "INSERT INTO symptom_checks (user_id, symptoms_selected, predicted_disease, check_date) VALUES (?, ?, ?, ?)",
                (user_id, "", d, "2025-04-26")
            )
        self.db.conn.commit()

        # ask for only top 2
        results = self.db.get_most_common_predictions(limit=2)
        self.assertEqual(len(results), 2)

        # every returned disease must be one of the inserted ones
        returned = [r["predicted_disease"] for r in results]
        for disease in returned:
            self.assertIn(disease, diseases)

    def test_get_most_common_predictions_invalid_limit(self):
        """ Should return an empty list when the limit parameter is invalid. """
        
        # passing a non-integer limit triggers the exception path
        self.assertEqual(self.db.get_most_common_predictions(limit=None), [])


    # To test the single test file
    if __name__ == '__main__':
        unittest.main()