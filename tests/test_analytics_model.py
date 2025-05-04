import unittest
from models.database import Database
from models.analytics import AnalyticsModel

class TestAnalyticsModel(unittest.TestCase):
    def setUp(self):
        # fresh in-memory database
        self.db = Database(dbname=":memory:")
        self.db.reset_schema()
        self.analytics_model = AnalyticsModel(self.db)

        # seed diseases
        self.db.cur.executemany(
            "INSERT INTO diseases (disease_name) VALUES (?)",
            [("DiseaseA",), ("DiseaseB",)]
        )
        # seed symptoms
        self.db.cur.executemany(
            "INSERT INTO symptoms (symptom_name) VALUES (?)",
            [("SymptomX",), ("SymptomY",)]
        )
        self.db.conn.commit()

        # link symptom_disease: DiseaseA→X, DiseaseA→Y, DiseaseB→X
        disease_a_row = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = ?", ("DiseaseA",)
        ).fetchone()
        disease_a_id = disease_a_row["id"]
        
        disease_b_row = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = ?", ("DiseaseB",)
        ).fetchone()
        disease_b_id = disease_b_row["id"]

        symptom_x_row = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = ?", ("SymptomX",)
        ).fetchone()
        symptom_x_id = symptom_x_row["id"]
        
        symptom_y_row = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = ?", ("SymptomY",)
        ).fetchone()
        symptom_y_id = symptom_y_row["id"]

        self.db.cur.executemany(
            "INSERT INTO symptom_disease (disease_id, symptom_id) VALUES (?, ?)",
            [
                (disease_a_id, symptom_x_id),
                (disease_a_id, symptom_y_id),
                (disease_b_id, symptom_x_id)
            ]
        )

        # seed severity: SymptomX→2, SymptomY→4
        self.db.cur.executemany(
            "INSERT INTO symptom_severity (symptom_id, severity_level) VALUES (?, ?)",
            [
                (symptom_x_id, "2"),
                (symptom_y_id, "4")
            ]
        )

        self.db.conn.commit()

    def test_get_most_common_diseases_default_limit(self):
        """ Should return diseases ordered by number of linked symptoms descending. """
        
        result_frame = self.analytics_model.get_most_common_diseases()
        expected = [
            {"Disease": "DiseaseA", "Symptom Count": 2},
            {"Disease": "DiseaseB", "Symptom Count": 1}
        ]
        self.assertEqual(result_frame.to_dict(orient="records"), expected)

    def test_get_most_common_symptoms_default_limit(self):
        """ Should return symptoms ordered by number of associated diseases descending. """
        
        result_frame = self.analytics_model.get_most_common_symptoms()
        expected = [
            {"Symptom": "SymptomX", "Disease Count": 2},
            {"Symptom": "SymptomY", "Disease Count": 1}
        ]
        self.assertEqual(result_frame.to_dict(orient="records"), expected)


    def test_get_symptom_frequency(self):
        """ Should return frequency of each symptom across diseases. """
        
        result_frame = self.analytics_model.get_symptom_frequency()
        expected = [
            {"Symptom": "SymptomX", "Frequency": 2},
            {"Symptom": "SymptomY", "Frequency": 1}
        ]
        self.assertEqual(result_frame.to_dict(orient="records"), expected)

    def test_get_symptom_severity_distribution(self):
        """ Should return distribution counts for each severity level. """
        
        result_frame = self.analytics_model.get_symptom_severity_distribution()
        expected = [
            {"Severity Level": "2", "Count": 1},
            {"Severity Level": "4", "Count": 1}
        ]
        self.assertEqual(result_frame.to_dict(orient="records"), expected)

    def test_get_symptom_disease_matrix(self):
        """ Should return a cross-tab matrix of diseases vs symptoms. """
        
        matrix = self.analytics_model.get_symptom_disease_matrix()
        
        # check index and columns
        self.assertListEqual(sorted(matrix.index.tolist()), ["DiseaseA", "DiseaseB"])
        self.assertListEqual(sorted(matrix.columns.tolist()), ["SymptomX", "SymptomY"])
        
        # check cell values
        self.assertEqual(matrix.loc["DiseaseA", "SymptomX"], 1)
        self.assertEqual(matrix.loc["DiseaseA", "SymptomY"], 1)
        self.assertEqual(matrix.loc["DiseaseB", "SymptomX"], 1)
        self.assertEqual(matrix.loc["DiseaseB", "SymptomY"], 0)

    def test_get_symptom_severity_mapping(self):
        """ Should return all symptoms with their corresponding severity levels in descending order. """
        
        result_frame = self.analytics_model.get_symptom_severity_mapping()
        expected = [
            {"Symptom": "SymptomY", "Severity Level": "4"},
            {"Symptom": "SymptomX", "Severity Level": "2"}
        ]
        self.assertEqual(result_frame.to_dict(orient="records"), expected)


if __name__ == "__main__":
    unittest.main()