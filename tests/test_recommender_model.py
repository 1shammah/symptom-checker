import unittest
from models.database import Database
from models.symptom import SymptomModel
from models.recommender import RecommenderModel

class TestRecommenderModel(unittest.TestCase):
    def setUp(self):
        """ Prepare a clean in-memory db and fit a recommender before each test """
        # Create an in-memory database for testing
        self.db = Database(":memory:")
        self.db.reset_schema()

        # seed one disease and two symptoms 
        self.db.cur.execute(
            "INSERT INTO diseases (disease_name) VALUES (?)", 
            ("Flu",)
        )
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name) VALUES (?)", 
            ("Fever",)
        )
        self.db.cur.execute(
            "INSERT INTO symptoms (symptom_name) VALUES (?)", 
            ("Cough",)
        )

        # link the disease to both symptoms in the symptom-disease table
        disease_id = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = ?", 
            ("Flu",)
        ).fetchone()["id"]
        fever_id = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = ?", 
            ("Fever",)
        ).fetchone()["id"]
        cough_id = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = ?", 
            ("Cough",)
        ).fetchone()["id"]

        self.db.cur.execute(
            "INSERT INTO symptom_disease (disease_id, symptom_id) VALUES (?, ?)", 
            (disease_id, fever_id)
        )
        self.db.cur.execute(
            "INSERT INTO symptom_disease (disease_id, symptom_id) VALUES (?, ?)", 
            (disease_id, cough_id)
        )
        self.db.conn.commit()

        # instantiate the models and train the recommender
        self.symptom_model = SymptomModel(self.db)
        self.recommender = RecommenderModel(self.db, self.symptom_model)
        self.recommender.fit()

    ############# fit() #############

    def test_fit_creates_vectorizer_and_matrix(self):
        """ Should create a TF-IDF vectorizer and a non-empty matrix after fit()"""
        
        self.assertIsNotNone(self.recommender.vectorizer)
        self.assertIsNotNone(self.recommender.tfidf_matrix)
        self.assertGreater(self.recommender.tfidf_matrix.shape[0], 0)

    def test_fit_loads_correct_disease_names(self):
        """Should load one disease name in the correct order."""
        
        self.assertEqual(self.recommender.disease_names, ["Flu"])

    ############# recommend() #############

    def test_recommend_basic_success(self):
        """Should return at least one recommendation and a float score."""
        
        recommendations = self.recommender.recommend(["Fever"])
        self.assertIsInstance(recommendations, list)
        self.assertGreaterEqual(len(recommendations), 1)
        disease_name, score = recommendations[0]
        self.assertEqual(disease_name, "Flu")
        self.assertIsInstance(score, float)

    def test_recommend_with_multiple_symptoms(self):
        """Should still recommend the same disease when given two matching symptoms."""
        
        recommendations = self.recommender.recommend(["Fever", "Cough"])
        disease_name, _ = recommendations[0]
        self.assertEqual(disease_name, "Flu")

    def test_recommend_empty_input(self):
        """Should return recommendations even if symptom list is empty."""
        
        recommendations = self.recommender.recommend([])
        self.assertIsInstance(recommendations, list)
        self.assertEqual(len(recommendations), 1)
        disease_name, _ = recommendations[0]
        self.assertEqual(disease_name, "Flu")

    def test_recommend_unknown_symptom(self):
        """Should handle unknown symptom by still scoring against known diseases."""
        recommendations = self.recommender.recommend(["AlienSymptom"])
        disease_name, _ = recommendations[0]
        self.assertEqual(disease_name, "Flu")

    def test_recommend_top_n_limit(self):
        """Should respect the top_n parameter when multiple diseases exist."""
        # add second disease linked only to 'Cough'
        self.db.cur.execute(
            "INSERT INTO diseases (disease_name) VALUES (?)",
            ("Cold",)
        )
        self.db.conn.commit()
        second_disease_id = self.db.cur.execute(
            "SELECT id FROM diseases WHERE disease_name = ?",
            ("Cold",)
        ).fetchone()["id"]
        cough_id = self.db.cur.execute(
            "SELECT id FROM symptoms WHERE symptom_name = ?",
            ("Cough",)
        ).fetchone()["id"]
        self.db.cur.execute(
            "INSERT INTO symptom_disease (disease_id, symptom_id) VALUES (?, ?)",
            (second_disease_id, cough_id)
        )
        self.db.conn.commit()

        # retrain and request top 2
        self.recommender.fit()
        recommendations = self.recommender.recommend(["Cough"], top_n=2)
        self.assertEqual(len(recommendations), 2)

    def test_recommend_raises_if_fit_not_called(self):
        """Should raise a RuntimeError if recommend() is called before fit()."""
        untrained = RecommenderModel(self.db, self.symptom_model)
        with self.assertRaises(RuntimeError):
            untrained.recommend(["Fever"])

    ############# invalid-input safety #############

    def test_recommend_invalid_input_type(self):
        """Should raise TypeError if selected_symptoms is not a list."""
        with self.assertRaises(TypeError):
            self.recommender.recommend(None)

if __name__ == "__main__":
    unittest.main()