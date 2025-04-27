# use unittest not pytest

import unittest
from models.database import Database
from models.symptom import SymptomModel, Symptom

class TestSymptomModel(unittest.TestCase):
    def setUp(self):
    # fresh in-memory DB and tables
        self.db = Database(dbname=":memory:")
        self.db.create_tables()
        self.model = SymptomModel(self.db)

    ############# get_all() #############

    def test_get_all_empty(self):
        """ Should return an empty list when no symptoms exist. """
        self.assertEqual(self.model.get_all(), [])

    def test_get_all_single_no_metadata(self):
        """ Should return one Symptom with name only, description and severity None. """
        
        # insert one symptom without description/severity
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name) VALUES (?)",
            ("Headache",)
        )
        self.db.conn.commit()

        all_symptoms = self.model.get_all()
        self.assertEqual(len(all_symptoms), 1)

        symptom = all_symptoms[0]
        self.assertIsInstance(symptom, Symptom)
        self.assertEqual(symptom.name, "Headache")
        self.assertIsNone(symptom.description)
        self.assertIsNone(symptom.severity)

    def test_get_all_multiple_and_order(self):
        """ Should return all Symptom objects in insertion (ID) order. """
        symptom_entries = [("A",), ("B",), ("C",)]
        self.db.cur.executemany(
            "INSERT INTO symptoms (symptom_name) VALUES (?)",
            symptom_entries
        )
        self.db.conn.commit()

        names = [s.name for s in self.model.get_all()]
        self.assertEqual(names, ["A", "B", "C"])

    
    ############# get_by_name() #############

    def test_get_by_name_not_found(self):
        """ Should return None when the symptom isn't in th db """
        self.assertIsNone(self.model.get_by_name("Nonexistent"))

    def test_get_by_name_partial_metadata(self):
        """
        Should return None if only description or only severity exists:
        both are required.
        """

        # seed symptom
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name, description) VALUES (?,?)",
            ("Fever", "High temperature")
        )
        self.db.conn.commit()
        
        # no severity inserted → fail
        self.assertIsNone(self.model.get_by_name("Fever"))

        # add severity but no description
        symptom_id = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = ?", ("Fever",)
        ).fetchone()["id"]
        
        # clear description, insert severity only
        self.db.cur.execute("UPDATE symptoms SET description = NULL WHERE id = ?", (symptom_id,))
        self.db.cur.execute(
            "INSERT INTO symptom_severity (symptom_id, severity_level) VALUES (?,?)",
            (symptom_id, "3")
        )
        self.db.conn.commit()
        
        self.assertIsNone(self.model.get_by_name("Fever"))

    def test_get_by_name_success(self):
        """ Should return a Symptom when both description and severity exist. """
       
        # seed both description and severity
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name, description) VALUES (?,?)",
            ("Cough", "Dry cough")
        )
        self.db.conn.commit()
        symptom_id = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = ?", ("Cough",)
        ).fetchone()["id"]
        self.db.cur.execute(
            "INSERT INTO symptom_severity (symptom_id, severity_level) VALUES (?,?)",
            (symptom_id, "2")
        )
        self.db.conn.commit()

        symptom = self.model.get_by_name("Cough")
        self.assertIsNotNone(symptom)
        self.assertEqual(symptom.name, "Cough")
        self.assertEqual(symptom.description, "Dry cough")
        self.assertEqual(symptom.severity, "2")

    ############# preprocess_symptoms() #############

    def test_preprocess_symptoms_basic(self):
        """
        Should:
          - lowercase all
          - replace spaces with underscores
          - remove duplicates
          - sort alphabetically
          - join with spaces
        """
        
        # insert some symptoms with spaces and duplicates
        raw = ["Head Ache", "head  ache", "Fever", "fever"]
        cleaned = self.model.preprocess_symptoms(raw)
        
        # duplicates removed and sorted: "fever head_ache"
        self.assertEqual(cleaned, "fever head_ache")

    def test_preprocess_symptoms_filters(self):
        """
        Should ignore empty strings, None, and non-str types.
        """

        # insert some symptoms with spaces and duplicates
        raw = ["  Cough  ", "", None, 123, "Sneezing"]
        cleaned = self.model.preprocess_symptoms(raw)
        
        # only valid strings with spaces replaced, lowercased & sorted
        self.assertEqual(cleaned, "cough sneezing")

    def test_preprocess_symptoms_empty_list(self):
        """ Should return an empty string when given no symptoms. """
        self.assertEqual(self.model.preprocess_symptoms([]), "")


if __name__ == "__main__":
    unittest.main()